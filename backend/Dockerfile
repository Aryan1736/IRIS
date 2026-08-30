FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SERVING_DIR=/app/data/serving

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
COPY backend/requirements.txt /app/backend-requirements.txt

RUN pip install --no-cache-dir -r requirements.txt -r backend-requirements.txt

COPY backend/ /app/backend/
COPY src/ /app/src/
COPY data/serving/ /app/data/serving/

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
