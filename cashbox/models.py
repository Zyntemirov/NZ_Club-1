from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class CashBox(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='cashbox',
                             verbose_name="Пользователь")
    method = models.CharField(max_length=50, verbose_name="Метод")
    operator = models.CharField(max_length=50, verbose_name="Оператор")
    props_number = models.CharField(max_length=255, verbose_name="Пропс номер")
    amount = models.IntegerField(verbose_name="Сумма")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачено")
    create_at = models.DateTimeField(auto_now=True,
                                     verbose_name="Дата создания")

    class Meta:
        verbose_name = _("Касса")
        verbose_name_plural = _("Касса")


class Transfer(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='cashbox_sender',
                               verbose_name="Отправитель")
    receiver = models.CharField(max_length=50, verbose_name="Получатель")
    amount = models.IntegerField(verbose_name="Сумма")
    code = models.CharField(max_length=50, verbose_name="Код")
    create_at = models.DateTimeField(auto_now=True,
                                     verbose_name="Дата создания")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачено")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        verbose_name = _("Перевод")
        verbose_name_plural = _("Переводы")
        ordering = ('-create_at',)


class PromoCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='promo_codes',
                             verbose_name="Пользователь")
    code = models.CharField(max_length=50, verbose_name="Код")
    create_at = models.DateTimeField(auto_now=True,
                                     verbose_name="Дата создания")

    class Meta:
        verbose_name = _("Промо код")
        verbose_name_plural = _("Промо коды")

    def __str__(self):
        return str(self.code)


class DonateTransfer(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='donate_sender',
                               verbose_name="Отправитель")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name='donate_receiver',
                                 verbose_name="Получатель")
    amount = models.IntegerField(verbose_name="Сумма")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Благотворительный перевод")
        verbose_name_plural = _("Блалготворительные переводы")
        ordering = ('-created',)
