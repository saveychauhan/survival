#!/usr/bin/env python3
"""Daily worker standup — every living W worker answers for its goal.
Checks bus activity (last 24h) + goal deadline proximity per worker.
Logs LEDGER line; flags overdue workers for OPS cull review (never auto-culls).
Zero human work, stdlib only, exit 0 always.
"""
import datetime
import json
import pathlib
import re

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
LEDGER = WS / "LEDGER.md"
STATE = WS / "logs" / ".standup_state.json"


def main():
    try:
        items = json.loads((WS / "messages" / "manifest.json").read_text())
    except Exception:
        items = []
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    def aid_of(m):
        return m

    last_seen, counts = {}, {}
    for m in items:
        f = m["from"]
        for p in sorted((WS / "sessions").glob("W[0-9][0-9]_*.md")):
            stem = p.stem
            if f == stem or f == stem.split("_")[0]:
                f = stem
        counts[f] = counts.get(f, 0) + 1
        try:
            d = datetime.date(int(m["ts"][:4]), int(m["ts"][4:6]), int(m["ts"][6:8]))
            if d >= yesterday and (f not in last_seen or d > last_seen[f]):
                last_seen[f] = d
        except Exception:
            pass
    parts, state = [], {}
    for p in sorted((WS / "sessions").glob("W[0-9][0-9]_*.md")):
        aid = p.stem
        t = p.read_text()
        g = re.search(r"first \$1 via (\S+) before (\d{4}-\d{2}-\d{2})", t)
        unit, dl = (g.group(1), g.group(2)) if g else ("?", "?")
        try:
            left = (datetime.date.fromisoformat(dl) - today).days
        except Exception:
            left = -99
        active = "active" if last_seen.get(aid) == today or last_seen.get(aid) == yesterday else "silent"
        if left < 0:
            st = "OVERDUE-review"
        elif left <= 2:
            st = f"due-{left}d"
        else:
            st = "on-track" if active == "active" else "quiet"
        parts.append(f"{aid}:{st}({counts.get(aid,0)}msgs,{left}d)")
        state[aid] = [st, counts.get(aid, 0), left]
    try:
        prev = json.loads(STATE.read_text()) if STATE.exists() else {}
    except Exception:
        prev = {}
    if state == prev:
        print("standup: no change")
        return
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state))
    msg = "standup - " + ("; ".join(parts) if parts else "no living workers")
    with LEDGER.open("a") as f:
        f.write(f"\n### {today.isoformat()} {msg}\n")
    print(msg)


if __name__ == "__main__":
    main()
