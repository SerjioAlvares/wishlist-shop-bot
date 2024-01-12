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
