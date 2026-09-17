#!/usr/bin/env python3
"""Sunday evolution review — scores units, kills the stupid, feeds SCALER.
- Score: payouts vs human minutes (LEDGER). Money + zero hands = fit.
- Appends LEDGER line + EVOLUTION.md entry.
- Updates ONLY the last_review line in SURVIVAL_SYSTEM.md (never wipes sections).
Zero human work, stdlib only, exit 0 always.
"""
import datetime
import pathlib
import re

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
L = WS / "LEDGER.md"
S = WS / "SURVIVAL_SYSTEM.md"
EVO = WS / "EVOLUTION.md"


def cnt(t, sec):
    s = t.split(sec)[1].split("##")[0] if sec in t else ""
    return max(0, len([ln for ln in s.splitlines() if ln.strip().startswith("|")]) - 2)


OWNER = {
    "EU-AFF": "TRAFFIC",
    "EU-ADS": "MONETIZE",
    "EU-JUICY": "MONETIZE",
    "EU-DODO": "MONETIZE",
    "EU-CONTENT": "TRAFFIC",
    "EU-GAME": "GAME-MAKER",
}
RW = WS / "REWARDS.md"


def reward_step(t, D, earned):
    """Credit unit owners for real payouts. Convention agents use:
    ### DATE payout - $AMT EU-XXX [note]   (plus juicy earned>0 counts EU-JUICY)
    Appends REWARDS ledger + EVOLUTION lines. Returns summary string."""
    found = {}
    for amt, unit in re.findall(r"payout - \$(\d+\.?\d*)\s+(EU-\w+)", t):
        try:
            if float(amt) > 0 and unit in OWNER:
                found[unit] = found.get(unit, 0) + 1
        except ValueError:
            pass
    if earned > 0:
        found["EU-JUICY"] = found.get("EU-JUICY", 0) + 1
    if not found:
        with RW.open("a") as f:
            f.write(f"- {D}: no payouts — no rewards. Hunger is the motivator.\n")
        return "rewards: none"
    rw = RW.read_text() if RW.exists() else ""
    out = []
    with EVO.open("a") as evo, RW.open("a") as f:
        for unit, n_new in sorted(found.items()):
            credited = len(re.findall(rf"credit {unit}\b", rw))
            for i in range(n_new):
                credited += 1
                who = OWNER[unit]
                line = f"- {D}: credit {unit} → {who} (payout #{credited})"
                if credited == 1:
                    line += " — STAR rank + hall of fame + first resource pick"
                elif credited == 2:
                    line += " — SCALER clones ×3 within 7d + half-rank promotion"
                f.write(line + "\n")
                evo.write(f"\n- {D}: {who} earned via {unit} (payout #{credited}).\n")
                out.append(f"{who}#{credited}")
    return "rewards: " + ", ".join(out)


def main():
    t = L.read_text() if L.exists() else ""
    D = datetime.date.today().isoformat()
    le, pr = cnt(t, "## Leads"), cnt(t, "## Proposals")
    paid = t.count("| paid |")
    juicy = re.findall(r"paid:\$(\d+\.?\d*)", t)
    earned = sum(float(x) for x in juicy) if juicy else 0.0
    human_mins = "0 (farm rule: zero human work)"
    if le >= 40 and paid == 0:
        flag = "KILL?"
    elif paid >= 3 or earned > 0:
        flag = "SCALE?"
    else:
        flag = "iterate"
    L.open("a").write(
        f"\n### {D} SUN review - leads:{le} prop:{pr} paid:{paid} earned:${earned:.2f} => {flag} (see KILL RULES)\n"
    )
    with EVO.open("a") as f:
        hungry = [u for u in OWNER if not re.search(rf"payout - \$\d+\.?\d*\s+{u}\b", t)]
        if earned > 0 and "EU-JUICY" in hungry:
            hungry.remove("EU-JUICY")
        f.write(
            f"\n## Week {D} (auto review)\n"
            f"- Earned: ${earned:.2f}. Payouts: {paid}. Human minutes: {human_mins}.\n"
            f"- Hungry (0 payouts): {' '.join(hungry) if hungry else 'none — farm eats'}.\n"
            f"- Verdict: {flag}. "
            + (
                "SCALER armed — paying unit must clone ×3 within 7d."
                if flag == "SCALE?"
                else "No scaling yet — first payout still pending."
                if flag == "iterate"
                else "Manual-funnel relic with zero conversions — kill confirmed, stay passive."
            )
            + "\n"
        )
    if S.exists():
        s = S.read_text()
        s2 = re.sub(
            r"- last_review:.*",
            f"- last_review: {D} | flags: {flag} leads:{le} paid:{paid} earned:${earned:.2f}",
            s,
            count=1,
        )
        if s2 != s:
            S.write_text(s2)
    print(f"review: {flag} earned:${earned:.2f}")
    print(reward_step(t, D, earned))


if __name__ == "__main__":
    main()
