from django.urls import path,include

app_name="posts"

urlpatterns = [path("api/v1/",include("posts.api.v1.urls"))]
