from django.conf import settings
from django.db import models
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django_resized import ResizedImageField
from django.utils.safestring import mark_safe

import PIL
from PIL import Image

from fcm_django.models import FCMDevice


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название")
    image = ResizedImageField(upload_to='category/', verbose_name='Фотография', size=[100, 100])

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")

    def image_tag(self):
        return mark_safe('<img src={} width="200" />'.format(self.image.url))

    image_tag.short_description = 'Фотография'

    def __str__(self):
        return self.title


class Video(models.Model):
    STATUS = (
        ('1', 'Отклонено'),
        ('2', 'Активно'),
        ('3', 'В ожидании')
    )
    TYPE = (
        ('1', 'Обычный'),
        ('2', 'Премиум'),
        ('3', 'Благотворительность'),
    )
    title = models.CharField(max_length=100, verbose_name="Название")
    text = models.TextField(verbose_name="Описание")
    phone_1 = models.CharField(max_length=16, null=True, blank=True, verbose_name="Телефон номер 1")
    phone_2 = models.CharField(max_length=16, null=True, blank=True, verbose_name="Телефон номер 2")
    phone_3 = models.CharField(max_length=16, null=True, blank=True, verbose_name="Телефон номер 3")
    instagram = models.CharField(max_length=50, null=True, blank=True, verbose_name="Инстаграм")
    facebook = models.CharField(max_length=50, null=True, blank=True, verbose_name="Файсбук")
    web_site = models.CharField(max_length=50, null=True, blank=True, verbose_name="Вебсайт")
    views = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='videos', verbose_name="Просмотров")
    watched_videos = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='watched_videos')
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favorites')
    # video = models.FileField(upload_to='media/videos/%Y/%m/%d/', verbose_name="Ютуб ссылка")
    video = models.CharField(max_length=255, null=True, verbose_name="Ютуб ссылка", help_text="Просмотр видео")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='videos', verbose_name="Категория")
    type = models.CharField(verbose_name="Тип", choices=TYPE, max_length=20)
    status = models.CharField("Статус", max_length=20, choices=STATUS, null=True, blank=True)
    create_at = models.DateTimeField(default=datetime.now, verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    is_top = models.BooleanField(default=True, verbose_name="Топ")
    image = models.ImageField(upload_to='videos/', verbose_name="Обложка")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='users',
                              verbose_name="Владелец")

    class Meta:
        verbose_name = _("Видео")
        verbose_name_plural = _("Видео")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                devices = FCMDevice.objects.all()
                devices.send_message(title="Новое видео🔥", body="Кликните сюда чтобы посмотреть видео " + self.title)

            this = Video.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except:
            pass

        if self.status == '1':
            self.is_active = False
        if self.status == '2':
            self.is_active = True
        if self.status == '3':
            self.is_active = False

        super(Video, self).save(*args, **kwargs)
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


@receiver(pre_delete, sender=Video)
def delete_image(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)


class Tariff(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='tariffs', verbose_name="Ютуб ссылка")
    views = models.IntegerField(verbose_name="Просмотр")
    price = models.FloatField(verbose_name="Цена")

    class Meta:
        verbose_name = _("Тариф")
        verbose_name_plural = _("Тарифы")


class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments', verbose_name="Ютуб ссылка")
    text = models.TextField(verbose_name="Текст")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments',
                             verbose_name="Пользователь")
    parent = models.ForeignKey('self', verbose_name="Родитель", related_name='children', on_delete=models.SET_NULL,
                               blank=True, null=True)
    create_at = models.DateTimeField(default=datetime.now, verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    class Meta:
        verbose_name = _("Комментарий")
        verbose_name_plural = _("Комментарии")

    def __str__(self):
        return self.text


class FAQ(models.Model):
    question = models.TextField(verbose_name="Вопрос")
    reply = models.TextField(verbose_name="Ответ")


class Request(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories',
                                 verbose_name="Категория")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    phone = models.CharField(max_length=15, verbose_name="Телефон номер")
    sum = models.IntegerField(default=0, verbose_name="Цена")
    promo_code = models.CharField(max_length=40, blank=True, verbose_name="Промо код")
    create_at = models.DateTimeField(default=datetime.now, verbose_name="Дата создания")
    is_checked = models.BooleanField(default=False, verbose_name="Провереннный")

    class Meta:
        verbose_name = _("Заявка")
        verbose_name_plural = _("Заявки")


class Banner(models.Model):
    video = models.CharField(max_length=255, null=True, verbose_name="Ютуб ссылка")
    image = models.ImageField(upload_to='banners/', verbose_name="Обложка")
    views = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='views')
    block = models.IntegerField(default=1, verbose_name="Блок")

    class Meta:
        verbose_name = _("Баннер")
        verbose_name_plural = _("Баннеры")

    def __str__(self):
        return self.video

    def save(self, *args, **kwargs):
        try:
            this = Banner.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()

        except:
            pass

        super(Banner, self).save(*args, **kwargs)
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


@receiver(pre_delete, sender=Banner)
def banner_image(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)


class ViewBanner(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='banners',
                             verbose_name="Пользователь")
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE, related_name='banners', verbose_name="Баннер видео")
    create_at = models.DateTimeField(default=datetime.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = _("Просмотр история (Баннер)")
        verbose_name_plural = _("Просмотр истории (Баннер)")


class ViewHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='histories',
                             verbose_name="Пользователь")
    bonus = models.IntegerField(default=0, verbose_name="Бонус")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='histories', verbose_name="Ютуб ссылка")
    create_at = models.DateTimeField(default=datetime.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = _("Просмотр история (Реклама))")
        verbose_name_plural = _("Просмотр истории (Реклама)")


class VideoTraining(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название")
    video = models.CharField(max_length=255, null=True, verbose_name="Ютуб ссылка")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    image = models.ImageField(upload_to='videos_training/', verbose_name="Фотография")

    class Meta:
        verbose_name = _("Видео обучения")
        verbose_name_plural = _("Видео обучения")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        try:
            this = VideoTraining.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()

        except:
            pass

        super(VideoTraining, self).save(*args, **kwargs)
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


@receiver(pre_delete, sender=VideoTraining)
def video_training_image(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)
