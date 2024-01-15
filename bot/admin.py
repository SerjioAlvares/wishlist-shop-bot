from django.contrib import admin

from bot.models import ChatData, Impression


@admin.register(ChatData)
class ChatDataAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'data',)


@admin.register(Impression)
class ImpressionAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'price_in_rubles')
    list_display_links = ('name',)
    search_fields = ('name',)
