from asgiref.sync import sync_to_async
from typing import Dict, List

from .models import BotData, Impression


class Database():
    """Transfer data asynchronously between the database and the bot."""
    def __init__(self):
        pass

    @sync_to_async
    def get_impressions(self, language: str) -> List[Dict]:
        """Get impressions from database."""
        impressions = Impression.objects.all()
        if language == 'russian':
            return [
                {
                    'id': impression.number,
                    'name': impression.name,
                    'price': f'{impression.price_in_rubles} ₽',
                    'url': impression.url_for_russians
                }
                for impression in impressions
            ]

        return [
            {
                'id': impression.number,
                'name': impression.english_name,
                'price': f'{impression.price_in_euros} €',
                'url': impression.url_for_english
            }
            for impression in impressions
        ]

    @sync_to_async
    def get_payment_details(self, language: str) -> str:
        """Get payment details from database."""
        bot = BotData.objects.all()
        if language == 'russian':
            return bot[0].russian_payment_details

        return bot[0].english_payment_details

    @sync_to_async
    def get_policy_url(self, language: str) -> str:
        """Get policy url from database."""
        bot = BotData.objects.all()
        if language == 'russian':
            return bot[0].russian_policy_url

        return bot[0].english_policy_url
