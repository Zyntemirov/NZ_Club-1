from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from .models import userProfile, User
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
