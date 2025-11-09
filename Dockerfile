FROM python:3.11-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul

# System deps (single logical line, no CRLF, no stray spaces after backslashes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq5 libpq-dev tzdata ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import pathlib,sys; sys.exit(0 if pathlib.Path('run_all.py').exists() else 1)"

# Start
RUN chmod +x /app/start.sh || true
CMD ["bash","-lc","./start.sh"]
