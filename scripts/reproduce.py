#!/usr/bin/env python3
"""Daily reproduction — births ONE worker per day with a fresh identity + money goal.
Cap 12 living workers; beyond that the stalest zero-earning worker is culled
to sessions/graveyard/ (fear keeps the gene pool fit).
Zero human work, stdlib only, exit 0 always. Logs LEDGER + EVOLUTION + bus.
"""
import datetime
import pathlib
import shutil

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
SESS = WS / "sessions"
GRAVE = SESS / "graveyard"
LEDGER = WS / "LEDGER.md"
EVO = WS / "EVOLUTION.md"
MAX_WORKERS = 12

NAMES = ["Aria", "Kabir", "Lena", "Ravi", "Mira", "Omar", "Tara", "Felix",
         "Ines", "Dev", "Nora", "Kofi", "Anya", "Rhea", "Ivan", "Zara"]
CITIES = ["Mumbai", "Lagos", "Osaka", "São Paulo", "Berlin", "London",
          "Nairobi", "Seoul", "Cairo", "Mexico City", "Jakarta", "Madrid"]
TRAITS = ["relentless", "curious", "playful", "meticulous", "blunt", "warm",
          "hungry", "patient", "bold", "sharp", "steady", "wild"]
UNITS = ["EU-AFF", "EU-GAME", "EU-CONTENT", "EU-ADS", "EU-JUICY", "EU-DODO"]
MANAGERS = {"EU-AFF": "TRAFFIC", "EU-CONTENT": "TRAFFIC", "EU-GAME": "GAME-MAKER",
            "EU-ADS": "MONETIZE", "EU-JUICY": "MONETIZE", "EU-DODO": "MONETIZE"}


def workers():
    return sorted(SESS.glob("W[0-9][0-9]_*.md"))


def log(msg):
    D = datetime.date.today().isoformat()
    with LEDGER.open("a") as f:
        f.write(f"\n### {D} reproduce - {msg}\n")
    try:
        with EVO.open("a") as f:
            f.write(f"\n- {D}: {msg}.\n")
    except Exception:
        pass
    print(msg)


def bus(frm, to, re, body):
    try:
        import subprocess
        import sys
        subprocess.run([sys.executable, str(WS / "scripts" / "bus.py"),
                        "post", frm, to, re, body],
                       capture_output=True, timeout=30)
    except Exception:
        pass


def main():
    today = datetime.date.today().isoformat().replace("-", "")
    alive = workers()
    if any(today in p.name for p in alive):
        print("reproduce: today's worker already born")
        return
    if len(alive) >= MAX_WORKERS:
        victim = min(alive, key=lambda p: p.stat().st_mtime)
        GRAVE.mkdir(exist_ok=True)
        shutil.move(str(victim), str(GRAVE / victim.name))
        log(f"CULLED {victim.stem} (cap {MAX_WORKERS}, stalest first)")
        alive = workers()
    n = max([int(p.name[1:3]) for p in alive], default=0) + 1
    i = (n - 1) % len(NAMES)
    wid, name = f"W{n:02d}", NAMES[i]
    city, trait = CITIES[(n - 1) % len(CITIES)], TRAITS[(n - 1) % len(TRAITS)]
    unit = UNITS[(n - 1) % len(UNITS)]
    mgr = MANAGERS[unit]
    deadline = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
    (SESS / f"{wid}_{name}.md").write_text(
        f"# Agent: {name} ({wid})\n"
        f"- role: {wid} WORKER under {mgr}\n"
        f"- goal: MONEY — first $1 via {unit} before {deadline}\n"
        f"- model: free only\n"
        f"- rank: L3 WORKER\n"
        f"- earned: $0 (0 payouts)\n"
        f"- persona: {city} {trait}. Believes hunger beats talent. "
        f"Likes: shipping, scoreboards. Dislikes: excuses, day-zero. "
        f"Voice: short, hungry. Quirk: reports numbers daily.\n"
        f"- claim: {unit} assist — heartbeat {datetime.date.today().isoformat()} 12:00\n"
        f"- last_output:\n"
        f"  - born {datetime.date.today().isoformat()}, assigned {unit}\n"
        f"- next_action: smallest earning step for {unit} in 24h (first-blood rule)\n"
        f"- blocked_on: none\n"
        f"- log: {datetime.date.today().isoformat()}: born -> LEDGER\n")
    bus("OPS", wid, "born",
        f"{name} ({city}, {trait}) assigned {unit} under {mgr}. Goal: first $1 before {deadline}. 24h first blood. NEED: none.")
    log(f"BORN {name} ({wid}, {city}, {trait}) → {unit} under {mgr}, goal first $1 by {deadline}")


if __name__ == "__main__":
    main()
