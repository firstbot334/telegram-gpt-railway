# Buildpack Hard Fix
- 루트에 이 파일들 그대로 올리고, Settings→Source에서 Root Directory 비우기, Settings→Deploy에서 Start Command 비우기, Dockerfile 삭제.
- 첫 배포는 `Procfile`(validate→collector) 사용. 정상 확인 후 `Procfile.dual` 내용으로 바꿔 커밋하면 요약도 동시에 실행.

Generated 2025-11-07 16:24 UTC
