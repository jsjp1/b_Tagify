FROM python:3.11-slim

WORKDIR /app

EXPOSE 8000

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ /app
COPY .env /app

ENV PYTHONPATH="/app"

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "3"]
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "3", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "app.main:app"]