from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from fcm_django.models import FCMDevice

from accounts.models import User, Notification
from .models import Video, MyVideo, Comment


@receiver(pre_save, sender=Video)
def video_pre_save_receiver(sender, instance, *args, **kwargs):
    if instance.id != None:
        old_instance = Video.objects.get(id=instance.id)
        if old_instance.is_active == False and (
                old_instance.status == '1' or old_instance.status == '3') and instance.is_active == True and instance.status == '2':
            try:
                devices = FCMDevice.objects.all()
                Notification.objects.bulk_create(
                    [Notification(user=device.user, title="Новое видео🔥",
                                  video=old_instance,
                                  body="Кликните сюда чтобы посмотреть видео " + instance.title,
                                  image=old_instance.image) for device in
                     devices])
                devices.send_message(title="Новое видео🔥",
                                     body="Кликните сюда чтобы посмотреть видео " + instance.title)
            except FCMDevice.DoesNotExist:
                pass


@receiver(post_save, sender=MyVideo)
def my_video_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created:
        if instance.is_active == True and instance.status == '3':
            try:
                users = User.objects.filter(
                    Q(profile__balance_lt=10) | Q(profile__withdrawn_balance=0))
                devices = FCMDevice.objects.filter(user__in=users)
                devices.send_message(title="Новое видео🔥",
                                     body="Кликните сюда чтобы посмотреть видео " + instance.title)
                Notification.objects.bulk_create(
                    [Notification(user=device.user, title="Новое видео🔥",
                                  video=instance,
                                  body="Кликните сюда чтобы посмотреть видео " + instance.title,
                                  image=instance.image) for device in devices])
            except:
                pass
    else:
        pass


@receiver(post_save, sender=Comment)
def comment_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created:
        comment = Comment.objects.get(id=instance.id)
        if comment.parent:
            comment_parent = Comment.objects.get(id=comment.parent_id)
            devices = FCMDevice.objects.filter(user=comment_parent.user)
            devices.send_message(title="Ответ на комментарий",
                                 body="Вам ответили на комментарий " +
                                      comment.text[:10] + "...")
            Notification.objects.create(user=comment_parent.user,
                                        video=comment.video,
                                        title="Ответ на комментарий",
                                        body="Вам ответили на комментарий " +
                                             comment.text[:10] + "...")
