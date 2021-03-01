from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import userProfile
from django.contrib.auth import get_user_model
from fcm_django.models import FCMDevice


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = userProfile
        fields = ['id', 'agent', 'gender', 'region', 'birth_date', 'image', 'balance', 'withdrawn_balance',
                  'view_count', 'image']


class ActivateUserSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True)

    class Meta:
        model = get_user_model()
        fields = ['code', 'email']


class ResetPasswordSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = get_user_model()
        fields = ['code', 'email', 'new_password']


class CheckActivationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username']


class FcmCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['phone', 'username', 'password']
        extra_kwargs = {'write_only': True}

    def validate_password(self, password):
        try:
            validate_password(password)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return password

    def create(self, validated_data):
        _user = get_user_model()
        user = _user.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user
