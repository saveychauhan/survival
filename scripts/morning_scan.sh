#!/bin/bash
WS="/Users/saveychauhan/Documents/Dexter/survival"
D=$(date +%F); T=$(date +%F_%H%M)
mkdir -p "$WS/prompts" "$WS/logs"
cat > "$WS/prompts/scan_$T.md" <<EOF
# 9AM Scan $D - paste into opencode (free model)
1. Read SURVIVAL_SYSTEM.md + LEDGER.md Totals.
2. Find 5 new trades/salons (Maps, 4.0-4.4*, 20-200 revs, no WA CTA).
3. Score: misses/wk x avg_job x 0.25 = leak INR. Top 2 only.
4. Output: table name|phone|leak|first-line + 1 WA to send today.
5. Log 5 rows to LEDGER Leads + 1 Time row.
UPI: saveychauhan@ybl
EOF
echo "" >> "$WS/LEDGER.md"
echo "### $D 09:00 scan queued -> prompts/scan_$T.md" >> "$WS/LEDGER.md"
osascript -e 'display notification "9AM scan ready: open prompts/scan_TODAY.md" with title "Survival"' 2>/dev/null || true
