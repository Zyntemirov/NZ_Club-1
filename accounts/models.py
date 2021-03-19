from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group


class User(AbstractUser):
    phone = models.CharField(verbose_name=_('Телефон'),
                             max_length=12,
                             null=True, unique=True, validators=[
            RegexValidator(regex=r'^996\d{9}$', message=_('Pass valid phone number'))
        ])
    otp = models.CharField(verbose_name=_('SMS code'), max_length=4)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                userProfile.objects.create(user=self)
        except:
            pass
        return super(User, self).save(*args, **kwargs)

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {'refresh': str(refresh),
                'access': str(refresh.access_token)}


# Create your models here.
class userProfile(models.Model):
    REGION = (
        ('1', 'Ош'),
        ('2', 'Ысык-Кол'),
        ('3', 'Жалал-Абад'),
        ('4', 'Талас'),
        ('5', 'Баткен'),
        ('6', 'Нарын'),
        ('7', 'Чуй'),

    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile",
                                verbose_name="Пользователь")
    agent = models.BooleanField(default=False, verbose_name='Агент Статус')
    gender = models.CharField(max_length=30, blank=True, verbose_name="Пол")
    region = models.CharField("Регион", max_length=10, choices=REGION, null=True, blank=True)
    view_count = models.IntegerField(default=0, verbose_name="Просмотров")
    balance = models.FloatField(default=0, verbose_name="Остаток баланса")
    withdrawn_balance = models.FloatField(default=0, verbose_name="Cнятый баланс")
    image = models.ImageField(upload_to='user', default='user/profile_photo.png', null=True, blank=True,
                              verbose_name="Фотография")
    birth_date = models.DateField(default=datetime.now, verbose_name="День рождения")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Дата вступления")
    updated_on = models.DateTimeField(auto_now=True, verbose_name="Обновление")

    class Meta:
        verbose_name = _("Аккаунт профиль")
        verbose_name_plural = _("Аккаунт профиль")

    def __str__(self):
        return self.user.username
