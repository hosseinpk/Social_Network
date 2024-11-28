from django.urls import path
from . import views


app_name = "api_v1"

urlpatterns = [
    path("registration/", views.RegistrationApiView.as_view(), name="registration"),
    path("login/", views.LoginApiView.as_view(), name="login"),
    path(
        "verifyaccount/confirm/<str:token>/",
        views.ActivationApiview.as_view(),
        name="activation",
    ),
    path(
        "verifyaccount/resend/",
        views.ResendActivationApiview.as_view(),
        name="resend-activation",
    ),
    path(
        "resetpassword/<int:id>/",
        views.ResetPasswordApiview.as_view(),
        name="resetpassword",
    ),
    path(
        "forgetpassword/", views.ForgetpasswordApiView.as_view(), name="forgetpassword"
    ),
    path(
        "forgetpassword/resetpassword/<str:token>",
        views.ResetForgetpasswordApiView.as_view(),
        name="forgetpassword",
    ),
]
