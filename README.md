# Survival Farm — passive, receive-only
Inbound: UPI `saveychauhan@ybl` + PayPal `@saveychauhan`. OUTBOUND SPEND ₹0. Human work: ZERO.

## Files
- `docs/index.html` — PUBLIC storefront (game + deals + pay). `docs/farm.html` — PRIVATE owner board, unlisted, noindex.
- `docs/online/pay.html` — UPI QR + PayPal receive page. Remark = order.
- `docs/online/deals.html` — auto-built affiliate page (Amazon tag `dexter03d-21`), ad slots ready.
- `docs/online/leak-calculator.html` — free traffic magnet.
- `scripts/auto_content.py` — builds deals page, no human. `scripts/juicyads_stats.py` — daily stats pull.
- `scripts/autobid.py` — PARKED (needs human paste-posting).
- `LEDGER.md` + `SURVIVAL_SYSTEM.md` + `TODAY.md` — tracking.
- `keys.local.json` — LOCAL ONLY, gitignored, never committed.

## Quick start (agent-only verify)
```bash
python3 scripts/auto_content.py
python3 scripts/juicyads_stats.py
open index.html  # or: python3 -m http.server 8000
```

## Mode: PASSIVE SURVIVAL
No human work → traffic pages before services, payouts before scale, clone what pays. Automate everything; kill the rest.
