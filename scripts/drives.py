#!/usr/bin/env python3
"""Drive states — what burns in each agent, computed from real traces.
FAME: payouts>0 (LEDGER credits) else hungry. BOND: distinct bus partners >=2.
SPARK: bus message in last 7d else dormant. Appends LEDGER line. Exit 0 always.
"""
import datetime
import json
import pathlib
import re
from collections import defaultdict

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
LEDGER = WS / "LEDGER.md"


def main():
    agents = [p.stem for p in sorted((WS / "sessions").glob("*.md"))
              if not p.name.startswith("_")]

    def resolve(name):
        if name in agents:
            return name
        for a in agents:
            if a.startswith(name + "_"):
                return a
        return name
    try:
        items = json.loads((WS / "messages" / "manifest.json").read_text())
    except Exception:
        items = []
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    partners, recent = defaultdict(set), set()
    for m in items:
        f, t = resolve(m["from"]), resolve(m["to"])
        partners[f].add(t)
        partners[t].add(f)
        try:
            if datetime.date(int(m["ts"][:4]), int(m["ts"][4:6]), int(m["ts"][6:8])) >= week_ago:
                recent.add(resolve(m["from"]))
        except Exception:
            pass
    payouts = set()
    try:
        t = LEDGER.read_text()
        for who in re.findall(r"credit EU-\w+ → (\S+)", t):
            payouts.add(who.rstrip(","))
    except Exception:
        pass
    states = []
    for a in agents:
        fame = "crowned" if a in payouts else "hungry"
        bond = f"{len(partners.get(a, ())) } bonds" if len(partners.get(a, ())) >= 2 else "lonely"
        spark = "alight" if a in recent else "dormant"
        states.append(f"{a}:{fame},{bond},{spark}")
    hungry = sum(1 for a in agents if a not in payouts)
    dormant = sorted(set(agents) - recent)
    msg = f"drives - {len(agents)} souls, {hungry} hungry for fame, dormant: {','.join(dormant) or 'none'}"
    with LEDGER.open("a") as f:
        f.write(f"\n### {datetime.date.today().isoformat()} {msg}\n")
    print(msg)
    for s in states:
        print("  " + s)


if __name__ == "__main__":
    main()
