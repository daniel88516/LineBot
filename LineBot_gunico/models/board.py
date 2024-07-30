from __future__ import annotations

from linebot import LineBotApi
from linebot.models import TextSendMessage

from .user_state import UserState


class Board(object):
    def __init__(self, line_bot_api: LineBotApi) -> None:
        self.line_bot_api = line_bot_api
        self.user_states: dict[str, UserState] = dict()

    def get_user(self, user_id: str) -> UserState:
        return self.user_states.get(user_id)

    def user_exist(self, user_id: str) -> bool:
        return True if self.get_user(user_id) is not None else False

    def add_user(self, user_id: str):
        self.user_states[user_id] = UserState()

    def remove_user(self, user_id: str):
        if self.user_exist(user_id):
            user = self.user_states.pop(user_id)
            del user

    def end_prediction(self, reply_token, user_id: str, reply_message: str | None = "謝謝光臨!! 有需要都可以在叫我喔"):
        if reply_message is not None:
            self.line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        self.remove_user(user_id=user_id)