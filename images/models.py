from django.db import models

class Image(models.Model):
    original = models.ImageField(upload_to='originals/')
    thumbnails = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"
