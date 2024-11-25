from django.urls import path
from . import views


app_name = "api_v1"

urlpatterns = [
    path("registration/", views.RegistrationApiView.as_view(), name="registration"),
    path("login/", views.LoginApiView.as_view(), name="login"),
]
