from django.urls import path
from .views import *

urlpatterns = [
    path('create/transfer/to_another', CreateTransferView.as_view()),
    path('create/cash_box', CreateCashBoxView.as_view()),
    path('create/promo_code', CreatePromoCodeView.as_view()),
    path('transfer/receive', ReceiveTransferView.as_view()),
    path('transfer/history/<int:user_id>/<str:from_date>/<str:before_date>',
         TransferHistoryUserView.as_view()),
    path('cash_box/history/<int:user_id>/<str:from_date>/<str:before_date>',
         CashBoxHistoryUserView.as_view()),
    path('transfer/notification/<int:user_id>',
         TransferNotificationUserView.as_view()),
    path('agent/promo_codes/<int:user_id>', AgentPromoCodesView.as_view()),
    path('transfer/update/read', UpdateTransferReadView.as_view()),
    path('donate_transfer/video/', CreateDonateTransferView.as_view()),
    path('donate_transfer/company/', CreateDonateForCompanyView.as_view())
]
