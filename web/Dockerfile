FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

RUN mkdir -p /app/database
RUN chown -R appuser:appuser /app/database
VOLUME [ "/app/database" ]

WORKDIR /app/web

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .
COPY ./templates ./templates

USER appuser

EXPOSE 8080

CMD ["python", "app.py"]
