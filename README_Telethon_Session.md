# Telethon StringSession 배포 패키지

`EOFError: EOF when reading a line` 문제는 서버에서 `input()`으로
전화번호/인증코드를 받을 수 없기 때문에 발생합니다.
이 패키지는 **사전 생성한 StringSession**으로 로그인하여
서버에서 **무인터랙티브 실행**을 가능하게 합니다.

## 구성
- `collector_telethon.py` : TELETHON_SESSION을 사용하여 수집 실행
- `make_session.py` : 로컬에서 세션 문자열 생성용(한 번만)
- `.env.example` : 필요한 환경변수 예시

## 사용 순서
1) 로컬에서
   ```bash
   pip install telethon
   python make_session.py
   ```
   전화번호/코드 입력 후 출력되는 **긴 문자열**을 복사합니다.

2) Railway 환경 변수에 추가
   - `TELETHON_SESSION=<복사한 세션 문자열>`
   - (이미 리포지토리에 있는) `NEWS_SOURCES`, `BACKFILL_DAYS`, DB 관련 변수 확인

3) 배포 실행
   - Dockerfile 또는 Procfile 기반으로 `python collector_telethon.py` 실행
   - 이제 더 이상 `Please enter your phone...` 프롬프트가 뜨지 않습니다.

## 참고
- 세션이 만료되거나 로그아웃되면 다시 `make_session.py`로 새로 발급받아 교체하세요.
