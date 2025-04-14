# ===== BASE =====
FROM python:3.12-slim AS base
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ===== FINAL PROD =====
FROM base AS prod

# Установим LibreOffice для PDF-конвертации
RUN apt update && \
    apt install -y libreoffice libreoffice-writer libreoffice-calc && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

# Открываем порт
EXPOSE 8000

# Поддержка переменных окружения через .env
ENV PYTHONUNBUFFERED=1

# CMD или gunicorn / uvicorn запуск
CMD ["gunicorn", "-c", "gunicorn.conf.py", "run:app"]
