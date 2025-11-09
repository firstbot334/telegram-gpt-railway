FROM python:3.11-slim

# Prevents Python from writing .pyc files & enables unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install minimal system deps (libpq for psycopg2-binary, tzdata for KST logs)
RUN apt-get update && apt-get install -y --no-install-recommends \    build-essential \    libpq5 \    libpq-dev \    tzdata \  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \ && pip install --no-cache-dir -r requirements.txt

# Copy the rest
COPY . .

# Default timezone can be overridden by env on Railway
ENV TZ=Asia/Seoul

# Healthcheck: Python available and main file exists
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD python -c "import os; import sys; import pathlib; sys.exit(0 if pathlib.Path('run_all.py').exists() else 1)"

# Start
RUN chmod +x /app/start.sh
CMD ["bash", "-lc", "./start.sh"]
