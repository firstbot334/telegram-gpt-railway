FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata ca-certificates \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY . .
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import pathlib,sys; sys.exit(0 if pathlib.Path('src/run_all.py').exists() else 1)"
RUN chmod +x /app/start_safe.sh || true
CMD ["bash","-lc","./start_safe.sh"]
