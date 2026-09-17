#!/bin/bash
WS="/Users/saveychauhan/Documents/Dexter/survival"
D=$(date +%F); T=$(date +%F_%H%M)
mkdir -p "$WS/prompts" "$WS/logs"
cat > "$WS/prompts/scan_$T.md" <<EOF
# 9AM Scan $D - paste into opencode (free model)
1. Read SURVIVAL_SYSTEM.md + LEDGER.md Totals.
2. Pick 1 traffic niche (zero-work): check deals.html clicks/views, find 1 product block to add/swap.
3. Score: search demand x affiliate commission x 0 effort = rank. Top 1 only.
4. Output: 1 product block (title|keywords|blurb) for auto_content.py BLOCKS.
5. Log 1 row to LEDGER + 1 Time row (agent minutes only, human 0).
UPI: saveychauhan@ybl
EOF
echo "" >> "$WS/LEDGER.md"
echo "### $D 09:00 scan queued -> prompts/scan_$T.md" >> "$WS/LEDGER.md"
osascript -e 'display notification "9AM scan ready: open prompts/scan_TODAY.md" with title "Survival"' 2>/dev/null || true
