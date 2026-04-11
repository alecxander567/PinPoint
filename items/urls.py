from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_item, name="add_item"),
    path("list/", views.get_user_items, name="get_user_items"),
    path("<uuid:item_id>/", views.get_item_detail, name="get_item_detail"),
    path("<uuid:item_id>/update/", views.update_item),
    path("<uuid:item_id>/delete/", views.delete_item),
    path("<uuid:item_id>/toggle-lost/", views.toggle_item_lost),
    path("filter/", views.filter_items, name="filter_items"),
]
