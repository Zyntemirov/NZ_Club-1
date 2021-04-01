from django.db.models.signals import pre_save, post_save
from video.models import Video
from django.dispatch import receiver


@receiver(pre_save, sender=Video)
def video_pre_save_receiver(sender, instance, *args, **kwargs):
    pass


@receiver(post_save, sender=Video)
def video_post_save_receiver(sender, instance, *args, **kwargs):
    pass
