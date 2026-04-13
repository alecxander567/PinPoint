import cloudinary.uploader
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from items.models import Item
from .models import Report
from .serializers import ReportSerializer
from core.notifications import notify_owner
from core.notifications import notify_owner


def get_public_id_from_url(url):
    try:
        if "upload/" in url:
            path_after_upload = url.split("upload/")[1]
            public_id = path_after_upload.split(".")[0]
            return public_id
        return None
    except Exception:
        return None


@api_view(["POST"])
@authentication_classes([])
def submit_report(request):
    """Submit a report for a found item"""
    item_id = request.data.get("item_id")
    landmark_image = request.FILES.get("landmark_image")
    location = (request.data.get("location") or "").strip()
    message = (request.data.get("message") or "").strip()

    if not all([item_id, location, message]):
        return Response(
            {"error": "item_id, location, and message are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not landmark_image:
        return Response(
            {"error": "A landmark image is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response(
            {"error": "Item not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    landmark_image_url = ""
    if landmark_image:
        upload_result = cloudinary.uploader.upload(landmark_image)
        landmark_image_url = upload_result.get("secure_url", "")

    report = Report.objects.create(
        item=item,
        landmark="",
        landmark_image_url=landmark_image_url,
        location=location,
        message=message,
    )

    item.status = "pending"
    item.save()

    notify_owner(item)

    serializer = ReportSerializer(report)
    data = serializer.data
    data["owner_view_url"] = f"{settings.FRONTEND_URL}/report/view/{report.view_token}"
    return Response(data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@authentication_classes([])
def get_owner_reports(request):
    owner_id = request.query_params.get("owner_id")
    if not owner_id:
        return Response(
            {"error": "owner_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    reports = Report.objects.filter(
        item__owner_id=owner_id, is_resolved=False
    ).select_related("item")

    serializer = ReportSerializer(reports, many=True)
    return Response(
        {"count": reports.count(), "reports": serializer.data},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([])
def get_item_reports(request, item_id):
    """Get all reports for a specific item"""
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response(
            {"error": "Item not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    reports = Report.objects.filter(item=item)
    serializer = ReportSerializer(reports, many=True)

    return Response(
        {"count": reports.count(), "reports": serializer.data},
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@authentication_classes([])
def delete_owner_reports(request):
    """Delete one or more reports belonging to the owner's items."""
    owner_id = request.data.get("owner_id")
    report_ids = request.data.get("report_ids") or []

    if not owner_id:
        return Response(
            {"error": "owner_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not report_ids or not isinstance(report_ids, list):
        return Response(
            {"error": "report_ids must be a non-empty list"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    reports = Report.objects.filter(id__in=report_ids, item__owner_id=owner_id)

    if not reports.exists():
        return Response(
            {"error": "No matching reports found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    deleted_count = reports.count()
    for report in reports:
        if report.landmark_image_url:
            public_id = get_public_id_from_url(report.landmark_image_url)
            if public_id:
                cloudinary.uploader.destroy(public_id)

    reports.delete()

    return Response(
        {"message": "Reports deleted successfully", "deleted_count": deleted_count},
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@authentication_classes([])
def resolve_report(request, report_id):
    try:
        report = Report.objects.select_related("item").get(id=report_id)
    except Report.DoesNotExist:
        return Response({"error": "Report not found"}, status=404)

    report.is_resolved = True
    report.save()

    item = report.item
    item.status = "found"
    item.save()

    return Response(
        {
            "message": "Report resolved, item marked as found",
            "item_status": item.status,
        },
        status=200,
    )


@api_view(["GET"])
@authentication_classes([])
def get_resolved_reports(request):
    owner_id = request.query_params.get("owner_id")

    if not owner_id:
        return Response(
            {"error": "owner_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    reports = (
        Report.objects.filter(item__owner_id=owner_id, is_resolved=True)
        .select_related("item")
        .order_by("-id")
    )

    serializer = ReportSerializer(reports, many=True)

    return Response(
        {
            "count": reports.count(),
            "reports": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([])
def get_report_by_token(request, token):
    try:
        report = Report.objects.select_related("item").get(view_token=token)
    except Report.DoesNotExist:
        return Response({"error": "Report not found"}, status=404)

    serializer = ReportSerializer(report)
    return Response(serializer.data)
