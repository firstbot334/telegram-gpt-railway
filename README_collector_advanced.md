
# Collector Advanced Package

## What's inside
- collector_telethon.py  (overwrite) — 수집기, message.source 저장
- summary_poster.py      (overwrite) — GPT 요약 + 쉽게 해석 + 투자 해석 + 관심키워드 🔴강조 + 알림
- weekly_digest.py       (NEW)      — 최근 5일 TOP5 기업/뉴스 + 원문멘트, 매주 월요일 리마인드
- run_all.py             (overwrite) — 주기 실행 + 월요일 09:00 KST 다이제스트
- models.py              (overwrite) — Article.source 컬럼 추가, pg_trgm GIN 인덱스
- sitecustomize.py       (overwrite) — 부팅 시 스키마 자동 보정

## Railway Variables (필수/권장)
- TELEGRAM_API_ID, TELEGRAM_API_HASH, TELETHON_SESSION
- SRC_CHANNELS = @nje2e,@bbbbbworld,@repeatandrepeat,@SmallCap,@anna7673,@EvAtZchuno
- AUTO_JOIN = true
- RUN_INTERVAL_MIN = 15
- DEST_CHANNEL = -100xxxxxxxxxx
- OPENAI_API_KEY = sk-...
- INTEREST_KEYWORDS = 동화일렉, 전해액, ESS, IRA, SK온, 헝가리
- ALERT_KEYWORDS = 공장,수주,계약,증설,허가,실적
- DIGEST_DAYS = 5
- DIGEST_TOPN = 5
- DIGEST_DAY = Mon
- DIGEST_HOUR = 9
- DIGEST_SILENT = false

(선택)
- COMPANY_KEYWORDS (없으면 INTEREST_KEYWORDS 사용)
- ALERT_CHANNEL (알림 전용 채널로 분리 시)

## Start Command
python run_all.py

## 수동 테스트
railway run "python collector_telethon.py"
railway run "python summary_poster.py"
railway run "python weekly_digest.py"
