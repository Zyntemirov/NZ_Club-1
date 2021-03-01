from random import randint, choices
from string import ascii_letters

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.password_validation import validate_password
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated

from .models import User
from .permissions import IsOwnerProfileOrReadOnly
from .serializers import *
from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from rest_framework.response import Response
from rest_framework import status
from fcm_django.models import FCMDevice

# Create your views here.
from .utils import send_message_code


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
        return Response(serializer.data)

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


class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        code = str(randint(1000, 9999))
        id = f'{randint(1000, 9999)}{code}{"".join(choices(ascii_letters, k=4))}'
        phone = self.request.data.get('phone', '')
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(otp=code)
            sms_resp = send_message_code(id, code, phone)
            return Response({'phone': serializer.data.get('phone'), 'message': sms_resp},
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
                return Response({'detail': 'User is successfully activated'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Code is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Enter code'}, status=status.HTTP_400_BAD_REQUEST)


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
                return Response({'detail': 'User with this phone number does not exists.'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Enter phone number'}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = []

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password reset success'}, status=status.HTTP_200_OK)
