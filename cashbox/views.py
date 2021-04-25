from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.views import APIView

from accounts.models import Notification
from .serializers import *
from .models import *
from rest_framework.generics import *
from datetime import date
from fcm_django.models import FCMDevice
from django.conf import settings


# update put, patch API
class CreateCashBoxView(viewsets.generics.UpdateAPIView):
    serializer_class = CreateCashBoxSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = get_user_model().objects.get(id=request.data['user_id'])
        if user:
            profile = user.profile

            if profile.balance < request.data['amount']:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            profile.balance = profile.balance - request.data['amount']
            profile.withdrawn_balance = profile.withdrawn_balance + \
                                        request.data['amount']
            profile.save()

            CashBox.objects.create(
                user=user,
                method=request.data['method'],
                operator=request.data['operator'],
                props_number=request.data['props_number'],
                amount=request.data['amount'],
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateTransferView(viewsets.generics.UpdateAPIView):
    serializer_class = CreateTransferSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = get_user_model().objects.get(id=request.data['user_id'])
        if user:
            profile = user.profile
            if profile.balance < float(request.data['amount']):
                return Response(status=status.HTTP_400_BAD_REQUEST)

            profile.balance = profile.balance - request.data['amount']
            profile.save()

            Transfer.objects.create(
                sender=user,
                receiver=request.data['username'],
                code=request.data['code'],
                amount=request.data['amount'],
            )

            receiver = get_user_model().objects.get(
                username=request.data['username'])
            device = FCMDevice.objects.filter(user=receiver)
            device.send_message(title="Перевод💰",
                                body="Пользователь " + user.username + " отправил(а) вам " + str(
                                    request.data[
                                        'amount']) + " баллов. Введите код чтобы получить перевод.",
                                icon=settings.GLOBAL_HOST + profile.image.url)
            Notification.objects.create(user=user, title="Перевод💰",
                                        body="Пользователь " + user.username + " отправил(а) вам " + str(
                                            request.data[
                                                'amount']) + " баллов. Введите код чтобы получить перевод.",
                                        image=settings.GLOBAL_HOST + profile.image.url)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CreatePromoCodeView(viewsets.generics.UpdateAPIView):
    serializer_class = CreatePromoCodeSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = get_user_model().objects.get(id=request.data['user_id'])
        print(user.profile.agent)
        if user.profile.agent:
            PromoCode.objects.create(
                user=user,
                code=request.data['code'],
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ReceiveTransferView(viewsets.generics.UpdateAPIView):
    serializer_class = ReceiveTransferSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        transfer = Transfer.objects.filter(
            receiver=request.data['username']).filter(
            code=request.data['code']).filter(
            is_paid=False).first()
        user = get_user_model().objects.get(username=request.data['username'])
        if transfer and user:
            transfer.is_paid = True
            transfer.save()
            profile = user.profile
            profile.balance = profile.balance + transfer.amount
            profile.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TransferHistoryUserView(viewsets.generics.ListAPIView):
    serializer_class = TransferHistorySerializer

    def get_queryset(self):
        user = get_user_model().objects.get(id=self.kwargs['user_id'])
        if user:
            queryset = Transfer.objects.filter(
                Q(sender=self.kwargs['user_id']) | Q(
                    receiver=user.username)).filter(
                create_at__gte=self.kwargs['from_date'],
                create_at__lte=self.kwargs['before_date'])
            return queryset
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CashBoxHistoryUserView(viewsets.generics.ListAPIView):
    serializer_class = CashBoxHistorySerializer

    def get_queryset(self):
        user = get_user_model().objects.get(id=self.kwargs['user_id'])
        if user:
            queryset = CashBox.objects.filter(user=self.kwargs['user_id'],
                                              create_at__gte=self.kwargs[
                                                  'from_date'],
                                              create_at__lte=self.kwargs[
                                                  'before_date'])
            return queryset
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TransferNotificationUserView(viewsets.generics.ListAPIView):
    serializer_class = TransferHistorySerializer

    def get_queryset(self):
        user = get_user_model().objects.get(id=self.kwargs['user_id'])
        if user:
            queryset = Transfer.objects.filter(receiver=user.username).order_by(
                'is_read', 'create_at').reverse()
            return queryset
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class AgentPromoCodesView(viewsets.generics.ListAPIView):
    serializer_class = AgentPromoCodesSerializer

    def get_queryset(self):
        user = get_user_model().objects.get(id=self.kwargs['user_id'])
        if user.profile.agent:
            queryset = PromoCode.objects.filter(user=user)
            return queryset
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdateTransferReadView(viewsets.generics.UpdateAPIView):
    serializer_class = UpdateTransferReadSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = get_user_model().objects.get(id=request.data['user_id'])
        transfer = Transfer.objects.filter(id=request.data['transfer_id'],
                                           receiver=user.username).first()
        if transfer and request.data['read']:
            transfer.is_read = True
            transfer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateDonateTransferView(APIView):
    serializer_class = CreateDonateTransferSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        video = Video.objects.get(id=request.data['video_id'])
        if user:
            if user.profile.balance < float(request.data['amount']):
                return Response({'amount': 'In your balance does not enough'
                                           ' this amount for transfer'},
                                status.HTTP_400_BAD_REQUEST)
            user.profile.balance -= float(request.data['amount'])
            video.owner.profile.balance += float(request.data['amount'])
            user.profile.save()
            video.owner.profile.save()
            DonateTransfer.objects.create(sender=user, receiver=video.owner,
                                          amount=request.data['amount']
                                          )
            device = FCMDevice.objects.filter(user=video.owner)
            device.send_message(title="Перевод💰",
                                body="Пользователь " + user.username + " отправил(а) вам " + str(
                                    request.data[
                                        'amount']),
                                icon=settings.GLOBAL_HOST + user.profile.image.url)
            Notification.objects.create(user=video.owner, title="Перевод💰",
                                        body="Пользователь " + user.username + " отправил(а) вам " + str(
                                            request.data[
                                                'amount']),
                                        image=settings.GLOBAL_HOST + video.owner.profile.image.url)
            return Response(status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)


class CreateDonateForCompanyView(viewsets.generics.CreateAPIView):
    serializer_class = CreateDonateForCompanySerializer
    permission_classes = [IsAuthenticated]
