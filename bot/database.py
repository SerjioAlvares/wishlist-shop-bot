from asgiref.sync import sync_to_async
from typing import Dict, List

from .models import Impression


class Database():
    """Transfer data asynchronously between the database and the bot."""
    def __init__(self):
        pass

    @sync_to_async
    def get_impressions(self) -> List[Dict]:
        """Get impressions from database."""
        impressions = Impression.objects.all()
        return [
            {
                'id': impression.number,
                'name': impression.name,
                'price': impression.price_in_rubles,
                'url': impression.url_for_russians
            }
            for impression in impressions
        ]
