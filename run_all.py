# run_all.py — collector -> summary -> stats; weekly Monday digest at 09:00 KST
import os, time, subprocess, sys, datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")
INTERVAL = int(os.environ.get("RUN_INTERVAL_MIN","0"))

def run(cmd):
    print(f"\n=== RUN: {cmd} ===", flush=True)
    rc = subprocess.call([sys.executable, "-u"] + cmd.split())
    print(f"=== EXIT {rc}: {cmd} ===\n", flush=True)
    return rc

def do_once():
    run("collector_telethon.py")
    run("summary_poster.py")
    try:
        run("stats.py")
    except Exception:
        pass

def maybe_weekly_digest():
    now = datetime.datetime.now(tz=KST)
    want_hour = int(os.environ.get("DIGEST_HOUR","9"))
    want_weekday = os.environ.get("DIGEST_DAY","Mon")
    weekday = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][now.weekday()]
    if weekday == want_weekday and now.hour == want_hour:
        stamp = now.strftime("%Y-%m-%d")
        flag = f"/tmp/digest_{stamp}.flag"
        try:
            open(flag, "x").close()  # create if not exists
            run("weekly_digest.py")
        except FileExistsError:
            pass  # already done today

if INTERVAL <= 0:
    do_once()
else:
    while True:
        do_once()
        maybe_weekly_digest()
        print(f"Sleeping {INTERVAL} min...", flush=True)
        time.sleep(INTERVAL * 60)
