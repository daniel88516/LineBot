from __future__ import annotations

from .question import Question

import requests
import json


class UserState(object):
    # 建構函式, 初始化用戶狀態, 紀錄 step, Question, data 
    def __init__(self, questions: list[Question] = list()):
        self.step = 0
        self.questions = list(questions)
        self.data = {}
        self.check_type: str | None = None

    @property
    def have_next_question(self):
        return self.step < len(self.questions)

    def next_question(self):
        self.step = self.step + 1

    def set_current_question_answer(self, answer):
        self.data[self.current_question.question_key] = answer

    def extend_questions(self, questions: list[Question]):
        self.questions.extend(questions)

    def add_question(self, question: Question):
        self.questions.append(question)

    @property
    def current_question(self) -> Question:
        return self.questions[self.step]
    
    def get_final_result(self, url: str):
        self.data.pop(self.check_type)
        response = requests.post(url, json=self.data)
        return json.loads(response.content)