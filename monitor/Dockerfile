FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY monitor/ ./monitor
WORKDIR /app/monitor

ENV FLASK_ENV=production
EXPOSE 5000
CMD ["python", "app.py"]
