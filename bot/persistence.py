from asgiref.sync import sync_to_async
from copy import deepcopy
from typing import Dict, Optional

from telegram.ext import BasePersistence, PersistenceInput
from telegram.ext._utils.types import (
    BD,
    CD,
    UD,
    CDCData,
    ConversationDict,
    ConversationKey
)

from .models import ChatData


class DjangoPersistence(BasePersistence):
    """Use Django's ChatData model for making a bot persistent."""
    def __init__(self):
        store_data = PersistenceInput(
            chat_data=True,
            bot_data=False,
            user_data=False,
            callback_data=False
        )
        super().__init__(store_data=store_data, update_interval=1)
        self.chat_data: Optional[Dict[int, CD]] = None

    @sync_to_async
    def get_chat_data(self) -> Dict[int, CD]:
        """Return the chat_data from the Database if it exists or
           an empty :obj:`dict`.

        Returns:
            Dict[:obj:`int`, :obj:`dict`]: The restored chat data.
        """
        if not self.chat_data:
            self.chat_data = {
                data.chat_id: data.data for data in ChatData.objects.all()
            }
        return deepcopy(self.chat_data)

    @sync_to_async
    def get_bot_data(self) -> BD:
        pass

    @sync_to_async
    def get_callback_data(self) -> Optional[CDCData]:
        pass

    @sync_to_async
    def get_conversations(self, name: str) -> ConversationDict:
        pass

    @sync_to_async
    def get_user_data(self) -> Dict[int, UD]:
        pass

    @sync_to_async
    def update_chat_data(self, chat_id: int, data: CD) -> None:
        """Update the chat_data and save them in Database.

        Args:
            chat_id (:obj:`int`): The chat the data might have been
                                  changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.Application.chat_data`
                                           ``[chat_id]``.
        """
        if self.chat_data is None:
            self.chat_data = {}

        if self.chat_data.get(chat_id) == data:
            return

        self.chat_data[chat_id] = data
        ChatData.objects.update_or_create(
            chat_id=chat_id,
            defaults={'data': data}
        )

    @sync_to_async
    def update_bot_data(self, data: BD) -> None:
        pass

    @sync_to_async
    def update_callback_data(self, data: CDCData) -> None:
        pass

    @sync_to_async
    def update_conversation(
        self,
        name: str,
        key: ConversationKey,
        new_state: Optional[object]
    ) -> None:
        pass

    @sync_to_async
    def update_user_data(self, user_id: int, data: UD) -> None:
        pass

    @sync_to_async
    def drop_chat_data(self, chat_id: int) -> None:
        """Delete the specified key from the ``chat_data`` and
        save them in Database.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int`): The chat id to delete from the persistence.
        """
        if self.chat_data is None:
            return

        self.chat_data.pop(chat_id, None)
        ChatData.objects.update_or_create(
            chat_id=chat_id,
            defaults={'data': None}
        )

    @sync_to_async
    def drop_user_data(self, user_id: int) -> None:
        pass

    @sync_to_async
    def refresh_chat_data(self, chat_id: int, chat_data: CD) -> None:
        """Do nothing.

        .. versionadded:: 13.6
        .. seealso:: :meth:`telegram.ext.BasePersistence.refresh_user_data`
        """

    @sync_to_async
    def refresh_bot_data(self, bot_data: BD) -> None:
        pass

    @sync_to_async
    def refresh_user_data(self, user_id: int, user_data: UD) -> None:
        pass

    def flush(self) -> None:
        pass
