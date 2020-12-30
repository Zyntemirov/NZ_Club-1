from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)


# Create your models here.
class userProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile", verbose_name="Пользователь")
    agent = models.BooleanField(default=False, verbose_name='Агент Статус')
    gender = models.CharField(max_length=30, blank=True, verbose_name="Пол")
    region = models.CharField(max_length=200, blank=True, verbose_name="Адрес")
    view_count = models.IntegerField(default=0, verbose_name="Просмотров")
    balance = models.FloatField(default=0, verbose_name="Остаток баланса")
    withdrawn_balance = models.FloatField(default=0, verbose_name="Cнятый баланс")
    image = models.ImageField(upload_to='user', default='user/profile_photo.png', null=True, blank=True, verbose_name="Фотография")
    birth_date = models.DateField(default=datetime.now, verbose_name="День рождения")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Дата вступления")
    updated_on = models.DateTimeField(auto_now=True, verbose_name="Обновление")

    class Meta:
        verbose_name = _("Аккаунт профиль")
        verbose_name_plural = _("Аккаунт профиль")

    def __str__(self):
        return self.user.username
