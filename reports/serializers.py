from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_image_url = serializers.URLField(source="item.image_url", read_only=True)
    item_qr_code_url = serializers.URLField(source="item.qr_code_url", read_only=True)
    owner_fb_url = serializers.CharField(
        source="item.owner_fb_account_url", read_only=True
    )

    class Meta:
        model = Report
        fields = [
            "id",
            "item",
            "landmark",
            "landmark_image_url",
            "location",
            "message",
            "is_resolved",
            "view_token",
            "created_at",
            "item_name",
            "item_image_url",
            "item_qr_code_url",
            "owner_fb_url",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "is_resolved",
            "view_token",
            "item_name",
            "item_image_url",
            "item_qr_code_url",
            "owner_fb_url",
            "landmark_image_url",
        ]
