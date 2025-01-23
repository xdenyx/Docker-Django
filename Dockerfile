FROM python:3.10
WORKDIR /app


RUN pip install Django psycopg2 Pillow gunicorn pika

COPY . /app

RUN python manage.py
EXPOSE 8000
