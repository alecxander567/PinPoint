import uuid
from django.db import models


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_id = models.UUIDField()  
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image_url = models.URLField()
    qr_code_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
