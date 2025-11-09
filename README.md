# newsbot_url_only (Collector)
- 입력은 **오직 t.me URL**만 허용 (예: `https://t.me/bbbbbw0rld`)
- 내부에서도 숫자ID 변환 없이 **username만** 사용
- 키워드 매칭된 메시지 텍스트/멘트 + URL 저장
- 30분 주기 수집 & 보관 일수 경과분 자동 삭제

## Env
```
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
TELETHON_SESSION=...
SRC_CHANNELS="https://t.me/abc https://t.me/def,https://t.me/ghi"
KEYWORDS="NVDA,TSMC,배터리,전해액"
DATABASE_URL="sqlite:///./newsbot.db"
RUN_INTERVAL_MIN=30
MAX_DAYS_KEEP=60
```

## Local
```
pip install -r requirements.txt
python src/fix_schema.py
python src/run_loop.py
```

## Railway
- Builder: Dockerfile
- 위 Env 넣고 배포
Generated: 2025-11-09 10:15 UTC
