# Telegram Collector + GPT Summary (Railway / Procfile)

## 핵심
- **유저 StringSession**만 허용 (봇 세션 차단). `validate_session.py`가 먼저 검사 후 수집/요약 실행.
- Procfile 빌드팩만 사용 (Dockerfile 불필요).

## 배포 순서
1) 레포 루트에 이 파일들을 그대로 커밋/푸시
2) Railway > Settings
   - Root Directory: 비움(루트)
   - Start Command: 비움 (Procfile 사용)
3) Variables 설정
   - TELEGRAM_API_ID / TELEGRAM_API_HASH / **TELETHON_SESSION(유저)** / DATABASE_URL / NEWS_SOURCES / BACKFILL_DAYS
   - SUMMARY_CHANNEL / OPENAI_API_KEY / TELEGRAM_TOKEN
4) Redeploy

## 로그 확인
- `validate_session.py`가 먼저 실행되어 `is_bot?: False`가 찍혀야 정상 유저 세션입니다.
- Collector: `[info] reading from: @...` / `[ok] saved: ...` 라인
- Summary: `[summary] posted`

2025-11-07 15:39 UTC 생성
