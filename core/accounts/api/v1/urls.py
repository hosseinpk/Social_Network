from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView

app_name = "api_v1"

profile_patterns = [
    path("", views.ProfileApiView.as_view(), name="own_profile"),
    path("<int:id>/", views.ProfileApiView.as_view(), name="profile_detail"),
    path(
        "<slug:slug>/followrequest/",
        views.FollowRequestApiView.as_view(),
        name="follow_request",
    ),
    path(
        "<slug:slug>/deletefollowrequest/",
        views.DeleteFollowRequestApiView.as_view(),
        name="delete_follow_request",
    ),
    path(
        "acceptrejectfollowrequest/<str:sign>/",
        views.AcceptOrRejectFollowRequestApiView.as_view(),
        name="accept_reject",
    ),
    path(
        "followrequest/",
        views.GetFollowRequestApiView.as_view(),
        name="get_follow_request",
    ),
    path(
        "<slug:slug>/unfollow/", views.RemoveFollowerApiView.as_view(), name="unfollow"
    ),
]

urlpatterns = [
    path("registration/", views.RegistrationApiView.as_view(), name="registration"),
    path("login/", views.LoginApiView.as_view(), name="login"),
    path('verifyotp/', views.OTPVerificationView.as_view(), name='verify-otp'),
    path("logout/", views.LogoutApiView.as_view(), name="logout"),
    path("verify/", TokenVerifyView.as_view(), name="verify"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path(
        "verifyaccount/confirm/<str:token>/",
        views.ActivationApiview.as_view(),
        name="activation",
    ),
    path(
        "verifyaccount/resend/",
        views.ResendActivationApiview.as_view(),
        name="resend_activation",
    ),
    path(
        "changepassword/<int:id>/",
        views.ResetPasswordApiview.as_view(),
        name="reset_password",
    ),
    path(
        "forgetpassword/", views.ForgetpasswordApiView.as_view(), name="forget_password"
    ),
    path(
        "forgetpassword/resetpassword/<str:token>/",
        views.ResetForgetpasswordApiView.as_view(),
        name="reset_forget_password",
    ),
    path("profile/", include(profile_patterns)),
]
