from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *
from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image')

    def get_image(self, user):
        return settings.GLOBAL_HOST + user.profile.image.url

    class Meta:
        model = get_user_model()
        ref_name = 'comment.user'
        fields = ['id', 'username', 'email', 'image']


class CreateCashBoxSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = CashBox
        fields = ['user_id', 'method', 'operator', 'props_number', 'amount']


class CreateTransferSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = Transfer
        fields = ['user_id', 'username', 'amount', 'code']


class CreatePromoCodeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = PromoCode
        fields = ['user_id', 'code']


class ReceiveTransferSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)

    class Meta:
        model = Transfer
        fields = ['username', 'code']


class AgentPromoCodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'
        depth = 1


class TransferHistorySerializer(serializers.ModelSerializer):
    sender = UserSerializer()

    class Meta:
        model = Transfer
        fields = ['id', 'sender', 'receiver', 'amount', 'create_at', 'is_paid', 'is_read']


class CashBoxHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CashBox
        fields = ['id', 'method', 'operator', 'props_number', 'amount', 'is_paid', 'create_at', 'user']


class UpdateTransferReadSerializer(serializers.ModelSerializer):
    transfer_id = serializers.IntegerField(required=True)
    read = serializers.BooleanField(default=False)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Transfer
        fields = ['transfer_id', 'user_id', 'read']
