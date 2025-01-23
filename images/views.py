import json
import os
import pika
from django.views import View
from django.shortcuts import render, redirect
from .models import Image
from .forms import ImageUploadForm

RABBIT_HOST = os.environ.get('RABBIT_HOST', 'rabbitmq')
RABBIT_USER = os.environ.get('RABBIT_USER', 'user')
RABBIT_PASS = os.environ.get('RABBIT_PASS', 'password')

class ImageUploadView(View):
    def get(self, request):
        form = ImageUploadForm()
        images = Image.objects.all().order_by('-created_at')
        return render(request, 'index.html', {'form': form, 'images': images})

    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save()
            # Відправляємо повідомлення в чергу для створення thumbnails
            credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials))
            channel = connection.channel()
            channel.queue_declare(queue='thumbnails_create')
            message = {
                'id': img.id,
                'filepath': img.original.path,
                'sizes': [128, 512, 1024]
            }
            channel.basic_publish(exchange='', routing_key='thumbnails_create', body=json.dumps(message))
            connection.close()
            return redirect('/')
        return render(request, 'index.html', {'form': form})
