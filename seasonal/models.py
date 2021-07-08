import PIL
from PIL import Image
from datetime import datetime

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django_resized import ResizedImageField
from django.utils.safestring import mark_safe
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название")
    image = ResizedImageField(upload_to='seasonal/category/', verbose_name='Фотография',
                              size=[100, 100])
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ('order',)

    def image_tag(self):
        return mark_safe('<img src={} width="200" />'.format(self.image.url))

    image_tag.short_description = 'Фотография'

    def __str__(self):
        return self.title


class SeasonalVideo(models.Model):
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
    views = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='video_views',
                                   verbose_name="Просмотров")
    watched_videos = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                            related_name='watcher')
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name='seasonal_favorites')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, name='likes')
    video = models.CharField(max_length=255, null=True,
                             verbose_name="Ютуб ссылка",
                             help_text="Просмотр видео")
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='videos',
                                 verbose_name="Категория")
    type = models.CharField(verbose_name="Тип", choices=TYPE, max_length=20)
    status = models.CharField("Статус", max_length=20, choices=STATUS,
                              null=True, blank=True)
    create_at = models.DateTimeField(default=datetime.now,
                                     verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    is_top = models.BooleanField(default=True, verbose_name="Топ")
    image = models.ImageField(upload_to='seasonal/videos/', verbose_name="Обложка")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE, related_name='owner',
                              verbose_name="Владелец")

    class Meta:
        verbose_name = _("Видео")
        verbose_name_plural = _("Видео")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == '2':
            self.is_active = True
        else:
            self.is_active = False

        super(SeasonalVideo, self).save(*args, **kwargs)
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


@receiver(pre_delete, sender=SeasonalVideo)
def delete_image(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)


class SeasonalComment(models.Model):
    video = models.ForeignKey(SeasonalVideo, on_delete=models.CASCADE,
                              related_name='comments',
                              verbose_name="Ютуб ссылка")
    text = models.TextField(verbose_name="Текст")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='comment_user',
                             verbose_name="Пользователь")
    parent = models.ForeignKey('self', verbose_name="Родитель",
                               related_name='children',
                               on_delete=models.SET_NULL,
                               blank=True, null=True)
    create_at = models.DateTimeField(default=datetime.now,
                                     verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    class Meta:
        verbose_name = _("Комментарий")
        verbose_name_plural = _("Комментарии")
        ordering = ('-create_at',)

    def __str__(self):
        return self.text


class Request(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='categories',
                                 verbose_name="Категория")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    phone = models.CharField(max_length=15, verbose_name="Телефон номер")
    sum = models.IntegerField(default=0, verbose_name="Цена")
    promo_code = models.CharField(max_length=40, blank=True,
                                  verbose_name="Промо код")
    create_at = models.DateTimeField(default=datetime.now,
                                     verbose_name="Дата создания")
    is_checked = models.BooleanField(default=False, verbose_name="Провереннный")

    class Meta:
        verbose_name = _("Заявка")
        verbose_name_plural = _("Заявки")


class Stories(models.Model):
    video = models.CharField(max_length=255, null=True, verbose_name="Ютуб ссылка")
    url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='seasonal/stories/', verbose_name="Обложка")
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


@receiver(pre_delete, sender=Stories)
def banner_image(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)


class LikeStories(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='like_stories',
                             verbose_name="Пользователь")
    stories = models.ForeignKey(Stories, on_delete=models.CASCADE, related_name='like_stories',
                                verbose_name="Сторис видео")
    create_at = models.DateTimeField(default=datetime.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = _("Лайк сториса")
        verbose_name_plural = _("Лайки сторисов")
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
        verbose_name = _("Просмотр сториса")
        verbose_name_plural = _("Просмотры сторисов")


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
        verbose_name = _("Жалоба на сторис")
        verbose_name_plural = _("Жалобы на сторисы")


class ViewHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='user',
                             verbose_name="Пользователь")
    bonus = models.IntegerField(default=0, verbose_name="Бонус")
    video = models.ForeignKey(SeasonalVideo, on_delete=models.CASCADE,
                              related_name='histories',
                              verbose_name="Ютуб ссылка")
    create_at = models.DateTimeField(default=datetime.now,
                                     verbose_name="Дата создания")

    class Meta:
        verbose_name = _("Просмотр видео")
        verbose_name_plural = _("Просмотры видео")


# class BookingRequest(models.Model):
#     entry_date = models.DateTimeField(default=datetime.now, verbose_name=_('Дата въезда'))
#     exit_date = models.DateTimeField(default=datetime.now, verbose_name=_('Дата выезда'))
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room', verbose_name=_('Номер'))
#
#     class Meta:
#         verbose_name = _('Заявка на заселение')
#         verbose_name_plural = _('Заявки на заселение')
