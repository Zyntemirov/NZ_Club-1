from django.urls import include, path

from .views import *

urlpatterns = [
    path("create/fcm", FcmCreateView.as_view(), name="fcm-create"),
    path("all-profiles", UserProfileListCreateView.as_view(),
         name="all-profiles"),
    path("profile/detail/<int:pk>", UserProfileDetailView.as_view(),
         name="profile"),
    path('update_profile/<int:pk>/', UpdateProfileView.as_view(),
         name='auth_update_profile'),
    # path("activate_user_by_email_code", ActivateUserWithEmailCodeView.as_view(), name="activate-email"),
    # path("reset_password_by_email_code", ResetPasswordWithEmailCodeView.as_view(), name="reset-password"),
    # path("check_activation_user", CheckActivationUserView.as_view(), name="check-activation")
    #############################NEW URLS##########################################
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('registration/', RegisterView.as_view(), name='registration'),
    path('activation/', UserActivationView.as_view(), name='user_activation'),
    path('password_reset/', RequestResetPasswordView.as_view(),
         name='password_reset'),
    path('set_new_password/', SetNewPasswordView.as_view(),
         name='set_new_password'),
    path('change_password/<int:pk>/', ChangePasswordView.as_view(),
         name='change_password'),
    path('region_list/', RegionListView.as_view(), name='region_list'),

    # PAYMENT
    path('pay24/check/', CheckPaymentView.as_view(), name='payment_check'),
    path('pay24/pay/', PayPaymentView.as_view(), name='payment_pay'),
    path('withdrawal/', WithdrawalView.as_view(), name='withdrawal'),
    path('withdrawal/history/', WithdrawalHistoryView.as_view(),
         name='withdrawal_history'),
    # Notification
    path('notification/', NotificationAPIView.as_view(), name='notification'),
    path('notification/delete/<int:pk>/', NotificationDeleteView.as_view(),
         name='notification_delete'),
    path('company/detail/', CompanyDetail.as_view(), name='company_detail'),
]
