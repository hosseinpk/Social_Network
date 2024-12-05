from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView


app_name = "api_v1"

urlpatterns = [
    path("registration/", views.RegistrationApiView.as_view(), name="registration"),
    path("login/", views.LoginApiView.as_view(), name="login"),
    path("logout", views.LogoutApiView.as_view(), name="logout"),
    path("verify/", TokenVerifyView.as_view(), name="verift"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
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
        "changepassword/<int:id>/",
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
    path("profile/", views.ProfileApiView.as_view(), name="profile"),
    path("profile/<int:id>/", views.ProfileApiView.as_view(), name="profile"),
    path(
        "profile/<slug:slug>/followrequest/",
        views.FollowRequestApiView.as_view(),
        name="followrequest",
    ),
    path(
        "profile/acceptrejectfollowrequest/<str:sign>/",
        views.AcceptOrRejectFollowRequestApiView.as_view(),
        name="accepreject",
    ),
    path(
        "profile/followrequest/",
        views.GetFollowRequestApiView.as_view(),
        name="getfollowrequest",
    ),
    path(
        "profile/<slug:slug>/unfollow/",
        views.RemoveFollowerApiView.as_view(),
        name="unfollow",
    ),
]
