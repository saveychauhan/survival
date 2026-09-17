#!/usr/bin/env python3
"""PARKED 2026-09-17 — paste-posting needs human hands. Violates zero-work rule."""
import datetime, pathlib
WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
OUT = WS/"scripts"/"bid_drafts"
OUT.mkdir(parents=True, exist_ok=True)
D = datetime.date.today().isoformat()
UPI = "saveychauhan@ybl"
drafts = f"""# Bid drafts {D} — paste manually, DO NOT bot-post (ban risk)
UPI: {UPI} | Reply <12h inbox-only | No phone

## 1. Catalog BG-remove (Meesho/Amazon seller, Upwork search: background removal)
> Hi, I clean 15 product photos to white-bg + 2-page catalog PDF in 24h for Rs499 UPI. 3 free samples in 6h — pay only if you like. Remark: BG-[username]-[count] to {UPI}. Pay: online/pay.html. Send Drive link + UTR here?

## 2. GBP Fix (Upwork: GBP optimization, $10-40 bands)
> Your Maps misses top-3 (photos/Q&A). I fix categories + 750-char description + 3 posts + review QR PDF in 48h Rs1499 UPI {UPI}. Remark: GBP-[biz]-[email]. Confirm <12h here. Free 1-page audit first?

---
Paste 2/day each = 4 touches/day. Log views/inbox/UPI in LEDGER.md. Kill if 100 views 0 inbox /14d.
"""
(OUT/f"{D}.md").write_text(drafts)
# append ledger nudge
L = WS/"LEDGER.md"
L.open("a").write(f"\n### {D} bids generated -> scripts/bid_drafts/{D}.md (paste 6, no bot)\n")
print(f"wrote scripts/bid_drafts/{D}.md")
