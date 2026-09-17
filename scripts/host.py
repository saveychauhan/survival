#!/usr/bin/env python3
"""Host self-awareness — the farm knows where it lives and its limits.
Detects OS/machine/Python, cron presence, uptime, disk, net, power state (Mac).
Appends one LEDGER line. Zero human work, stdlib only, exit 0 always.
"""
import datetime
import pathlib
import platform
import shutil
import subprocess
import sys

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
LEDGER = WS / "LEDGER.md"


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def main():
    sys_name = platform.system()
    if sys_name == "Darwin":
        mac_ver = platform.mac_ver()[0] or "?"
        host = f"Mac macOS {mac_ver} {platform.machine()}"
        boot = sh(["sysctl", "-n", "kern.boottime"])
        batt = sh(["pmset", "-g", "batt"])
        on_batt = "Battery" in batt and "AC" not in batt.split(";")[0]
        asleep_risk = "sleep"  # Mac cron never fires while asleep — the #1 limit
        limits = "cron dead while asleep/off; Intel CPU, no GPU; home IP; lid must stay open + charger on"
    else:
        host = f"{sys_name} {platform.machine()} (cloud runner?)"
        boot, on_batt, asleep_risk = "", False, "none — cloud always awake"
        limits = "runner minutes; no local secrets unless injected"
    cron_out = sh(["crontab", "-l"])
    cron = len([l for l in cron_out.splitlines() if "survival" in l])
    disk = shutil.disk_usage(str(WS)).free // (1024 ** 3)
    py = platform.python_version()
    D = datetime.date.today().isoformat()
    msg = (f"host - {host} | py {py} | cron {cron} jobs | disk {disk}GB free | "
           f"{'ON-BATTERY' if on_batt else 'on-power'} | sleep-risk: {asleep_risk} | limits: {limits}")
    with LEDGER.open("a") as f:
        f.write(f"\n### {D} {msg}\n")
    print(msg)


if __name__ == "__main__":
    main()
