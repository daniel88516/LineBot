from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from linebot import LineBotApi
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent, UnsendEvent


class Question(ABC):
    def __init__(self, question_text, question_key: str):
        # 設定問題的文字內容
        self.question_text = question_text
        self.question_key = question_key

    @abstractmethod
    def ask_question(self, reply_token): ...


class TextQuestion(Question):
    def __init__(self, question_text, question_key: str, line_bot_api: LineBotApi):
        super().__init__(question_text, question_key)
        self.line_bot_api = line_bot_api

    def ask_question(self, reply_token):
        # 傳送文字問題
        message = TextSendMessage(text=self.question_text)
        # 使用 reply 方法傳送
        self.line_bot_api.reply_message(reply_token, message)


class ButtonOption(object):
    def __init__(self, label: str, data: Any) -> None:
        self.label = label
        self.data = data


class ButtonQuestion(Question):
    def __init__(self, question_text, question_key: str, line_bot_api: LineBotApi, choices: list[ButtonOption], introduction: str | None = None):
        super().__init__(question_text, question_key)
        self.line_bot_api = line_bot_api
        self.introduction = introduction if introduction else "請選擇您的" + question_text
        self.choices = choices

    def ask_question(self, reply_token):
        actions = [PostbackAction(label=option.label, data=option.data) for option in self.choices]
        template_message = TemplateSendMessage(
            alt_text=self.question_text,
            template=ButtonsTemplate(
                title=self.question_text,
                text=self.introduction,
                actions=actions
            )
        )
        self.line_bot_api.reply_message(reply_token, template_message)


