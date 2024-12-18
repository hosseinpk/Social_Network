from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            User.objects.get(Q(email=username) | Q(username=username))
        except User.DoesNotExist:
            return None
        # return super().authenticate(request, username, password, **kwargs)

    def user_can_authenticate(self, user):
        return user.is_active

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
