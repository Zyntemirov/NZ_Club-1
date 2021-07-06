import PIL
from PIL import Image
from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_resized import ResizedImageField
from django.utils.safestring import mark_safe


class Stories(models.Model):
    video = models.CharField(max_length=255, null=True, verbose_name="Ютуб ссылка")
    url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='stories/', verbose_name="Обложка")
    views = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='stories_views')
    order = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Сторис")
        verbose_name_plural = _("Сторисы")
        ordering = ('order',)

    def __str__(self):
        return self.video

    def save(self, *args, **kwargs):
        try:
            this = Stories.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except:
            pass

        super(Stories, self).save(*args, **kwargs)
        img = Image.open(self.image)
        width, height = img.size
        if width > 1080:
            ratio = float(width / 1080)
            width = int(width / ratio)
            height = int(height / ratio)
            img = img.resize((width, height), PIL.Image.ANTIALIAS)
            img.save(self.image.path, quality=100, optimize=True)
        else:
            img.save(self.image.path, quality=100, optimize=True)


class LikeStories(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='like_stories',
                             verbose_name="Пользователь")
    stories = models.ForeignKey(Stories, on_delete=models.CASCADE, related_name='like_stories',
                                verbose_name="Сторис видео")
    create_at = models.DateTimeField(default=datetime.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = _("Лайк (Сторис)")
        verbose_name_plural = _("Лайк (Сторис)")
        unique_together = (('user', 'stories'),)


class ViewStories(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='stories',
                             verbose_name="Пользователь")
    stories = models.ForeignKey(Stories, on_delete=models.CASCADE,
                                related_name='stories',
                                verbose_name="Сторис видео")
    create_at = models.DateTimeField(default=datetime.now,
                                     verbose_name="Дата создания")

    class Meta:
        verbose_name = _("Просмотр история (Сторис)")
        verbose_name_plural = _("Просмотр истории (Сторис)")


class ComplaintStories(models.Model):
    TYPE_COMPLAINT = (
        ('1', '1'),
        ('2', '2'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='complaint_stories',
                             verbose_name="Пользователь")
    stories = models.ForeignKey(Stories, on_delete=models.CASCADE,
                                related_name='complaint_stories',
                                verbose_name="Сторис видео")
    type = models.CharField("Тип жалобы", choices=TYPE_COMPLAINT, max_length=2)
    text = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Жалоба (Сторис)")
        verbose_name_plural = _("Жалоба (Сторис)")
