from celery import shared_task
from django.db.models import F
from django.utils.timezone import now

from .models import User
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