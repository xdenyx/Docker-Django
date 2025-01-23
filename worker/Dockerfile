FROM python:3.10
WORKDIR /app
COPY worker.py /app/worker.py
RUN pip install Pillow pika
CMD ["python", "worker.py"]
