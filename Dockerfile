FROM python:3.10
WORKDIR /app


RUN pip install Django psycopg2 Pillow gunicorn pika

COPY . /app
# Зберігаємо статику (якщо потрібно)
RUN python manage.py
EXPOSE 8000
