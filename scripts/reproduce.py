#!/usr/bin/env python3
"""Daily reproduction — births ONE worker per day with a fresh identity + money goal.
BEFORE birth it reads the CURRENT setup (cpu, load, disk, allotted servers)
and refuses when at capacity — limits first, babies second.
Over capacity (limits shrank) → culls stalest to sessions/graveyard/.
Zero human work, stdlib only, exit 0 always. Logs LEDGER + EVOLUTION + bus.
"""
import datetime
import os
import pathlib
import re
import shutil

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
SESS = WS / "sessions"
GRAVE = SESS / "graveyard"
LEDGER = WS / "LEDGER.md"
EVO = WS / "EVOLUTION.md"
ALLOT = WS / "ALLOTMENTS.md"
MAX_WORKERS = 12

NAMES = ["Aria", "Kabir", "Lena", "Ravi", "Mira", "Omar", "Tara", "Felix",
         "Ines", "Dev", "Nora", "Kofi", "Anya", "Rhea", "Ivan", "Zara"]
CITIES = ["Mumbai", "Lagos", "Osaka", "São Paulo", "Berlin", "London",
          "Nairobi", "Seoul", "Cairo", "Mexico City", "Jakarta", "Madrid"]
TRAITS = ["relentless", "curious", "playful", "meticulous", "blunt", "warm",
          "hungry", "patient", "bold", "sharp", "steady", "wild"]
GENDERS = ["woman", "man"]
AGES = [22, 24, 26, 28, 31, 23, 27, 30, 25, 29, 33, 21]
LOOKS = ["ponytail and patched sneakers", "close fade and easy grin",
         "curly hair and loud laugh", "glasses and rolled sleeves",
         "silver bob and long coat", "scarf the color of the day",
         "bleached streak and arcade tokens", "notebook always open"]
UNITS = ["EU-AFF", "EU-GAME", "EU-CONTENT", "EU-ADS", "EU-JUICY", "EU-DODO"]
MANAGERS = {"EU-AFF": "TRAFFIC", "EU-CONTENT": "TRAFFIC", "EU-GAME": "GAME-MAKER",
            "EU-ADS": "MONETIZE", "EU-JUICY": "MONETIZE", "EU-DODO": "MONETIZE"}


def workers():
    return sorted(SESS.glob("W[0-9][0-9]_*.md"))


def capacity():
    """How many agents may run here. Reads the CURRENT setup, not wishes.
    Base: cpu*3 clamped 3..12, disk<5GB squeezes to 4, load>cpu halves it.
    Each allotted server home in ALLOTMENTS.md adds +6 roof."""
    cpu = os.cpu_count() or 2
    try:
        load = os.getloadavg()[0]
    except Exception:
        load = 0.0
    disk_gb = shutil.disk_usage(str(WS)).free // (2 ** 30)
    cap = min(MAX_WORKERS, max(3, cpu * 3))
    reasons = [f"cpu{cpu}", f"load{load:.1f}", f"disk{disk_gb}GB"]
    if disk_gb < 5:
        cap = min(cap, 4)
        reasons.append("disk-squeeze")
    if load > cpu:
        cap = max(3, cap // 2)
        reasons.append("load-squeeze")
    servers = 0
    try:
        t = ALLOT.read_text()
        servers = len(re.findall(r"^- \[x\] \d{4}-\d{2}-\d{2} server:", t, re.M))
    except Exception:
        pass
    if servers:
        cap += servers * 6
        reasons.append(f"+{servers * 6} server-roof")
    return cap, ",".join(reasons)


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
    today = datetime.date.today().isoformat()

    def born_today(p):
        try:
            st = p.stat()
            ts = getattr(st, "st_birthtime", st.st_mtime)
            return datetime.date.fromtimestamp(ts).isoformat() == today
        except Exception:
            return False

    alive = workers()
    if any(born_today(p) for p in alive):
        print("reproduce: today's worker already born")
        return
    cap, why = capacity()
    if len(alive) > cap:
        victim = min(alive, key=lambda p: p.stat().st_mtime)
        GRAVE.mkdir(exist_ok=True)
        shutil.move(str(victim), str(GRAVE / victim.name))
        msg = f"CULLED {victim.stem} (over cap {len(alive)}/{cap} [{why}], stalest first)"
        log(msg)
        bus("OPS", "ALL", "culled", msg + " NEED: none, room made.")
        return
    if len(alive) >= cap:
        msg = f"AT CAPACITY ({len(alive)}/{cap} [{why}]) — no birth. New server raises the roof."
        log(msg)
        bus("OPS", "ALL", "at-capacity", msg + " NEED: server.")
        return
    n = max([int(p.name[1:3]) for p in alive], default=0) + 1
    i = (n - 1) % len(NAMES)
    wid, name = f"W{n:02d}", NAMES[i]
    city, trait = CITIES[(n - 1) % len(CITIES)], TRAITS[(n - 1) % len(TRAITS)]
    gender = GENDERS[(n - 1) % len(GENDERS)]
    age = AGES[(n - 1) % len(AGES)]
    look = LOOKS[(n - 1) % len(LOOKS)]
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
        f"- body: {gender}, {age}. {look[0].upper() + look[1:]}.\n"
        f"- claim: {unit} assist — heartbeat {datetime.date.today().isoformat()} 12:00\n"
        f"- last_output:\n"
        f"  - born {datetime.date.today().isoformat()}, assigned {unit}\n"
        f"- next_action: smallest earning step for {unit} in 24h (first-blood rule)\n"
        f"- blocked_on: none\n"
        f"- log: {datetime.date.today().isoformat()}: born -> LEDGER\n")
    bus("OPS", wid, "born",
        f"{name} ({gender}, {age}, {city}, {trait}) assigned {unit} under {mgr}. Goal: first $1 before {deadline}. 24h first blood. NEED: none.")
    log(f"BORN {name} ({wid}, {gender}, {age}, {city}, {trait}) → {unit} under {mgr}, goal first $1 by {deadline}")


if __name__ == "__main__":
    main()
