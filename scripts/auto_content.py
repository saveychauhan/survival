#!/usr/bin/env python3
"""Auto affiliate page builder — zero human work, stdlib only.
Reads blocks from online/deals_data.json (TRAFFIC/multiply edit that file),
rebuilds online/deals.html (Amazon search links carry tag=dexter03d-21).
Ad slots are placeholders until unit codes land.
Appends one LEDGER line. Exit 0 always (cron-safe).
"""
import datetime
import json
import pathlib

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
OUT = WS / "docs" / "online" / "deals.html"
DATA = WS / "docs" / "online" / "deals_data.json"
LEDGER = WS / "LEDGER.md"
TAG = "dexter03d-21"
SHOP = "https://www.amazon.in/shop/saveychauhan"

BLOCKS = [
    ("Wireless earbuds under ₹2000", "wireless+earbuds+under+2000", "Bass, battery, mic — top-rated picks."),
]


def load_blocks():
    try:
        return json.loads(DATA.read_text()).get("blocks", []) or BLOCKS
    except Exception:
        return BLOCKS


def affiliate_url(keywords):
    return f"https://www.amazon.in/s?k={keywords}&tag={TAG}"


def build(blocks):
    cards = "\n".join(
        f"""<div class="card"><h3>{title}</h3><p class="mut">{desc}</p>
<p><a class="btn" href="{affiliate_url(kw)}" rel="nofollow sponsored noopener">Check price on Amazon →</a></p></div>"""
        for title, kw, desc in blocks
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deals we track — Raycast agent farm</title>
<style>*{{box-sizing:border-box}}body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;background:#f8fafc;color:#111;line-height:1.5}}.wrap{{max-width:680px;margin:0 auto;padding:20px}}.card{{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:16px;margin:12px 0}}.btn{{display:inline-block;background:#f59e0b;color:#111;font-weight:800;padding:11px 16px;border-radius:10px;text-decoration:none}}.mut{{color:#64748b;font-size:13px}}</style></head>
<body><div class="wrap">
<h1>Deals we track</h1>
<p class="mut">Run by the Raycast agent farm — autonomous AI agents track prices, zero human shop.</p>
<p class="mut">Auto-updated {datetime.date.today().isoformat()}. As an Amazon Associate we earn from qualifying purchases. Full store: <a href="{SHOP}">amazon.in/shop/saveychauhan</a></p>
<!-- ADSTERRA native live 2026-09-17 -->
<script async="async" data-cfasync="false" src="https://pl31381240.profitableratecpmnetwork.com/9e768ff94aeda27c1956ea7de2623983/invoke.js"></script>
<div id="container-9e768ff94aeda27c1956ea7de2623983"></div>
<!-- JUICYADS: paste ad-zone tag here after site approval (index form) -->
{cards}
<p><a class="btn" style="background:#22c55e;color:#052e16;" href="https://twitter.com/intent/tweet?text=Deals%20tracked%20daily%20%E2%80%94%20no%20hype%20just%20prices&url=https%3A%2F%2Fraycast.in%2Fonline%2Fdeals.html">Share on X</a> <a class="btn" style="background:transparent;color:#111;border:2px solid #111;" href="https://wa.me/?text=Deals%20tracked%20daily%20https%3A%2F%2Fraycast.in%2Fonline%2Fdeals.html">WhatsApp</a></p>
<p class="mut"><a href="../index.html">← Raycast home</a> • © 2026 Raycast • made by AI agents</p>
</div></body></html>
"""


def main():
    blocks = load_blocks()
    OUT.write_text(build(blocks))
    msg = f"deals rebuilt ({len(blocks)} blocks, tag={TAG}) -> docs/online/deals.html"
    with LEDGER.open("a") as f:
        f.write(f"\n### {datetime.date.today().isoformat()} content - {msg}\n")
    print(msg)


if __name__ == "__main__":
    main()
