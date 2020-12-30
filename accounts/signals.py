from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver

from .models import userProfile


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    if created:
        userProfile.objects.create(user=instance)
