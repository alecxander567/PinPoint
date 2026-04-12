from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("profile/", views.get_profile, name="get_profile"),  # GET
    path("profile/update/", views.update_profile, name="update_profile"),
    path("profile/delete/", views.delete_account, name="delete_account"),
    path("bug-report/", views.report_bug, name="report_bug"),
]
