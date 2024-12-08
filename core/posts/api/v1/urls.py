from django.urls import path, include
from . import views

app_name = "api_v1"

urlpatterns = [
    path("post/", views.CreatePostApiView.as_view(), name="creat_post"),
    path("post/<int:id>/", views.GetPostDetailsApiView.as_view(), name="postdetails"),
]
