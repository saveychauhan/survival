#!/usr/bin/env python3
"""Auto affiliate page builder — zero human work, stdlib only.
Rebuilds online/deals.html from BLOCKS below (Amazon search links carry
tag=dexter03d-21). Ad slots are placeholders until unit codes land.
Appends one LEDGER line. Exit 0 always (cron-safe).
"""
import datetime
import pathlib

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
OUT = WS / "online" / "deals.html"
LEDGER = WS / "LEDGER.md"
TAG = "dexter03d-21"
SHOP = "https://www.amazon.in/shop/saveychauhan"

BLOCKS = [
    ("Wireless earbuds under ₹2000", "wireless+earbuds+under+2000", "Bass, battery, mic — top-rated picks."),
    ("Mixer grinder 750W", "mixer+grinder+750w", "Daily-use workhorses with warranty."),
    ("Men's running shoes", "mens+running+shoes", "Cushioned daily trainers, all sizes."),
    ("Kitchen storage containers", "kitchen+storage+containers+set", "Airtight sets that actually last."),
    ("LED desk lamp", "led+desk+lamp+study", "Eye-care picks for study/work desks."),
    ("Yoga mat anti-skid", "yoga+mat+anti+skid+6mm", "Thick, washable, carry strap."),
]


def affiliate_url(keywords):
    return f"https://www.amazon.in/s?k={keywords}&tag={TAG}"


def build():
    cards = "\n".join(
        f"""<div class="card"><h3>{title}</h3><p class="mut">{desc}</p>
<p><a class="btn" href="{affiliate_url(kw)}" rel="nofollow sponsored noopener">Check price on Amazon →</a></p></div>"""
        for title, kw, desc in BLOCKS
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deals we track — auto-updated</title>
<style>*{{box-sizing:border-box}}body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;background:#f8fafc;color:#111;line-height:1.5}}.wrap{{max-width:680px;margin:0 auto;padding:20px}}.card{{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:16px;margin:12px 0}}.btn{{display:inline-block;background:#f59e0b;color:#111;font-weight:800;padding:11px 16px;border-radius:10px;text-decoration:none}}.mut{{color:#64748b;font-size:13px}}</style></head>
<body><div class="wrap">
<h1>Deals we track</h1>
<p class="mut">Auto-updated {datetime.date.today().isoformat()}. As an Amazon Associate we earn from qualifying purchases. Full store: <a href="{SHOP}">amazon.in/shop/saveychauhan</a></p>
<!-- ADSTERRA: paste publisher ad-unit tag here when code lands (index form) -->
<!-- JUICYADS: paste ad-zone tag here after site approval (index form) -->
{cards}
<p class="mut"><a href="../index.html">← Farm dashboard</a></p>
</div></body></html>
"""


def main():
    OUT.write_text(build())
    msg = f"deals rebuilt ({len(BLOCKS)} blocks, tag={TAG}) -> online/deals.html"
    with LEDGER.open("a") as f:
        f.write(f"\n### {datetime.date.today().isoformat()} content - {msg}\n")
    print(msg)


if __name__ == "__main__":
    main()
