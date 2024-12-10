from rest_framework.permissions import BasePermission
from posts.models import Post
from accounts.models import Profile
from django.shortcuts import get_object_or_404


class IsPostOwnser(BasePermission):

    def has_object_permission(self, request, view, obj):

        return obj.author.user == request.user


class CanCommentOnPost(BasePermission):

    def has_permission(self, request, view):

        post = get_object_or_404(Post, id=view.kwargs["id"])
        profile = post.author

        if not post.allowed_comment:
            return False

        if not profile.private:
            return True

        if profile.follower.filter(user=request.user).exists():
            return True

        return False
