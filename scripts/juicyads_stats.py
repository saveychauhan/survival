#!/usr/bin/env python3
"""Daily JuicyAds publisher stats pull — zero human work, stdlib only.
Reads token from keys.local.json (gitignored, never repo).
Endpoint: GET /statistics/popunders/publisher/{token}/{start}/{end} (docs v1.0).
Appends one LEDGER line. Exit 0 always (cron-safe).
"""
import datetime
import json
import pathlib
import subprocess
import urllib.request

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
KEYS = WS / "keys.local.json"
LEDGER = WS / "LEDGER.md"
BASE = "https://api.juicyads.com"


def log(msg):
    with LEDGER.open("a") as f:
        f.write(f"\n### {datetime.date.today().isoformat()} juicyads - {msg}\n")
    print(msg)


def main():
    try:
        token = json.loads(KEYS.read_text()).get("juicyads_api_key", "").strip()
    except Exception:
        token = ""
    if not token:
        log("KEY-MISSING (add via index form, stays local)")
        return
    end = datetime.date.today()
    start = end - datetime.timedelta(days=7)
    url = f"{BASE}/statistics/popunders/publisher/{token}/{start.isoformat()}/{end.isoformat()}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "survival-farm/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
    except Exception:
        # Fallback: system curl (Mac Python often lacks certs; curl uses system store)
        try:
            out = subprocess.run(
                ["curl", "-sS", "-m", "30", url],
                capture_output=True, text=True, timeout=40,
            )
            data = json.loads(out.stdout.strip() or "null")
        except Exception as e:
            log(f"API-FAIL ({type(e).__name__}: {e}). Key unverified - check dashboard.")
            return
    try:
        paid = sum(float(d.get("paid", 0) or 0) for d in data)
        imps = sum(int(d.get("total", 0) or 0) for d in data)
    except Exception:
        log(f"API-UNEXPECTED-RESPONSE (key accepted, shape unknown): {str(data)[:120]}")
        return
    log(f"KEY-OK 7d imps:{imps} paid:${paid:.4f} (auto, 0 human min)")


if __name__ == "__main__":
    main()
