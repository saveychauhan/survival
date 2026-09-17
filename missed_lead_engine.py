import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).parent

DEFAULT_TEMPLATES = {
    "missed_call_textback": "Hi {name}, this is {business} — sorry we missed your call at {time}. Are you needing {service_hint}? Reply YES and I'll get you booked in the next 2 hrs. - {owner}",
    "second_nudge": "Hi {name}, {owner} from {business} again — holding a slot for you tomorrow. Want morning or afternoon? Reply 1 for AM, 2 for PM.",
    "review_request": "Hi {name}, thanks for choosing {business}! If we earned 5 stars, would you tap this link? {review_link} It takes 30 sec and helps us a lot. - {owner}",
    "after_hours": "Hi {name}, you reached {business} after hours ({time}). We open at {open_hours}. Reply with your issue + address and we'll prioritize you first thing. - {owner}"
}

PHONE_RE = re.compile(r"\D+")

def normalize_phone(p: str) -> str:
    digits = PHONE_RE.sub("", p or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits

def load_leads(csv_path: Path):
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k.strip(): (v or "").strip() for k, v in r.items()})
    return rows

def render(template: str, ctx: dict) -> str:
    out = template
    for k, v in ctx.items():
        out = out.replace("{" + k + "}", str(v))
    # remove any unfilled placeholders
    out = re.sub(r"\{[^}]+\}", "", out)
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out

def build_queue(leads, business="Sharma Plumbing Co.", owner="Savey", review_link="https://g.page/r/YOUR-LINK", open_hours="8am-7pm", avg_job_value=450.0, close_rate=0.25):
    queue = []
    now = datetime.now()
    for i, lead in enumerate(leads):
        name = lead.get("name") or "there"
        phone = normalize_phone(lead.get("phone", ""))
        time = lead.get("call_time") or now.strftime("%I:%M %p")
        service_hint = lead.get("service") or "help with your job"
        status = (lead.get("status") or "missed").lower()
        if not phone or len(phone) < 10:
            continue
        # choose template
        if "after" in status or "hour" in status:
            t = DEFAULT_TEMPLATES["after_hours"]
            send_at = now + timedelta(minutes=5)
            kind = "after_hours_textback"
        else:
            t = DEFAULT_TEMPLATES["missed_call_textback"]
            send_at = now + timedelta(minutes=5)
            kind = "missed_call_textback"
        ctx = {"name": name.split()[0], "business": business, "owner": owner, "time": time, "service_hint": service_hint, "review_link": review_link, "open_hours": open_hours}
        msg1 = render(t, ctx)
        msg2 = render(DEFAULT_TEMPLATES["second_nudge"], ctx)
        queue.append({
            "phone": phone,
            "name": name,
            "kind": kind,
            "send_at": send_at.strftime("%Y-%m-%d %H:%M"),
            "followup_at": (send_at + timedelta(hours=23)).strftime("%Y-%m-%d %H:%M"),
            "message_1": msg1,
            "message_2_nudge_if_no_reply": msg2,
            "service": service_hint,
            "chars_1": len(msg1),
            "segments_1": (len(msg1) // 160) + 1,
        })
    # ROI
    n = len(queue)
    expected_recovered = round(n * close_rate, 1)
    expected_revenue = round(expected_recovered * avg_job_value, 2)
    return queue, {"leads": n, "expected_recovered_jobs": expected_recovered, "expected_revenue": expected_revenue, "avg_job_value": avg_job_value, "close_rate": close_rate}

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Second-Chance Revenue Engine: missed-call textback generator")
    ap.add_argument("--in", dest="inp", default=str(BASE / "demo_leads.csv"))
    ap.add_argument("--out", dest="out", default=str(BASE / "outbox.json"))
    ap.add_argument("--out-csv", dest="outcsv", default=str(BASE / "outbox.csv"))
    ap.add_argument("--business", default="Sharma Plumbing Co.")
    ap.add_argument("--owner", default="Savey")
    ap.add_argument("--review-link", default="https://g.page/r/YOUR-LINK")
    ap.add_argument("--open-hours", default="8am-7pm")
    ap.add_argument("--avg-job-value", type=float, default=450.0)
    ap.add_argument("--close-rate", type=float, default=0.25)
    args = ap.parse_args()

    leads = load_leads(Path(args.inp))
    queue, roi = build_queue(leads, business=args.business, owner=args.owner, review_link=args.review_link, open_hours=args.open_hours, avg_job_value=args.avg_job_value, close_rate=args.close_rate)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"generated_at": datetime.now().isoformat(timespec="seconds"), "business": args.business, "roi": roi, "messages": queue}, f, indent=2)

    with open(args.outcsv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["phone", "name", "kind", "send_at", "followup_at", "message_1", "message_2_nudge_if_no_reply", "service"])
        w.writeheader()
        for q in queue:
            w.writerow({k: q[k] for k in w.fieldnames})

    print(f"Loaded {len(leads)} leads -> {len(queue)} sendable messages")
    print(f"Expected: {roi['expected_recovered_jobs']} recovered jobs = ${roi['expected_revenue']:,.2f} at ${roi['avg_job_value']}/job x {roi['close_rate']*100:.0f}% close")
    print(f"Wrote {args.out} and {args.outcsv}")
    for q in queue[:3]:
        print(f"- {q['phone']} @ {q['send_at']}: {q['message_1'][:110]}...")

if __name__ == "__main__":
    main()
