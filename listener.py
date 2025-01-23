import os
import django
import pika
import json
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab2.settings')
django.setup()

from images.models import Image

RABBIT_HOST = os.environ.get('RABBIT_HOST', 'rabbitmq')
RABBIT_USER = os.environ.get('RABBIT_USER', 'user')
RABBIT_PASS = os.environ.get('RABBIT_PASS', 'password')

# Очікуємо деякий час поки RabbitMQ підніметься
time.sleep(10)

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='thumbnails_result')

def callback(ch, method, properties, body):
    data = json.loads(body)
    img_id = data['id']
    thumbs = data['thumbnails']  # [{"128": "path"}, ...]
    image = Image.objects.get(id=img_id)
    thumb_dict = {}
    for t in thumbs:
        thumb_dict.update(t)
    image.thumbnails = thumb_dict
    image.save()
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='thumbnails_result', on_message_callback=callback)
print("Listening for thumbnail results...")
channel.start_consuming()
