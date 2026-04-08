from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_item, name="add_item"),
    path("list/", views.get_user_items, name="get_user_items"),
]
