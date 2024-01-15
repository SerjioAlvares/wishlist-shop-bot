from asgiref.sync import sync_to_async
from typing import Dict, List

from .models import Impression


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
