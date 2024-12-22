from django.urls import path, include
from . import views

app_name = "api_v1"

urlpatterns = [
    path("post/", views.PostApiView.as_view(), name="creat_post"),
    path("post/<int:id>/", views.GetPostDetailsApiView.as_view(), name="postdetails"),
    path("post/<int:id>/comment/", views.CommentApiView.as_view(), name="comment"),
    path(
        "post/<int:id>/comment/<int:comment_id>/",
        views.CommentDetailApiView.as_view(),
        name="comment_details",
    ),
    path(
        "<slug:slug>/posts/", views.OtherUserPostApiView.as_view(), name="otherprofile"
    ),
    path("post/<int:id>/like/", views.LikeApiView.as_view(), name="like"),
    path(
        "post/<int:id>/like/<int:like_id>/",
        views.LikeDetailApiView.as_view(),
        name="like",
    ),
]
