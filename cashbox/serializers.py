from django.contrib.auth import get_user_model
from fcm_django.models import FCMDevice
from rest_framework import serializers

from accounts.models import User, Notification
from video.models import Video
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
        fields = ['id', 'sender', 'receiver', 'amount', 'code','create_at', 'is_paid',
                  'is_read']


class CashBoxHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CashBox
        fields = ['id', 'method', 'operator', 'props_number', 'amount',
                  'is_paid', 'create_at', 'user']


class UpdateTransferReadSerializer(serializers.ModelSerializer):
    transfer_id = serializers.IntegerField(required=True)
    read = serializers.BooleanField(default=False)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Transfer
        fields = ['transfer_id', 'user_id', 'read']


class CreateDonateTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonateTransfer
        fields = ['amount']


class CreateDonateForCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = DonateTransfer
        fields = ['amount']

    def validate(self, attrs):
        request = self.context.get('request')
        if request.user.profile.balance < attrs['amount']:
            raise serializers.ValidationError({
                'amount': 'In your balance does not enough'
                          ' this amount for transfer'
            })
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        user.profile.balance -= float(validated_data.get('amount'))
        user.profile.withdrawn_balance += float(validated_data.get('amount'))
        user.profile.save()
        nz_club = User.objects.get(username='nz_club')
        nz_club.profile.balance += float(validated_data.get('amount'))
        nz_club.profile.save()
        transfer = DonateTransfer.objects.create(sender=user, receiver=nz_club,
                                                 amount=validated_data.get(
                                                     'amount'))
        device = FCMDevice.objects.filter(user=nz_club)
        device.send_message(title="Перевод💰",
                            body="Пользователь " + user.username + " отправил(а) вам " + str(
                                request.data[
                                    'amount']),
                            icon=settings.GLOBAL_HOST + nz_club.profile.image.url)
        Notification.objects.create(user=nz_club, title="Перевод💰",
                                    body="Пользователь " + user.username + " отправил(а) вам " + str(
                                        request.data[
                                            'amount']),
                                    image=settings.GLOBAL_HOST + nz_club.profile.image.url)
        return transfer
