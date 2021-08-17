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
from django.core.validators import FileExtensionValidator


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


class City(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название города")
    image = ResizedImageField(upload_to='seasonal/city/', verbose_name='Фотография',
                              size=[100, 100])
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        verbose_name = _("Город")
        verbose_name_plural = _("Города")
        ordering = ('order',)

    def image_tag(self):
        return mark_safe('<img src={} width="200" />'.format(self.image.url))

    image_tag.short_description = 'Фотография'

    def __str__(self):
        return self.title


class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'))
    capacity = models.IntegerField(verbose_name=_('Вместимость'))
    price = models.FloatField(verbose_name=_('Цена'))
    room_limit = models.IntegerField(verbose_name=_('Колличество номеров'))
    apartment = models.ForeignKey('SeasonalApartment', related_name='apartment', verbose_name=_('Пансионат'),
                                  on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'

    def __str__(self):
        return self.name


class  BookingRequest(models.Model):
    entry_date = models.DateTimeField(default=datetime.now, verbose_name=_('Дата въезда'))
    exit_date = models.DateTimeField(default=datetime.now, verbose_name=_('Дата выезда'))
    room = models.ForeignKey('Room', related_name='room', verbose_name=_('Номер'),
                             on_delete=models.CASCADE)
    phone = models.CharField(max_length=12, verbose_name=_('Номер телефона'))
    comment = models.TextField(verbose_name=_('Коментарий'))
    adult_count = models.IntegerField(verbose_name=_('Количество взрослых'))
    kids_count = models.IntegerField(verbose_name=_('Количество детей'))
    room_count = models.IntegerField(verbose_name=_('Количество номеров'))
    total_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name=_('Сумма брони'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='booking_user',
                             verbose_name="Пользователь")
    accept = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = _('Заявка на заселение')
        verbose_name_plural = _('Заявки на заселение')


class ApartmentImage(models.Model):
    image = models.ImageField(verbose_name=_('Изображение'), upload_to='seasonal/image/')
    apartment = models.ForeignKey('SeasonalApartment', verbose_name=_('Пансинат'),
                                  related_name='images', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Изображение')
        verbose_name_plural = _('Список изображений')


class SeasonalApartment(models.Model):
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
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    phone = models.CharField(max_length=15, verbose_name="Телефон номер")
    video_by_user = models.FileField(upload_to='videos_uploaded', blank=True, null=True,
                                     validators=[FileExtensionValidator(
                                         allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    video_link = models.CharField(max_length=255, null=True, blank=True,
                                  verbose_name="Ютуб ссылка",
                                  help_text="Ссылка на видео для публикации")
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 verbose_name="Категория")
    city = models.ForeignKey(City, on_delete=models.CASCADE,
                                 verbose_name="Город")
    cover_image = ResizedImageField(size=[500, 300], upload_to='seasonal/apartment/',
                                    verbose_name=_('Обложка'), blank=True, null=True)

    views = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='apartment_views',
                                   verbose_name="Просмотров")
    watched_videos = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                            related_name='watcher')
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name='seasonal_favorites')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, name='likes')
    is_checked = models.BooleanField(default=False, verbose_name="Провереннный")
    type = models.CharField(verbose_name="Тип", choices=TYPE, max_length=20)
    # status = models.CharField("Статус", max_length=20, choices=STATUS,
    #                           null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True,
                                     verbose_name="Дата создания")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE, related_name='owner',
                              verbose_name="Владелец")

    class Meta:
        verbose_name = _("Пансионат")
        verbose_name_plural = _("Пансионаты")

    def __str__(self):
        return self.name


class Request(models.Model):
    STATUS = (
        ('1', 'Отклонено'),
        ('2', 'Активно'),
        ('3', 'В ожидании')
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    phone = models.CharField(max_length=15, verbose_name="Телефон номер")
    video_by_user = models.FileField(upload_to='videos_uploaded', blank=True, null=True,
                                     validators=[FileExtensionValidator(
                                         allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 verbose_name="Категория")
    city = models.ForeignKey(City, on_delete=models.CASCADE,
                                 verbose_name="Город")
    cover_image = ResizedImageField(size=[500, 300], upload_to='seasonal/apartment/',
                                    verbose_name=_('Обложка'), blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE, related_name='RequestOwner',
                              verbose_name="Владелец")
    status = models.CharField('Статус', choices=STATUS, max_length=20, default='3')
    create_at = models.DateTimeField(auto_now_add=True,
                                     verbose_name="Дата создания")
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class ApartmentRequestImage(models.Model):
    image = models.ImageField(verbose_name=_('Изображение'), upload_to='seasonal/image/')
    apartment = models.ForeignKey('Request', verbose_name=_('Пансинат'),
                                  related_name='RequestImages', on_delete=models.CASCADE)


class SeasonalComment(models.Model):
    apartment = models.ForeignKey(SeasonalApartment, on_delete=models.CASCADE,
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
    apartment = models.ForeignKey(SeasonalApartment, on_delete=models.CASCADE,
                                  related_name='histories',
                                  verbose_name="Ютуб ссылка")
    create_at = models.DateTimeField(default=datetime.now,
                                     verbose_name="Дата создания")

    class Meta:
        verbose_name = _("Просмотр видео")
        verbose_name_plural = _("Просмотры видео")
