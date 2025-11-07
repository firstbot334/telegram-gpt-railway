# Railway Python Deployment (Procfile Only)

이 구성은 **Dockerfile 없이** 간단하게 Railway에서 Python buildpack으로 인식되도록 만든 버전입니다.

## 포함 파일
- `Procfile` → 서비스 실행 커맨드 정의
- `runtime.txt` → Python 버전 지정
- `requirements.txt` → 필요한 패키지 정의

## 사용 방법
1. Railway 프로젝트 루트에 이 세 파일을 그대로 복사
2. `collector_telethon.py` 등 실행할 스크립트가 **레포 루트에 존재**해야 함
3. `Procfile` 내용:
   ```
   worker: python collector_telethon.py
   ```
4. 커밋 → Redeploy

빌드 로그에 `Python app detected` 가 뜨면 성공입니다.