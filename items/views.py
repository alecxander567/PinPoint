from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Item
from .serializer import ItemSerializer
import cloudinary.uploader
import qrcode
from io import BytesIO
import base64
import requests
import os

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_item(request):
    owner_id = request.data.get("owner_id")
    name = request.data.get("name")
    description = request.data.get("description", "")
    image_file = request.FILES.get("image")

    if not all([owner_id, name, image_file]):
        return Response(
            {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Upload image to Cloudinary
    upload_result = cloudinary.uploader.upload(image_file)
    image_url = upload_result.get("secure_url")

    # Generate QR code with item ID or URL (encode the item info in QR)
    item_id = str(uuid.uuid4())
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"{SUPABASE_URL}/items/{item_id}")
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    qr_code_url = f"data:image/png;base64,{qr_code_base64}"

    # Save in Supabase
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "id": item_id,
        "owner_id": owner_id,
        "name": name,
        "description": description,
        "image_url": image_url,
        "qr_code_url": qr_code_url,
    }

    supabase_response = requests.post(
        f"{SUPABASE_URL}/rest/v1/items", headers=headers, json=payload
    )

    if supabase_response.status_code in [200, 201]:
        item = Item.objects.create(
            id=item_id,
            owner_id=owner_id,
            name=name,
            description=description,
            image_url=image_url,
            qr_code_url=qr_code_url,
        )
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(
        {"error": "Failed to save item in Supabase"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
