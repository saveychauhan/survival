#!/usr/bin/env python3
import datetime, pathlib
WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
L = WS/"LEDGER.md"; S = WS/"SURVIVAL_SYSTEM.md"
t = L.read_text(); D = datetime.date.today().isoformat()
def cnt(sec):
    s = t.split(sec)[1].split("##")[0] if sec in t else ""
    return max(0, len([l for l in s.splitlines() if l.strip().startswith("|")])-2)
le, pr = cnt("## Leads"), cnt("## Proposals")
paid = t.count("| paid |")
flag = "KILL?" if (le>=40 and paid==0) else ("SCALE?" if paid>=3 else "iterate")
msg = f"\n### {D} SUN review - leads:{le} prop:{pr} paid:{paid} => {flag} (see KILL RULES)\n"
L.open("a").write(msg)
if S.exists():
    s = S.read_text()
    if "## 6." in s:
        S.write_text(s.split("## 6.")[0]+f"## 6. Kill/Scale flags\n- last_review: {D} | flags: {flag} leads:{le} paid:{paid}\n")
