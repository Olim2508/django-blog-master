from allauth.account.utils import setup_user_email
from dj_rest_auth.serializers import PasswordChangeSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.status import HTTP_400_BAD_REQUEST

from main.services import MainService
from src import settings
from actions.models import Follower
from . import models
from .choices import GenderChoice
from .models import Profile
from .services import UserProfileService

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    image = serializers.URLField(source='avatar_url')

    class Meta:
        model = Profile
        fields = ['gender', 'image', 'birthdate', 'bio', 'website']


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    subscribers = serializers.SerializerMethodField("get_subscribers_count")
    has_subscribed = serializers.SerializerMethodField("get_has_subscribed")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.update(rep.pop("profile", {}))
        return rep

    def get_subscribers_count(self, obj):
        return obj.subscribers_count()["count"]

    def get_has_subscribed(self, obj):
        try:
            Follower.objects.get(subscriber=self.context["request"].user,
                                 to_user=User.objects.get(pk=obj.pk))
            has_subscription = True
        except Follower.DoesNotExist:
            has_subscription = False

        return has_subscription

    class Meta:
        model = User
        fields = ['full_name', 'id', 'profile', "subscribers", "has_subscribed"]


class TrueUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep.update(rep.pop("profile", {}))
        return rep

    class Meta:
        model = User
        fields = ['full_name', 'id', 'profile']


class ChangePasswordSerializer(PasswordChangeSerializer):
    old_password = serializers.CharField()
    new_password1 = serializers.CharField(min_length=8)
    new_password2 = serializers.CharField(min_length=8)


class ChangeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['image']

    def validate(self, attrs):
        limit = 4 * 1024 * 1024  # 4 mb
        if attrs.get('image').size > limit:
            raise serializers.ValidationError('File too large. Size should not exceed 4 MiB.')
        return attrs


class UserShortInfoSerializer(serializers.ModelSerializer):
    image = serializers.URLField(source='avatar_url')
    profile = serializers.URLField(source='get_absolute_url')

    class Meta:
        model = User
        fields = ('id', 'full_name', 'image', 'profile')


class GetUsersIdSerializer(serializers.Serializer):
    user_id = serializers.ListField(child=serializers.IntegerField())

    def validate(self, attrs):
        users = set(models.User.objects.filter(pk__in=attrs['user_id']).values_list('id', flat=True))
        not_existed_users = set(attrs['user_id']).difference(users)
        errors = {user: "Not found" for user in not_existed_users}
        if errors:
            raise serializers.ValidationError(errors)
        return attrs
