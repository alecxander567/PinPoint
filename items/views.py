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


def get_public_id_from_url(url):
    try:
        if "upload/" in url:
            path_after_upload = url.split("upload/")[1]
            public_id = path_after_upload.split(".")[0]
            return public_id
        return None
    except:
        return None


@api_view(["GET"])
@authentication_classes([])
def get_item_detail(request, item_id):
    """Get a single item by id for public frontend consumption."""
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([])
def get_user_items(request):
    """Get all items for a specific user"""
    owner_id = request.query_params.get("owner_id")

    if not owner_id:
        return Response(
            {"error": "owner_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        User.objects.get(id=owner_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid owner_id"}, status=status.HTTP_400_BAD_REQUEST
        )

    items = Item.objects.filter(owner_id=owner_id).order_by("-created_at")
    serializer = ItemSerializer(items, many=True)

    return Response(
        {"count": items.count(), "items": serializer.data},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([])
def add_item(request):
    owner_id = request.data.get("owner_id")
    name = request.data.get("name")
    description = request.data.get("description", "")
    owner_fb_account_url = request.data.get("owner_fb_account_url", "")
    image_file = request.FILES.get("image")

    if not all([owner_id, name, image_file, owner_fb_account_url]):
        return Response(
            {"error": "owner_id, name, image, and owner_fb_account_url are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(id=owner_id)
    except User.DoesNotExist:
        return Response({"error": "Invalid owner_id"}, status=400)

    upload_result = cloudinary.uploader.upload(image_file)
    image_url = upload_result.get("secure_url")

    item = Item.objects.create(
        owner_id=owner_id,
        name=name,
        description=description,
        image_url=image_url,
        owner_fb_account_url=owner_fb_account_url,
    )

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"{FRONTEND_URL}/found/{item.id}")
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    qr_upload = cloudinary.uploader.upload(buffer.getvalue(), resource_type="image")

    item.qr_code_url = qr_upload.get("secure_url")
    item.save()

    serializer = ItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
@authentication_classes([])
def update_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)

    name = request.data.get("name")
    description = request.data.get("description")
    owner_fb_account_url = request.data.get("owner_fb_account_url")
    image_file = request.FILES.get("image")

    if name:
        item.name = name

    if description is not None:
        item.description = description

    if owner_fb_account_url is not None:
        item.owner_fb_account_url = (
            owner_fb_account_url if owner_fb_account_url else None
        )

    if image_file:
        if item.image_url:
            old_public_id = get_public_id_from_url(item.image_url)
            if old_public_id:
                cloudinary.uploader.destroy(old_public_id)

        upload_result = cloudinary.uploader.upload(image_file)
        item.image_url = upload_result.get("secure_url")

    item.save()

    serializer = ItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@authentication_classes([])
def delete_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)

    if item.image_url:
        public_id = get_public_id_from_url(item.image_url)
        if public_id:
            cloudinary.uploader.destroy(public_id)

    if item.qr_code_url:
        qr_public_id = get_public_id_from_url(item.qr_code_url)
        if qr_public_id:
            cloudinary.uploader.destroy(qr_public_id)

    item.delete()

    return Response(
        {"message": "Item and images deleted successfully"},
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@authentication_classes([])
def toggle_item_lost(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)

    if item.status == "lost":
        item.status = "found"
    elif item.status == "found":
        item.status = "lost"
    elif item.status == "pending":
        return Response({"error": "Cannot toggle while item is pending"}, status=400)
    item.save()

    return Response({"message": "Status updated", "status": item.status}, status=200)


@api_view(["GET"])
@authentication_classes([])
def get_lost_items(request):
    owner_id = request.query_params.get("owner_id")

    if not owner_id:
        return Response(
            {"error": "owner_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    items = Item.objects.filter(owner_id=owner_id, status="lost").order_by(
        "-created_at"
    )

    serializer = ItemSerializer(items, many=True)

    return Response(
        {
            "count": items.count(),
            "items": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([])
def filter_items(request):
    owner_id = request.query_params.get("owner_id")
    status_param = request.query_params.get("status")

    if not owner_id:
        return Response(
            {"error": "owner_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    queryset = Item.objects.filter(owner_id=owner_id)

    if status_param:
        queryset = queryset.filter(status=status_param)

    queryset = queryset.order_by("-created_at")

    serializer = ItemSerializer(queryset, many=True)

    return Response(
        {
            "count": queryset.count(),
            "items": serializer.data,
        },
        status=status.HTTP_200_OK,
    )
