# 뉴스 수집·요약·배포 봇 — Railway 배포용 (FIXED)

이 폴더는 **Dockerfile 우선**으로 빌드되며, 필요 시 **Nixpacks**로도 동작하도록 구성했습니다.
스크린샷의 `Error creating build plan with Railpack` 문제를 우회/해결합니다.

## ✅ 핵심 변경점
1) `Dockerfile`을 강화(시스템 라이브러리 설치 + `start.sh`)하여 빌드 실패를 줄였습니다.  
2) `railway.json`에서 **builder=dockerfile**을 강제 → Railpack/Nixpacks 플랜 생성 오류를 회피.  
3) `nixpacks.toml`도 포함(백업 플랜). Railway가 Nixpacks로 잡더라도 정상 실행.  
4) `start.sh`가 실행 전에 **스키마 자동 보정(fix_schema.py)** → 런타임 스키마 이슈 최소화.  
5) `.env.example` 제공: 필수 환경변수 정리.

## 🔧 배포 순서 (Railway)
1. 이 리포를 Railway에 연결(GitHub).  
2. **Settings → Build** 에서 Builder가 *Dockerfile*인지 확인. (아니면 Dockerfile로 변경)  
3. **Variables**에 `.env.example` 기준으로 값을 등록:
   - `DATABASE_URL` (Railway Postgres의 *psycopg2 접속 문자열* 사용 권장)
   - `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELETHON_SESSION`  
   - `OPENAI_API_KEY`, `DEST_BOT_TOKEN`, `DEST_CHAT_ID` 등
4. **Deploy**. 첫 실행에서 `fix_schema.py`가 테이블/인덱스를 자동 생성/보정합니다.

> 여전히 Railpack 오류가 보인다면: 기존 빌드 캐시 삭제 후 재배포, 또는 Settings→Source에서 Root Directory/Start Command를 비우고 재시도하세요.

## 🧪 로컬 테스트
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export $(cat .env.example | grep -v '^#' | xargs)  # 예시 환경값 로드
python -u fix_schema.py
python -u run_all.py
```

## ⏱ 운영
- `RUN_INTERVAL_MIN=10` → 10분마다 `collector → summarizer/poster → weekly_digest(조건)` 흐름 실행
- 매주 월요일 09:00(KST)에는 주간 다이제스트 전송
- `MAX_DAYS_KEEP` 기준으로 오래된 데이터 prune

## 🧩 자주 막히는 포인트
- `Error creating build plan with Railpack` → 이 리포는 **Dockerfile 강제**로 해결
- `psycopg2` 빌드 문제 → slim 이미지에 `libpq5`, `libpq-dev` 추가 설치(이미 반영)
- 타임존 로그가 뒤죽박죽 → `TZ=Asia/Seoul` 환경변수 설정

---
Generated: 2025-11-09 07:23 UTC
