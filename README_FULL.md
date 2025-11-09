# 뉴스 수집·요약·배포 봇 — FULL FIX (Railway-ready)

이 패키지는 다음 이슈들을 **모두 해결**합니다.

- Railpack/Nixpacks 빌드 플랜 오류 → **Dockerfile 강제**
- apt 오류/CRLF 줄끝 문제 → **LF 강제 + 단일 RUN 라인**
- Telethon 엔티티 해석 실패(`-100...`) → **소스 검증 + 가이드**
- 링크만 있는 메시지 → **페이지 크롤링 후 본문 추출/요약**
- OpenAI API 예외/속도 제한 → **재시도/타임아웃**
- SHA-256 중복 방지, 스키마 자동 보정, 주간 다이제스트(월 09:00 KST)

## 배포
1) 깃허브 푸시
2) Railway → Settings → Build → **Builder = Dockerfile**
3) Variables 설정(.env 키는 `src/config.py` 참고)
4) Deploy

## 로컬
```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export $(cat .env | xargs)  # 또는 개별 export
python -u src/fix_schema.py
python -u src/run_all.py
```
Generated: 2025-11-09 07:44 UTC
