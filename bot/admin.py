from django.contrib import admin

from bot.models import BotData, ChatData, Impression


@admin.register(BotData)
class BotDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'bot_name',)
    list_display_links = ('bot_name',)


@admin.register(ChatData)
class ChatDataAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'data',)


@admin.register(Impression)
class ImpressionAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'price_in_rubles')
    list_display_links = ('name',)
    search_fields = ('name',)
