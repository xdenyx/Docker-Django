import os
import json
import pika
from PIL import Image
from pathlib import Path

RABBIT_HOST = os.environ.get('RABBIT_HOST', 'rabbitmq')
RABBIT_USER = os.environ.get('RABBIT_USER', 'user')
RABBIT_PASS = os.environ.get('RABBIT_PASS', 'password')
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/app/media')

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='thumbnails_create')
channel.queue_declare(queue='thumbnails_result')

def create_thumbnails(image_path, sizes):
    thumbnails_info = []
    with Image.open(image_path) as img:
        base_name = Path(image_path).stem
        ext = Path(image_path).suffix
        thumb_dir = os.path.join(MEDIA_ROOT, 'thumbnails')
        os.makedirs(thumb_dir, exist_ok=True)
        for size in sizes:
            img_copy = img.copy()
            img_copy.thumbnail((size, size))
            thumb_filename = f"{base_name}_{size}{ext}"
            thumb_path = os.path.join(thumb_dir, thumb_filename)
            img_copy.save(thumb_path)
            thumbnails_info.append({str(size): f"thumbnails/{thumb_filename}"})
    return thumbnails_info

def callback(ch, method, properties, body):
    data = json.loads(body)
    img_id = data['id']
    filepath = data['filepath']
    sizes = data['sizes']

    thumbs = create_thumbnails(filepath, sizes)
    result = {
        'id': img_id,
        'thumbnails': thumbs
    }
    channel.basic_publish(exchange='', routing_key='thumbnails_result', body=json.dumps(result))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='thumbnails_create', on_message_callback=callback)

print("Worker started. Waiting for messages...")
channel.start_consuming()
