from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.contrib import auth
from rest_framework_simplejwt.tokens import RefreshToken

from .models import userProfile, User
from django.contrib.auth import get_user_model, authenticate
from fcm_django.models import FCMDevice
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import (AuthenticationFailed, ValidationError)
from rest_framework_simplejwt.serializers import (PasswordField, TokenRefreshSerializer as BaseRefreshSerializer)
from rest_framework_simplejwt.settings import api_settings


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


############################## USER AUTHORIZATION #########################

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


class LoginSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=256, min_length=10)
    password = serializers.CharField(max_length=256, write_only=True)
    refresh = serializers.SerializerMethodField('get_refresh_token')
    access = serializers.SerializerMethodField('get_access_token')
    user_info = serializers.SerializerMethodField('get_user_info')

    class Meta:
        model = User
        fields = ['phone', 'password', 'refresh', 'access', 'user_info']

    def get_user_info(self, obj):
        user = User.objects.get(phone=obj['phone'])
        user_profile = userProfile.objects.get(user=user)
        return {
            'region': str(user_profile.get_region_display()),
            'gender': str(user_profile.gender)
        }

    def get_refresh_token(self, obj):
        user = User.objects.get(phone=obj['phone'])
        return user.tokens()['refresh']

    def get_access_token(self, obj):
        user = User.objects.get(phone=obj['phone'])
        return user.tokens()['access']

    def validate(self, attrs):
        phone = attrs.get('phone', '')
        password = attrs.get('password', '')
        user = auth.authenticate(phone=phone, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        return {'phone': user.phone, 'tokens': user.tokens()}


class SetNewPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    code = serializers.CharField(max_length=4, required=True)
    password = serializers.CharField(write_only=True, min_length=1, required=True)
    password2 = serializers.CharField(write_only=True, min_length=1, required=True)

    class Meta:
        fields = ['phone', 'code', 'password', 'password2']

    def validate(self, attrs):
        try:
            phone = attrs.get('phone', '')
            password = attrs.get('password', '')
            password2 = attrs.get('password2', '')
            code = attrs.get('code', '')
            user = User.objects.get(phone=phone)
            if code != user.otp:
                raise AuthenticationFailed('Code is incorrect')
            if password == password2:
                user.set_password(password)
                user.save()
            elif password != password2:
                raise AuthenticationFailed('Password is not match')
        except User.DoesNotExist:
            raise AuthenticationFailed('User is not exists')
        return super().validate(attrs)
