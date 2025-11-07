# Telegram Collector — Railway (Procfile)

이 프로젝트는 **Dockerfile 없이** Procfile로 배포됩니다.

## 필요한 파일(루트 위치 필수)
- `Procfile` → `worker: python collector_telethon.py`
- `collector_telethon.py`
- `config.py`, `db.py`, `models.py`
- `requirements.txt`, `runtime.txt`

## 환경 변수
- `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` — my.telegram.org에서 발급
- `TELETHON_SESSION` — 로컬에서 사용자 계정으로 만든 StringSession
- `DATABASE_URL` — Railway Postgres
- `NEWS_SOURCES` — `@ch1,@ch2` 처럼 쉼표 구분
- `BACKFILL_DAYS` — 예: `2`
- (옵션) `OPENAI_API_KEY`, `SUMMARY_CHANNEL`, `STANCE_MODEL`, `INTEREST_KEYWORDS`, `TZ`

## 배포 전 점검
1. **Railway Settings → Root Directory** 가 빈 값(루트)인지 확인
2. **Dockerfile가 레포에 없어야** Procfile이 적용됨
3. **Start Command 비우기** (Procfile이 대신 실행)

## 세션 검증
```
python validate_session.py
```
- `Is bot?: True` → 봇 세션입니다. 사용자 StringSession으로 교체하세요.

2025-11-07 15:26 UTC 생성
