from django.db import models


class BotData(models.Model):
    bot_name = models.CharField('Название бота', max_length=256)
    english_bot_name = models.CharField(
        'Название бота по-английски',
        max_length=256
    )
    russian_policy_url = models.URLField(
        'Url Политики конфиденциальности на русском',
        blank=True
    )
    english_policy_url = models.URLField(
        'Url Политики конфиденциальности на английском',
        blank=True
    )
    russian_payment_details = models.TextField(
        'Реквизиты для оплаты сертификата (на русском)',
        blank=True
    )
    english_payment_details = models.TextField(
        'Реквизиты для оплаты сертификата (на английском)',
        blank=True
    )

    class Meta:
        verbose_name = 'бот'
        verbose_name_plural = 'боты'


class ChatData(models.Model):
    chat_id = models.BigIntegerField(
        'ID чата',
        primary_key=True,
        null=False,
        blank=False
    )
    data = models.JSONField()

    class Meta:
        verbose_name = 'чат'
        verbose_name_plural = 'чаты'


class Impression(models.Model):
    number = models.PositiveIntegerField('Номер', unique=True)
    name = models.CharField('Наименование по-русски', max_length=256)
    english_name = models.CharField(
        'Наименование по-английски', max_length=256
    )
    price_in_rubles = models.PositiveIntegerField('Цена в рублях')
    price_in_euros = models.PositiveIntegerField('Цена в Евро')
    url_for_russians = models.URLField('Url русского описания', blank=True)
    url_for_english = models.URLField('Url английского описания', blank=True)

    class Meta:
        ordering = ['number']
        verbose_name = 'впечатление'
        verbose_name_plural = 'впечатления'
