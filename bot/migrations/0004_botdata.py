# Generated by Django 4.2.9 on 2024-01-15 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_impression_english_name_impression_price_in_euros_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BotData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bot_name', models.CharField(max_length=256, verbose_name='Название бота по-русски')),
                ('english_bot_name', models.CharField(max_length=256, verbose_name='Название бота по-английски')),
                ('russian_policy_url', models.URLField(blank=True, verbose_name='Url Политики конфиденциальности на русском')),
                ('english_policy_url', models.URLField(blank=True, verbose_name='Url Политики конфиденциальности на английском')),
            ],
        ),
    ]
