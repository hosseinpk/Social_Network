from rest_framework.permissions import BasePermission


class IsPostOwnser(BasePermission):

    def has_object_permission(self, request, view, obj):

        return obj.author.user == request.user
