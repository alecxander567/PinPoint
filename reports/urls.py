from django.urls import path
from . import views

urlpatterns = [
    path("submit/", views.submit_report, name="submit_report"),
    path("list/", views.get_owner_reports, name="get_owner_reports"),
    path("delete/", views.delete_owner_reports, name="delete_owner_reports"),
    path("<uuid:item_id>/list/", views.get_item_reports, name="get_item_reports"),
    path("<uuid:report_id>/resolve/", views.resolve_report),
    path("resolved/", views.get_resolved_reports, name="get_resolved_reports"),
    path("view/<uuid:token>/", views.get_report_by_token, name="get_report_by_token"),
]
