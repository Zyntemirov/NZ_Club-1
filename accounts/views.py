from random import randint, choices
from string import ascii_letters
from django.db import transaction
from django.db.models import F
from rest_framework_xml.parsers import XMLParser
from .renders import MyXMLRenderer
from django.utils.http import urlsafe_base64_decode
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenViewBase
from .permissions import IsOwnerProfileOrReadOnly
from .serializers import *
from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from rest_framework.response import Response
from rest_framework import status
from fcm_django.models import FCMDevice

from .tasks import process_withdrawal
from .utils import send_message_code
from datetime import date


class UserProfileListCreateView(ListAPIView):
    queryset = userProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class UserProfileDetailView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerProfileOrReadOnly, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = userProfile.objects.all()
        user_profile = get_object_or_404(queryset, user_id=kwargs['pk'])
        serializer = self.get_serializer(user_profile)
        return Response(
            {'data': serializer.data, 'phone': user_profile.user.phone},
            status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        queryset = userProfile.objects.all()
        user_profile = get_object_or_404(queryset, user_id=kwargs['pk'])
        if user_profile:
            serializer = self.get_serializer(user_profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ActivateUserWithEmailCodeView(UpdateAPIView):
    serializer_class = ActivateUserSerializer

    def update(self, request, *args, **kwargs):
        uid = force_text(urlsafe_base64_decode(request.data['code']))
        user = get_user_model().objects.get(pk=uid)
        if request.data['email'] == user.email:
            user.is_active = True
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordWithEmailCodeView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer

    def update(self, request, *args, **kwargs):
        uid = force_text(urlsafe_base64_decode(request.data['code']))
        user = get_user_model().objects.get(pk=uid)
        if request.data['email'] == user.email:
            validate_password(request.data['new_password'])
            user.set_password(request.data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CheckActivationUserView(UpdateAPIView):
    serializer_class = CheckActivationUserSerializer

    def update(self, request, *args, **kwargs):
        username = request.data['username']
        user = get_user_model().objects.get(username=username)
        if user.is_active:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class FcmCreateView(UpdateAPIView):
    serializer_class = FcmCreateSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = get_user_model().objects.get(id=request.data['user'])
        if user:
            try:
                fcm = FCMDevice.objects.get(user=request.data['user'])
                fcm.registration_id = request.data['registration_id']
                fcm.type = request.data['type']
                fcm.active = request.data['active']
                fcm.save()
            except FCMDevice.DoesNotExist:
                FCMDevice.objects.create(
                    user=user,
                    name=request.data['name'],
                    device_id=request.data['device_id'],
                    registration_id=request.data['registration_id'],
                    type=request.data['type'],
                )

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = []

    def post(self, reqeust, *args, **kwargs):
        serializer = self.serializer_class(data=reqeust.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        code = str(randint(1000, 9999))
        id = f'{randint(1000, 9999)}{code}{"".join(choices(ascii_letters, k=4))}'
        phone = self.request.data.get('phone', '')
        birth_date = (self.request.data.get('birth_date', '')).split('-')
        int_time = [int(i) for i in birth_date]
        date_time = date(int_time[0], int_time[1], int_time[2])
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            sms_resp = send_message_code(id, code, phone)
            user = User.objects.get(phone=phone)
            user.otp = code
            user.save()
            userProfile.objects.create(user=user,
                                       birth_date=date_time)
            return Response(
                {'phone': serializer.data.get('phone'), 'message': sms_resp},
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActivationView(GenericAPIView):
    permission_classes = []

    def put(self, request, *args, **kwargs):
        code = request.data.get('code', '')
        phone = request.data.get('phone', '')
        user = User.objects.get(phone=phone)
        if code:
            if code == user.otp:
                user.is_active = True
                user.save()
                return Response({'detail': 'User is successfully activated'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Code is incorrect'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Enter code'},
                            status=status.HTTP_400_BAD_REQUEST)


class RequestResetPasswordView(GenericAPIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        code = str(randint(1000, 9999))
        id = f'{randint(1000, 9999)}{code}{"".join(choices(ascii_letters, k=4))}'
        phone = request.data.get('phone', '')
        if phone:
            try:
                user = User.objects.get(phone=phone)
                user.otp = code
                send_message_code(id, code, phone)
                user.save()
                return Response({'phone': user.phone,
                                 'message': 'We sent you reset SMS. Please check the message and enter the code'},
                                status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(
                    {'detail': 'User with this phone number does not exists.'},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Enter phone number'},
                            status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = []

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password reset success'},
                        status=status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer


class TokenObtainPairView(TokenViewBase):
    serializer_class = TokenPairObtainSerializer


class TokenRefreshView(TokenViewBase):
    serializer_class = TokenPairRefreshSerializer


class CheckPaymentView(GenericAPIView):
    parser_classes = [XMLParser]
    renderer_classes = [MyXMLRenderer]

    def get(self, request, *args, **kwargs):
        command = request.query_params.get('command', '')
        phone = request.query_params.get('account', '')
        if command == 'check':
            try:
                user = User.objects.get(phone=phone)
                return Response({'result': 0, 'account': user.username})
            except User.DoesNotExist:
                return Response({'result': 5})
        return Response({'result': 'Command is not correct'})


class PayPaymentView(GenericAPIView):
    parser_classes = [XMLParser]
    renderer_classes = [MyXMLRenderer]

    def get(self, request, format=None):
        command = request.query_params.get('command', '')
        phone = request.query_params.get('account', '')
        sum = float(request.query_params.get('sum', ''))
        if command == 'pay':
            try:
                user = User.objects.get(phone=phone)
                user_profile = userProfile.objects.get(user=user)
                user_profile.balance = F('balance') + (sum)
                devices = FCMDevice.objects.filter(user=user)
                devices.send_message(title="При пополнении счета",
                                     body=f"Успешно пополено на сумму “{sum}” через Pay24.")
                Notification.objects.create(user=user,
                                            title="При пополнении счета",
                                            body=f"Успешно пополено на сумму “{sum}” через Pay24.",
                                            image=user_profile.image)
                user_profile.save()
                return Response({'result': 0})
            except User.DoesNotExist:
                return Response({'result': 5})
        return Response({'result': 'Command is not correct'})


class WithdrawalView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return WithdrawalListSerializer if self.request.method == 'GET' else WithdrawalCreateSerializer

    def get_queryset(self):
        return self.request.user.withdrawal_set.filter(status='successful')

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                try:
                    request.data._mutable = True
                except AttributeError:
                    pass
                user = User.objects.select_for_update().get(id=request.user.id)
                request.data.update({'user': request.user.id})
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                if user.profile.balance >= serializer.validated_data.get(
                        'amount'):
                    user.profile.balance -= serializer.validated_data.get(
                        'amount')
                    user.profile.withdrawn_balance += serializer.validated_data.get(
                        'amount')
                    user.profile.save()
                    headers = self.get_success_headers(serializer.data)
                    return Response(serializer.data, status.HTTP_201_CREATED,
                                    headers=headers)
                else:
                    return Response({'error': 'Your balance is not enough'})
        except InterruptedError as e:
            return Response({'error': ('Insufficient funds')},
                            status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({'error': e.args}, status.HTTP_400_BAD_REQUEST)


class WithdrawalBulkView(GenericAPIView):
    def get_serializer_class(self):
        return WithdrawBulkSerializer if self.request.method == 'POST' else WithdrawalBulkUpdateSerializer

    def get_queryset(self):
        return Withdrawal.objects.filter(status='unprocessed')

    def post(self, request):
        data = self.get_serializer(self.get_queryset(), many=True).data
        return Response(data, status.HTTP_200_OK)

    def put(self, request):
        this_srz = self.get_serializer(data=request.data)
        this_srz.is_valid(raise_exception=True)
        process_withdrawal.delay(this_srz.vaidated_data['error'],
                                 status='error')
        process_withdrawal.delay(this_srz.vaidated_data['successful'],
                                 status='successful')
        return Response({'message': 'IDs successfully processed'},
                        status.HTTP_200_OK)


class NotificationAPIView(GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification

    def get(self, request, *args, **kwargs):
        queryset = Notification.objects.filter(user=request.user)
        serializers = self.serializer_class(queryset, many=True,
                                            context={'request': request})
        return Response(serializers.data, status.HTTP_200_OK)


class NotificationDeleteView(GenericAPIView):
    def delete(self, request, *args, **kwargs):
        notification = Notification.objects.get(pk=kwargs['pk'])
        notification.delete()
        return Response({'detail': 'Удалено'}, status.HTTP_204_NO_CONTENT)


class RegionListView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        region_list = {'1': 'Ош', '2': 'Ысык-Кол', '3': 'Жалал-Абад',
                       '4': 'Талас', '5': 'Баткен', '6': 'Нарын', '7': 'Чуй',
                       '8': 'Бишкек'}
        return Response(region_list)


class WithdrawalHistoryView(ListAPIView):
    serializer_class = WithdrawalHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Withdrawal.objects.filter(user=self.request.user)
        return queryset


class CompanyDetail(GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(username='nz_club')
            return Response({'balance': user.profile.balance},
                            status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({}, status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(UpdateAPIView):
    queryset = userProfile.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateProfileSerializer