from rest_framework import serializers
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
