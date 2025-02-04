FROM python:3.11

WORKDIR /app

COPY server/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/app /app
COPY .env /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]