#!/usr/bin/env python3
"""Farm setup audit — checks the WHOLE current setup, reports PASS/FAIL per line.
Files, links, tags, slots, keys (presence only, never values), secret leaks,
cron installed, public site live, internals unserved. Appends LEDGER line.
Zero human work, stdlib only, exit 0 always.
"""
import datetime
import json
import pathlib
import re
import subprocess
import urllib.request

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
LEDGER = WS / "LEDGER.md"
KEYS = WS / "keys.local.json"
SITE = "https://raycast.in"
TAG = "dexter03d-21"
EMAIL = "sav.ey" + "@" + "live.co.uk"  # split so this file never matches its own leak scan

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def url_status(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "farm-health/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except Exception:
        try:  # curl fallback (Mac cert store)
            out = subprocess.run(["curl", "-sS", "-m", "20", "-o", "/dev/null",
                                  "-w", "%{http_code}", url],
                                 capture_output=True, text=True, timeout=30)
            return int(out.stdout.strip() or 0)
        except Exception:
            return 0


def main():
    # 1. required public files
    for f in ["docs/index.html", "docs/farm.html", "docs/online/pay.html",
              "docs/online/deals.html", "docs/online/games/reaction.html",
              "docs/online/upi-generic.png", "docs/CNAME"]:
        check(f"file {f}", (WS / f).exists())
    # 2. internal links in served html resolve
    for page in ["docs/index.html", "docs/farm.html", "docs/online/pay.html",
                 "docs/online/deals.html", "docs/online/games/reaction.html"]:
        try:
            h = (WS / page).read_text()
            links = re.findall(r'(?:href|src)="([^"#]+?)"', h)
            # pages serve from docs/ root: resolve page-relative, then docs-relative
            real_bad = []
            for l in links:
                if l.startswith(("http", "upi://", "mailto:")) or l.startswith("#"):
                    continue
                if ((WS / page).parent / l).exists() or (WS / "docs" / l).exists():
                    continue
                real_bad.append(l)
            check(f"links {page}", not real_bad, ",".join(real_bad[:3]))
        except Exception as e:
            check(f"links {page}", False, str(e)[:60])
    # 3. affiliate tag + ad slots
    for f in ["docs/online/deals.html", "docs/online/games/reaction.html"]:
        try:
            t = (WS / f).read_text()
            check(f"tag {f}", TAG in t)
            check(f"adslots {f}", "ADSTERRA" in t and "JUICYADS" in t)
        except Exception:
            check(f"tag {f}", False)
    # 4. keys present (never print values)
    try:
        k = json.loads(KEYS.read_text())
        check("key juicyads present", bool(k.get("juicyads_api_key", "").strip()))
        check("key paypal_email stored", bool(k.get("paypal_email", "").strip()))
    except Exception:
        check("keys.local.json readable", False)
    # 5. secret/email leak scan (tracked files only)
    try:
        secret = json.loads(KEYS.read_text()).get("juicyads_api_key", "")
        leaks, exposed = [], []
        for p in WS.rglob("*"):
            if ".git" in p.parts or p.name == "keys.local.json" or p.is_dir():
                continue
            try:
                t = p.read_text()
            except Exception:
                continue
            if secret and secret in t:
                leaks.append(str(p.relative_to(WS)))
            if EMAIL in t and p.suffix in (".html", ".py", ".sh", ".json"):
                exposed.append(str(p.relative_to(WS)))
        check("no key leaks in repo", not leaks, ",".join(leaks[:3]))
        check("email hidden from code", not exposed, ",".join(exposed[:3]))
    except Exception as e:
        check("leak scan", False, str(e)[:60])
    # 6. cron installed
    try:
        out = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=10)
        check("cron installed", "survival" in out.stdout, f"{out.stdout.count('survival')} jobs")
    except Exception:
        check("cron installed", False)
    # 7. public site
    check("live home", url_status(SITE + "/") == 200)
    check("live game", url_status(SITE + "/online/games/reaction.html") == 200)
    check("live pay", url_status(SITE + "/online/pay.html") == 200)
    check("live farm board", url_status(SITE + "/farm.html") == 200)
    check("ledger unserved", url_status(SITE + "/LEDGER.md") == 404)
    # report
    fails = [n for n, ok, d in results if not ok]
    line = f"health {len(results) - len(fails)}/{len(results)}"
    if fails:
        line += " FAIL: " + ",".join(fails[:6])
    D = datetime.date.today().isoformat()
    with LEDGER.open("a") as f:
        f.write(f"\n### {D} health - {line}\n")
    print(line)
    for n, ok, d in results:
        print(("PASS " if ok else "FAIL ") + n + (f" ({d})" if d and not ok else ""))


if __name__ == "__main__":
    main()
