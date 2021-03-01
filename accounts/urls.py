from django.urls import include, path

from .views import *

urlpatterns = [
    path("create/fcm", FcmCreateView.as_view(), name="fcm-create"),
    path("all-profiles", UserProfileListCreateView.as_view(), name="all-profiles"),
    path("profile/detail/<int:pk>", UserProfileDetailView.as_view(), name="profile"),
    # path("activate_user_by_email_code", ActivateUserWithEmailCodeView.as_view(), name="activate-email"),
    # path("reset_password_by_email_code", ResetPasswordWithEmailCodeView.as_view(), name="reset-password"),
    # path("check_activation_user", CheckActivationUserView.as_view(), name="check-activation")
    #############################NEW URLS##########################################
    path('registration/', RegisterView.as_view(), name='registration'),
    path('activation/', UserActivationView.as_view(), name='user_activation'),
]
