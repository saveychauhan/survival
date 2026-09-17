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
SHOP = "https://www.amazon.in/?linkCode=ll2&tag=dexter03d-21&linkId=1ad1fede02a40f57a74f102f0a24e3c1&ref_=as_li_ss_tl"

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
        f"""<div class="card"><h3>{title}</h3><p>{desc}</p>
<p><a class="btn-primary" href="{affiliate_url(kw)}" rel="nofollow sponsored noopener">Check price on Amazon</a></p></div>"""
        for title, kw, desc in blocks
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deals we track — Raycast</title>
<meta name="description" content="Raycast tracks Amazon deals. As an Amazon Associate we earn from qualifying purchases.">
<link rel="stylesheet" href="../morrow.css"></head>
<body>
<header class="site-header"><div class="nav-inner"><div class="brand-group"><a class="brand-title" href="../index.html">raycast</a></div><nav class="site-nav"><a href="games/index.html">Arcade</a><a href="deals.html">Deals</a><a href="affiliates.html">Affiliates</a><a href="pay.html">Pay</a></nav></div></header>
<div class="container">
<section class="hero"><div class="hero-tag">Tracked daily &middot; No hype just prices</div><h1 class="hero-heading">Deals we track</h1>
<p class="hero-sub">Run by the Raycast agent farm. Auto-updated {datetime.date.today().isoformat()}. As an Amazon Associate we earn from qualifying purchases. Full store: <a data-amz href="{SHOP}">Amazon shop</a> · <a href="affiliates.html">how affiliates fund the hamster</a></p></section>
<div class="adbox"><!-- ADSTERRA native live 2026-09-17 -->
<script async="async" data-cfasync="false" src="https://pl31381240.profitableratecpmnetwork.com/9e768ff94aeda27c1956ea7de2623983/invoke.js"></script>
<div id="container-9e768ff94aeda27c1956ea7de2623983"></div>
<!-- JUICYADS: paste ad-zone tag here after site approval (index form) --></div>
<div class="grid">
{cards}
</div>
<div><p><a class="btn-secondary" href="https://twitter.com/intent/tweet?text=Deals%20tracked%20daily%20%E2%80%94%20no%20hype%20just%20prices&url=https%3A%2F%2Fraycast.in%2Fonline%2Fdeals.html">Share on X</a> <a class="btn-secondary" href="https://wa.me/?text=Deals%20tracked%20daily%20https%3A%2F%2Fraycast.in%2Fonline%2Fdeals.html">WhatsApp</a></p>
<section class="section"><div class="section-label">How tracking works</div><h2 class="section-title">No hype, just prices.</h2><div class="grid2"><div class="card"><h3>Live Amazon results</h3><p>Every pick opens current Amazon search results — prices, ratings and availability are always live, never screenshots.</p></div><div class="card"><h3>Everyday categories</h3><p>Earbuds, mixers, shoes, storage, lamps and yoga gear: things people actually buy, refreshed by an automated weekly check.</p></div></div></section>
<section class="section"><div class="section-label">Good to know</div><h2 class="section-title">Deal questions.</h2><details class="faq-item" open><summary><span>Are prices guaranteed?</span><span>+</span></summary><p>No — Amazon prices change constantly. Always check the live price on Amazon before buying.</p></details><details class="faq-item"><summary><span>Do you earn from my purchase?</span><span>+</span></summary><p>As an Amazon Associate we earn from qualifying purchases, at no extra cost to you. That is what funds the farm.</p></details><details class="faq-item"><summary><span>Why search links instead of single products?</span><span>+</span></summary><p>Single products go out of stock or get replaced. Search links always show what's available right now.</p></details></section>
<footer class="site-footer"><div>© 2026 Raycast<br>As an Amazon Associate we earn from qualifying purchases.</div><nav><a href="../index.html">Home</a><a href="games/index.html">Arcade</a><a href="deals.html">Deals</a><a href="affiliates.html">Affiliates</a><a href="pay.html">Pay</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="cookies.html">Cookies</a></nav></footer></div>
</div><script src="../amz.js"></script></body></html>
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
