from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Item
from .serializer import ItemSerializer
import cloudinary.uploader
import qrcode
from io import BytesIO
import os
from users.models import User


@api_view(["POST"])
@authentication_classes([])  
def add_item(request):
    owner_id = request.data.get("owner_id")
    name = request.data.get("name")
    description = request.data.get("description", "")
    image_file = request.FILES.get("image")

    if not all([owner_id, name, image_file]):
        return Response(
            {"error": "owner_id, name, and image are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # validate user
    try:
        user = User.objects.get(id=owner_id)
    except User.DoesNotExist:
        return Response({"error": "Invalid owner_id"}, status=400)

    # upload image
    upload_result = cloudinary.uploader.upload(image_file)
    image_url = upload_result.get("secure_url")

    # create item
    item = Item.objects.create(
        owner_id=owner_id,
        name=name,
        description=description,
        image_url=image_url,
    )

    # generate QR
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"{FRONTEND_URL}/found/{item.id}")
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    # upload QR
    qr_upload = cloudinary.uploader.upload(buffer.getvalue(), resource_type="image")

    item.qr_code_url = qr_upload.get("secure_url")
    item.save()

    serializer = ItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
