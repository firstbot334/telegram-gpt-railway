# Railway Python Fix (Procfile Buildpack)

이 패치는 Railway에서 `python: command not found` 오류를 해결하기 위해
**정상 Procfile(확장자 없음)** 을 추가합니다.

## 포함 파일
- `Procfile` : `worker: python collector_telethon.py`

## 적용 방법
1. 이 zip을 다운받아 리포지토리 루트에 `Procfile`을 추가하세요. (확장자 `.txt` 금지)
2. 이미 리포지토리에 `runtime.txt`와 `requirements.txt`가 있으므로 그대로 두세요.
   - `runtime.txt` 예: `python-3.11.9`
3. 커밋 & 푸시한 뒤 Railway에서 **Redeploy**를 눌러 재배포합니다.
4. 재배포 로그에 아래 메시지가 보이면 정상입니다.
   ```
   -----> Python app detected
   -----> Installing python-3.11.9
   -----> Installing pip packages from requirements.txt
   ```

## 환경 변수 체크리스트 (Railway Variables)
- `OPENAI_API_KEY`
- `TELEGRAM_TOKEN` (또는 `TELEGRAM_BOT_TOKEN`)
- `SUMMARY_CHANNEL`
- `STANCE_MODEL` (예: gpt-4o-mini)
- `INTEREST_KEYWORDS` (콤마로 구분된 문자열)
- `DATABASE_URL`

## 실행 엔트리포인트
- Procfile은 Worker 프로세스로 `collector_telethon.py`를 실행합니다.
  필요 시 다음과 같이 변경 가능:
  - `worker: python summarize_news.py --window day`
  - `worker: python summarize_news.py --window night`

## 참고
- Dockerfile을 사용하고 싶다면, Procfile 대신 Dockerfile을 리포지토리에 추가하고
  Railway가 Docker 모드로 빌드하도록 하세요. (동시에 두 개가 있으면 Dockerfile이 우선될 수 있음)
