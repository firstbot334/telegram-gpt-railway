# run_all.py — loop runner + weekly digest + retention pruning
import os, time, subprocess, sys, datetime
from zoneinfo import ZoneInfo
from db import SessionLocal
from models import Article

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
    import datetime as _dt
    now = _dt.datetime.now(tz=KST)
    want_hour = int(os.environ.get("DIGEST_HOUR","9"))
    want_weekday = os.environ.get("DIGEST_DAY","Mon")
    weekday = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][now.weekday()]
    if weekday == want_weekday and now.hour == want_hour:
        stamp = now.strftime("%Y-%m-%d")
        flag = f"/tmp/digest_{stamp}.flag"
        try:
            open(flag, "x").close()
            run("weekly_digest.py")
        except FileExistsError:
            pass

def maybe_prune():
    keep = int(os.environ.get("RETENTION_DAYS", "0"))
    trim = int(os.environ.get("TRIM_TEXT_AFTER_DAYS", "0"))
    s = SessionLocal()
    try:
        if keep > 0:
            cutoff = datetime.datetime.now(tz=KST) - datetime.timedelta(days=keep)
            deleted = s.query(Article).filter(Article.date < cutoff).delete(synchronize_session=False)
            s.commit()
            if deleted:
                print(f"[prune] deleted {deleted} rows (< {keep}d)")
        if trim > 0:
            cutoff2 = datetime.datetime.now(tz=KST) - datetime.timedelta(days=trim)
            updated = s.query(Article).filter(Article.date < cutoff2, Article.text != None).update({Article.text: None}, synchronize_session=False)
            s.commit()
            if updated:
                print(f"[prune] trimmed text on {updated} rows (< {trim}d)")
    finally:
        s.close()

if INTERVAL <= 0:
    do_once()
    maybe_prune()
    maybe_weekly_digest()
else:
    while True:
        do_once()
        maybe_prune()
        maybe_weekly_digest()
        print(f"Sleeping {INTERVAL} min...", flush=True)
        time.sleep(INTERVAL * 60)
