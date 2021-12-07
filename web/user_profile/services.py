from django.conf import settings
from django.contrib.auth import get_user_model

from main.services import MainService

User = get_user_model()


class UserProfileService:
    @staticmethod
    def get_user_queryset():
        return User.objects.filter(is_active=True, is_staff=False, is_superuser=False, )
        # return User.objects.all()

    @staticmethod
    def get_user_profile_queryset(user_id):
        return User.objects.filter(id=user_id, )