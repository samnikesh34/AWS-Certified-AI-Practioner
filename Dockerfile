FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY templates ./templates
COPY static ./static
COPY private ./private
RUN useradd --create-home appuser && mkdir -p /data && chown appuser:appuser /data
USER appuser
ENV APP_ENV=production DATABASE_PATH=/data/progress.sqlite3
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "app:app"]
