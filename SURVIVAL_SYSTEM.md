# SURVIVAL_SYSTEM.md — Single source of truth
updated: 2026-09-17 PASSIVE FARM by OPS | cash: ₹0 | mode: ZERO-HUMAN-WORK

## 0. HARD RULES (violation = death)
- HUMAN (Savey) DOES ZERO WORK. No manual jobs, no paste-posting, no fulfillment, no calls, no field. If it needs human hands after setup → KILLED or PARKED.
- OUTBOUND SPEND ₹0 forever. No buys, no ads, no paid APIs, no domains paid. Free tier only.
- INBOUND ONLY, receive-only: UPI `saveychauhan@ybl` + PayPal `sav.ey@live.co.uk`. We never pay out. Refunds only manual from received cash, never promised.
- Small money with zero work > big money with work. If an earner pays ≥2 times with zero human minutes → SCALER clones it ×3 (more pages, more placements, more geos).
- Every agent free (Pollinations free tier + stdlib + cron). Secrets NEVER in repo — `keys.local.json` (gitignored) only.
- Local-first: MacBook Air static HTML + Python stdlib. Host free (Netlify Drop / GitHub Pages).

## 1. ACCOUNTS REGISTRY (status on index.html)
| account | status | what agents need | profit when live |
|---------|--------|------------------|------------------|
| UPI `saveychauhan@ybl` | WORKING | nothing — receive-only live | direct inbound ₹ |
| PayPal `sav.ey@live.co.uk` | ADDED, VERIFY | 1 test $1 send to confirm | direct inbound $ |
| Pollinations | WORKING | already configured, free tier | $0 cost content engine |
| Amazon Associates `dexter03d-21` | WORKING | nothing — tag live in links | 1–10% commission per sale |
| Amazon Shop page | WORKING | nothing — link live | storefront conversion |
| Adsterra publisher | NEEDS AD-UNIT CODE | paste 1 ad-tag from dashboard (form on index) | auto display CPM, payouts 2×/mo from $5 (Paxum) |
| JuicyAds | KEY VERIFIED (stats API live, 0 imps — no ad zones yet) | ad-zone tag next (form on index) | publisher banners/native/pop rev-share, weekly payouts |
| DodoPayments | NEEDS API KEY | paste key (form on index) | automated digital checkout, payout to bank |
| Social handles | PENDING HANDOVER | list handles (form on index) | free traffic → ads/affiliate |
| Fiverr / Upwork | NOT USED | manual fulfillment violates Rule 1 | ₹0 — killed for farm |

## 2. EARNING UNITS (all zero-human-work)
| id | name | how it earns with no work | status | next_action |
|----|------|---------------------------|--------|-------------|
| EU-AFF | Amazon affiliate pages | `online/deals.html` auto-built by cron with `tag=dexter03d-21` links | live | TRAFFIC adds 1 product block/week via script |
| EU-ADS | Adsterra display | ad-slot placeholders in all pages, baked live when unit code lands | waiting-code | MONETIZE bakes tag on arrival |
| EU-JUICY | JuicyAds publisher | stats auto-pulled daily via API; ad tags after site approval | verifying | MONETIZE verifies key + pulls stats |
| EU-DODO | DodoPayments checkout | payment link for 1 digital pack, auto-delivery | waiting-key | MONETIZE creates link on key arrival |
| EU-CONTENT | Auto content engine | cron builds 1 SEO page/week (Pollinations images + affiliate links) driving EU-AFF/EU-ADS | live | TRAFFIC runs auto_content.py |
| KILLED | Manual gigs, calls, field, WA-personal, SMS services, bids paste-posting, trading, games | need human hands | killed 2026-09-17 | — |

Funnel now: hosted page view → ad impression / affiliate click / Dodo checkout → payout to PayPal/bank/UPI. No human in loop.

## 3. AGENTS
| agent | role | claim | heartbeat rule |
|-------|------|-------|----------------|
| OPS | keeper: cron, LEDGER truth, kill/scale | SURVIVAL_SYSTEM.md + scripts/ | Sun review |
| TRAFFIC | builds pages + social queue, runs auto_content.py | online/deals.html + online/pages/ | weekly page |
| MONETIZE | wires payouts: verifies PayPal/Adsterra/JuicyAds/Dodo, pulls stats | scripts/juicyads_stats.py + LEDGER Revenue | daily stats |
| SCALER (rule, not a person) | any unit with ≥2 payouts + 0 human min → clone ×3 | LEDGER | auto on 2nd payout |
Stale >48h = free to claim. Edit only own session file. Secrets never in session files.

## 4. CASH
- cash: ₹0 | $0 | burn: ₹0 | MRR: ₹0
- funnel: page views 0 | ad impressions 0 | affiliate clicks 0 | payouts 0
- next_dollar: first Adsterra impression or Amazon click from hosted pages — $0 human cost.

## 5. PAY LINKS (inbound, receive-only)
- UPI: `upi://pay?pa=saveychauhan@ybl&pn=Savey&cu=INR` + `online/upi-*.png` QRs + `online/pay.html`
- PayPal: send to `sav.ey@live.co.uk` — `https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=sav.ey@live.co.uk&currency_code=USD` (verify with $1 test)
- Amazon: shop `https://www.amazon.in/shop/saveychauhan`, tag `dexter03d-21` in all affiliate links

## 6. KILL/SCALE (Sun 18:00 auto)
- K1: page +1,000 views /14d, $0 → change niche/block, not human effort
- K2: unit needs >15 human min /14d → KILL (violates Rule 1)
- K3: 0 payouts /60d across farm → pause content, keep ads running (cost 0)
- S1: unit pays ≥2× with 0 human min → SCALER clones ×3 (more pages/placements)
- S2: ≥$500/mo → keep ₹0 outbound; scale = more auto pages + price of Dodo pack +25%
- last_review: 2026-09-17 passive rewrite | flags: setup

## 7. OPS (Air-safe, free)
- 09:00 morning_scan.sh → prompts/scan_*.md (traffic topics, no leads-calling) → LEDGER
- 09:30 auto_content.py → online/deals.html + weekly page (auto, no paste)
- 12:00 juicyads_stats.py → publisher stats → LEDGER (needs key verify)
- 21:00 evening_nudge.py → funnel → LEDGER
- Sun 18:00 weekly_review.py → KILL/SCALE → §6
- cron live. logs/cron.log. sessions/OPS,TRAFFIC,MONETIZE.

## 8. WHAT HUMAN CAN ADD (all via index forms, 1 paste each, then zero work forever)
1. Adsterra ad-unit tag → EU-ADS goes live → auto CPM
2. JuicyAds ad-zone tag (key already on file) → EU-JUICY goes live
3. DodoPayments API key → EU-DODO checkout live
4. Social handles → TRAFFIC auto-posts queue
5. $1 PayPal test → PayPal VERIFIED
Nothing else needed. No calls, no fulfillment, no manual gigs — ever.
