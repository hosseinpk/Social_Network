from django.urls import path
from .views import *

urlpatterns = [
    path("registration/", RegistrationApiView.as_view(), name="registration")
]
