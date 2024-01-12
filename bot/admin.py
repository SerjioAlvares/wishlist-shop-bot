from django.contrib import admin

from bot.models import ChatData


@admin.register(ChatData)
class ChatDataAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'data',)
