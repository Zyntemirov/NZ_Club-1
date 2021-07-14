from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User, userProfile


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        user = User.objects.get_or_create(email='admin@admin.com', phone="996558779117")[0]
        user.set_password('1')
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.save()
        user_profile = userProfile.objects.get_or_create(user=user, region=7)[0]
        user_profile.save()
