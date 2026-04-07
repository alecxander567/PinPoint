from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_item, name="add_item"),
]
