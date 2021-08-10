from celery import shared_task
from django.utils.timezone import now
from fcm_django.models import FCMDevice

from .models import User, Withdrawal, Notification
import datetime

current_time = datetime.datetime.now()


@shared_task
def delete_no_active_user():
    users = User.objects.filter(is_active=False)
    for user in users:
        user.date_joined += datetime.timedelta(minutes=3)
        if user.date_joined.minute == now().minute:
            user.delete()
            return f'{user.phone} user is deleted'


@shared_task
def process_withdrawal(withdrawal_ids: list, status: str):
    if withdrawals := Withdrawal.objects.filter(id__in=withdrawal_ids):
        if status == 'error':
            for withdrawal in withdrawals:
                if withdrawal.status == 'unprocessed':
                    user = withdrawal.user
                    user.profile.withdrawn_balance -= withdrawal.amount
                    user.profile.balance += withdrawal.amount
                    user.profile.save()
                withdrawals.update(status='error')
        if status == 'successful':
            withdrawals = Withdrawal.objects.filter(
                id__in=withdrawal_ids).update(
                status='successful')
            for withdrawal in withdrawals:
                device = FCMDevice.objects.filter(user=withdrawal.user)
                device.send_message(title="При выводе средств",
                                    body=f"Успешно выведено баллов на сумму “{withdrawal.amount}” через “{withdrawal.get_method_display()}”")
                Notification.objects.create(user=withdrawal.user,
                                            title="При выводе средств",
                                            body=f"Успешно выведено баллов на сумму “{withdrawal.amount}” через “{withdrawal.get_method_display()}”")
            return f'{len(withdrawal_ids)} withdrawals processed successfully'
        return f'There is no withdrawals to be processed in this request'
