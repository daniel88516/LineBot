import os

from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent

from models import TextQuestion, ButtonQuestion, ButtonOption, UserState, Board

load_dotenv()

app = Flask(__name__)

# Line API 驗證
access_token = os.getenv('LINE_ACCESS_TOKEN')
secret = os.getenv('LINE_SECRET')
predict_api_url = os.getenv('PREDICT_API_URL')
line_bot_api = LineBotApi(access_token)  # token 確認
handler = WebhookHandler(secret)      # secret 確認

@app.route("/", methods=['POST'])
def webhook():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

board = Board()

introduction = \
(
    "您好，我是健康智能管家。\n"
    "您可以叫我阿瑄=U=\n"
    "請問是否進行疾病預測呢?"
)

intro_question_options = [
    ButtonOption(label='是', data='continue'), 
    ButtonOption(label='否', data='exit')
]

ANS_DIABETES = 'diabetes'
predict_type_question_options = [
    ButtonOption(label='糖尿病', data=ANS_DIABETES)
]

gender_question_options = [
    ButtonOption(label='男', data=0),
    ButtonOption(label='女', data=1)
]

intro_question = ButtonQuestion(line_bot_api=line_bot_api, question_text='是否進行疾病預測?', choices=intro_question_options, introduction=introduction, question_key='intro')
predict_type_question = ButtonQuestion(line_bot_api=line_bot_api, question_text='請選擇預測項目', choices=predict_type_question_options, question_key='check_type')

diabeteQuestions = [
    ButtonQuestion(line_bot_api=line_bot_api, question_text="請輸入性別", choices=gender_question_options),
    TextQuestion(line_bot_api=line_bot_api, question_text="請輸入年齡: ", question_key='age'),
    TextQuestion(line_bot_api=line_bot_api, question_text="請輸入BMI: ", question_key='bmi'),
    TextQuestion(line_bot_api=line_bot_api, question_text="請輸入HbA1c水平: ", question_key='hba1c'),
    TextQuestion(line_bot_api=line_bot_api, question_text="請輸入血糖水平: ", question_key='blood_sugar')
]

check_types = [
    ANS_DIABETES
]

def validate_numeric_input(event, msg):
    if not msg.isdigit():
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確的數字"))
        return False
    if float(msg) <= 0:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入大於 0 的有效數字"))
        return False
    return True

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent):
    user_id = event.source.user_id
    msg = event.message.text
    if msg == 'exit':
        board.end_prediction(reply_token=event.reply_token, user_id=user_id)
    if not board.get_user(user_id):
        board.add_user(user_id)
    user = board.get_user(user_id)
    user.add_question(intro_question)
    if isinstance(user.current_question, ButtonQuestion):
        # 按鈕問題不應該輸入文字回答
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇按鈕選項"))
    # 數字驗證
    if not validate_numeric_input(event, msg):
        return
    # 將資料加入, 前往下一題
    # 驗證通過，加入正確資料，前往下一題目
    user.set_current_question_answer(msg)
    if user.have_next_question:
        user.next_question()

@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    # 獲取使用者與回傳的按鈕資訊
    user_id = event.source.user_id
    postback_data = event.postback.data
    if not board.get_user(user_id):
        board.add_user(user_id)
        user = board.get_user(user_id)
        user.add_question(intro_question)
    user = board.get_user(user_id)
    if isinstance(user.current_question, TextQuestion):
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入數字"))
    if postback_data == 'exit':
        return board.end_prediction(reply_token=event.reply_token, user_id=user_id)
    user.set_current_question_answer(postback_data)
    if postback_data in check_types:
        user.extend_questions(diabeteQuestions)
    if user.have_next_question:
        user.next_question()
    else:
        result = user.get_final_result(url=predict_api_url)
        have_diabetes = result.get('have_daibetes')
        diabetes_percentage = result.get('diabetes_percentage')
        have_diabetes_str = "您有糖尿病" if have_diabetes is True else "您沒有糖尿病"
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text=f"{have_diabetes_str}"),
            TextSendMessage(text=f"糖尿病機率:{diabetes_percentage}%"),
            TextSendMessage(text="謝謝光臨!! 有需要都可以在叫我喔")
        ])