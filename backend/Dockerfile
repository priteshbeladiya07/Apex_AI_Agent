
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend/src
ENV EXPENSE_PYTHON=/opt/expense-venv/bin/python
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend-requirements.txt /tmp/backend-requirements.txt
COPY expense-requirements.txt /tmp/expense-requirements.txt

RUN python -m venv /opt/apex-venv \
    && /opt/apex-venv/bin/pip install --no-cache-dir -r /tmp/backend-requirements.txt \
    && python -m venv /opt/expense-venv \
    && /opt/expense-venv/bin/pip install --no-cache-dir -r /tmp/expense-requirements.txt

COPY backend/src/ /app/backend/src/

EXPOSE 8000

CMD ["/bin/sh", "-c", "exec /opt/apex-venv/bin/uvicorn apex_ai.main:app --app-dir /app/backend/src --host 0.0.0.0 --port ${PORT:-8000}"]
