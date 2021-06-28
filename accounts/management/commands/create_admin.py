from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        user = User.objects.get_or_create(email='admin1234@admin.com',phone="996702059829")[0]
        user.set_password('admin1234')
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.save()
