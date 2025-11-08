# sitecustomize.py
# Python 프로세스 시작 시 자동 import되어 DB 스키마를 안전하게 보정합니다.
# - date 컬럼 추가
# - pg_trgm 확장 설치
# - BTREE 인덱스 제거 후 GIN(trigram) 인덱스 생성
# collector/summary 코드 수정 없이, 실행 초기에 자동으로 반영됩니다.

from sqlalchemy import text
try:
    from db import engine
except Exception as e:
    # db 모듈이 아직 import되지 않는 환경이라면 조용히 패스
    # (예: 로컬 도구 실행 등). 앱 런타임에선 정상 실행됨.
    engine = None

def _apply_schema():
    if engine is None:
        return
    sqls = [
        "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
        "ALTER TABLE IF EXISTS articles ADD COLUMN IF NOT EXISTS date TIMESTAMPTZ;",
        "DROP INDEX IF EXISTS ix_articles_text;",
        "CREATE INDEX IF NOT EXISTS ix_articles_text_trgm ON articles USING gin (text gin_trgm_ops);",
    ]
    with engine.begin() as conn:
        for s in sqls:
            try:
                conn.exec_driver_sql(s)
            except Exception as _e:
                # 다른 워커가 동시에 생성했을 수 있으니 안전하게 무시
                pass

try:
    _apply_schema()
except Exception:
    # 어떤 경우에도 앱 부팅을 막지 않음
    pass
