#!/usr/bin/env python3
import datetime, pathlib, subprocess
WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
L = WS/"LEDGER.md"; t = L.read_text()
D = datetime.date.today().isoformat()
def cnt(sec):
    s = t.split(sec)[1].split("##")[0] if sec in t else ""
    return max(0, len([l for l in s.splitlines() if l.strip().startswith("|")])-2)
le, co, pr = cnt("## Leads"), cnt("## Conversations"), cnt("## Proposals")
paid = t.count("| paid |")
rate = round(paid/max(1,le)*100,1) if le else 0
L.open("a").write(f"\n### {D} 21:00 check - leads:{le} conv:{co} prop:{pr} paid:{paid} close:{rate}% | TODO: log today rows + tomorrow next_dollar\n")
subprocess.run(["osascript","-e",'display notification "9PM: update LEDGER (2 min)" with title "Survival"'],capture_output=True)
