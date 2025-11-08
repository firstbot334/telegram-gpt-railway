# 배포/실행 (Railway - Worker 방식)

- 단일 진입점: **Procfile** 의 worker 프로세스만 사용합니다.
- `nixpacks.toml` 은 제거했습니다. (충돌 방지)

## 실행 방식
Railway에서 서비스 타입을 **Worker**로 생성하고, 빌드 후 이 worker가 자동 시작되도록 설정하세요.

### Procfile
```
worker: python -u listener.py
```

- `-u` 옵션으로 버퍼링을 끄고 실시간 로그를 확보합니다.
- 실행 진입점은 `listener.py` 하나입니다.

## 배포 순서
1. 이 ZIP을 Railway에 업로드(또는 연결된 Git에 반영)합니다.
2. **Rebuild & Deploy** 를 진행합니다.
3. 배포 후 **Restart all** 로 완전 재시작(캐시된 이전 이미지 사용 방지).
4. Logs 에서 `listener.py started` 또는 봇 연결 메시지를 확인하세요.

## 환경 변수(예시)
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `BOT_TOKEN` 등 필요한 값들을 Railway **Variables**에 등록하세요.

## 주의
- 다른 진입점 파일(예: `nixpacks.toml`)이 있으면 충돌이 날 수 있으니 포함하지 마세요.
- Web 서비스로 띄우지 않는 한, 포트 바인딩은 불필요합니다.
- 스케일 1 이상으로 늘리면 동일 봇이 중복 동작할 수 있으니 주의하세요.