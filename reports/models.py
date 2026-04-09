import uuid
from django.db import models
from items.models import Item


class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="reports")
    landmark = models.CharField(max_length=255, blank=True)
    landmark_image_url = models.URLField(blank=True)
    location = models.TextField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.item.name} - {self.created_at}"

    class Meta:
        ordering = ["-created_at"]
