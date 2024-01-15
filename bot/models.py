from django.db import models


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
