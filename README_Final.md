# Final Railway Bundle — User Session Collector

이 번들은 현재 설정(Variables 스크린샷 기준)에 맞춘 **유저 세션 기반** 수집기로,
다음 문제들을 해결합니다:

- `BotMethodInvalidError / GetHistoryRequest` — 봇 세션으로 실행되던 문제 차단
- `JoinChannelRequest` 필요 없음 — 이미 가입한 채널의 히스토리만 읽음
- `NEWS_SOURCES`가 문자열/리스트 어떤 형태여도 안전하게 파싱

## 포함 파일
- `collector_telethon.py` — 실제 실행 파일 (Procfile에서 이 파일을 실행)
- `validate_session.py` — 배포 후 세션이 "봇"인지 "유저"인지 즉시 확인용

## 환경 변수 체크리스트
- `TELEGRAM_API_ID` ✔︎ (숫자)
- `TELEGRAM_API_HASH` ✔︎
- `TELETHON_SESSION` ✔︎  (로컬에서 사용자 계정으로 생성한 **StringSession**)
- `NEWS_SOURCES` ✔︎  예: `@ch1,@ch2,@group1`
- `BACKFILL_DAYS` ✔︎  예: `2`
- `DATABASE_URL` ✔︎  (Railway Postgres)
- `OPENAI_API_KEY`, `SUMMARY_CHANNEL`, `STANCE_MODEL`, `INTEREST_KEYWORDS`, `TELEGRAM_TOKEN` 등 기존 값 유지

## Procfile
```
worker: python collector_telethon.py
```

## 배포 순서
1) 깃에 `collector_telethon.py` 커밋/푸시
2) Railway Variables 위 체크리스트대로 확인
3) **Redeploy**
4) 문제가 있으면 `python validate_session.py`로 먼저 세션 타입 확인
   - `Is bot?: True` → 세션이 봇입니다. **유저 StringSession**으로 다시 만들고 TELETHON_SESSION 교체
   - `Is bot?: False` → 정상 (수집 코드 실행)

2025-11-07 14:57 UTC 생성
