from flask import Flask, request, abort
import os
from dotenv import load_dotenv
import joblib
import pandas as pd
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent, UnsendEvent, Event

# 载入 .env 文件
load_dotenv()

app = Flask(__name__)

# Line API 驗證
access_token = os.getenv('LINE_ACCESS_TOKEN')
secret = os.getenv('LINE_SECRET')
predict_api_url = os.getenv('PREDICT_API_URL')
line_bot_api = LineBotApi(access_token)  # token 確認
handler = WebhookHandler(secret)      # secret 確認

"""
接收並處理來自 Line 平台的 Webhook 請求。
獲取並驗證請求的簽名。
調用相應的處理函數處理請求數據。
在簽名驗證失敗時返回 400 錯誤碼。
"""
@app.route("/", methods=['POST'])
def webhook():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 載入模型
model = joblib.load('./diabete_prediction_model.pkl')
# 定義 Question 類別, 方便問問題
class Question:
    def __init__(self, question_text):
        # 設定問題的文字內容
        self.question_text = question_text
    def ask_question(self, reply_token):
        raise NotImplementedError("這個方法應該在子類別實現")

class TextQuestion(Question):
    def __init__(self, question_text):
        # 初始化跟父類別相同
        super().__init__(question_text)

    def ask_question(self, reply_token):
        # 傳送文字問題
        message = TextSendMessage(text=self.question_text)
        # 使用 reply 方法傳送
        line_bot_api.reply_message(reply_token, message)
        
class ButtonQuestion(Question):
    def __init__(self, question_text, choices, introduction=None):
        super().__init__(question_text)
        self.introduction = introduction if introduction else "請選擇您的" + question_text
        self.choices = choices

    def ask_question(self, reply_token):
        actions = [PostbackAction(label=label, data=data) for label, data in self.choices]
        template_message = TemplateSendMessage(
            alt_text= "請輸入" + self.question_text,
            template=ButtonsTemplate(
                title=self.question_text,
                text=self.introduction,
                actions=actions
            )
        )
        line_bot_api.reply_message(reply_token, template_message)
class UserState:
    # 建構函式, 初始化用戶狀態, 紀錄 step, Question, data 
    def __init__(self, questions):
        self.step = 0
        self.questions = list(questions)
        self.data = []
        self.testType = None
# 紀錄用戶當前輸入狀態
user_state = {}
# 問題列表, 之後可以在更加簡化
introduction = ("您好，我是健康智能管家。\n"
                "您可以叫我阿瑄=U=\n"
                "請問是否進行疾病預測呢?")
introQuestions = [
    ButtonQuestion('是否進行疾病預測?', [('是', 'continue'), ('否', 'exit')], introduction),
    ButtonQuestion('請選擇預測項目', [('糖尿病', 'diabete'), ('高血壓', 'hypertension'), ('心臟病', 'heart_disease')])
]
diabeteQuestions = [
    ButtonQuestion('性別', [('男', '0'), ('女', '1')]),
    TextQuestion("請輸入年齡: "),
    TextQuestion("請輸入BMI: "),
    TextQuestion("請輸入HbA1c水平: "),
    TextQuestion("請輸入血糖水平: ")
]
hypertensionQuestions = [
    ButtonQuestion('測試問題1 (高血壓)', [('測試答案1', '0'), ('測試答案2', '1'), ('測試答案3', '2')]),
    TextQuestion("測試問題2 (高血壓)"),
    TextQuestion("測試問題3 (高血壓)"),
]
heartDiseaseQuestions = [
    ButtonQuestion('測試問題1 (心臟病)', [('測試答案1', '0'), ('測試答案2', '1'), ('測試答案3', '2')]),
    TextQuestion("測試問題2 (心臟病)"),
    TextQuestion("測試問題3 (心臟病)"),
]
# 初始化新的使用者
def initializeNewUser(reply_token, user_id):
    # 初始化
    user_state[user_id] = UserState(introQuestions)
    # 問第一個問題
    user_state[user_id].questions[0].ask_question(reply_token)
    
# 最後輸出, 根據使用者輸入預測結果
def process_final_input(reply_token, user_id):
    # 獲取使用者資料
    user_testType = user_state[user_id].testType
    user_data = user_state[user_id].data
    
    if user_testType == 'diabete':
        # 將使用者輸入轉換成 pandas, 並加入標籤
        user_input = pd.DataFrame([user_data], columns=['gender', 'age', 'bmi', 'HbA1c_level', 'blood_glucose_level'])
        # 使用模型預測結果
        prediction = model.predict(user_input)
        # 二分判斷
        result = "没有糖尿病" if prediction[0] == 0 else "有糖尿病"
        prediction = model.predict_proba(user_input)[0]
        line_bot_api.reply_message(reply_token, [
            TextSendMessage(text=f"{result}"),
            TextSendMessage(text=f"糖尿病機率:{prediction[1]*100:.2f}%"),
            TextSendMessage(text="謝謝光臨!! 有需要都可以在叫我喔")
        ])
    elif user_testType == 'hypertension':
        line_bot_api.reply_message(reply_token, TextSendMessage(text="高血壓測試結束"))
    elif user_testType == 'heart_disease':
        line_bot_api.reply_message(reply_token, TextSendMessage(text="心臟病測試結束"))
    del user_state[user_id]
    
def EndPrediction(reply_token, user_id):
    line_bot_api.reply_message(reply_token, TextSendMessage(text="謝謝光臨!! 有需要都可以在叫我喔"))
    del user_state[user_id]

#下一個問題
def NextQuestion(reply_token, user_id):
    user_state[user_id].step += 1
    # 還沒到最後一個問題: 繼續問下一個問題
    if user_state[user_id].step < len(user_state[user_id].questions):
        user_state[user_id].questions[user_state[user_id].step].ask_question(reply_token)
    else:
        # 否則輸出最後結果
        process_final_input(reply_token, user_id)

# 正整數驗證
def validate_numeric_input(event, msg):
    if not msg.isdigit():
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確的數字"))
        return False
    if float(msg) <= 0:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入大於 0 的有效數字"))
        return False
    return True
# 用戶傳送訊息的時候做出的回覆
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event: Event):
    user_id = event.source.user_id
    msg = event.message.text
    if msg == 'exit':
        EndPrediction(event.reply_token, user_id)
    # 初始化新的使用者 or 判斷輸入
    if user_id not in user_state:
        initializeNewUser(event.reply_token, user_id)
        return
    if isinstance(user_state[user_id].questions[user_state[user_id].step], ButtonQuestion):
        # 按鈕問題不應該輸入文字回答
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇按鈕選項"))
        return
    # 數字驗證
    if not validate_numeric_input(event, msg):
        return
    # 將資料加入, 前往下一題
    # 驗證通過，加入正確資料，前往下一題目
    user_state[user_id].data.append(float(msg))
    NextQuestion(event.reply_token, user_id)
# 按鈕按下之後的回應
@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    # 獲取使用者與回傳的按鈕資訊
    user_id = event.source.user_id
    postback_data = event.postback.data
    # 初始化新的使用者 or 判斷輸入
    if user_id not in user_state:
        initializeNewUser(event.reply_token, user_id)
        return
    if isinstance(user_state[user_id].questions[user_state[user_id].step], TextQuestion):
        # 文字問題不接受按鈕回答
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入數字"))
        return
    # 回答分支判斷, 可考慮建立一個讀路的函式處理
    if(postback_data == 'exit'):
        # 退出對話, 刪除使用者紀錄
        EndPrediction(event.reply_token, user_id)
    if(postback_data == 'diabete'):
        user_state[user_id].testType = 'diabete'
        user_state[user_id].questions.extend(diabeteQuestions)
        # 加入多個問題, 因此是 extend 而不是 append, 不需要使用指標解引用, python 會幫忙
    elif(postback_data == 'heart_disease'):
        user_state[user_id].testType = 'heart_disease'
        user_state[user_id].questions.extend(heartDiseaseQuestions)
    elif(postback_data == 'hypertension'):
        user_state[user_id].testType = 'hypertension'
        user_state[user_id].questions.extend(hypertensionQuestions)
    elif(postback_data != 'continue'):
        # 如果不是特別判斷的分支, 表示這是一般問題的回答, 將回傳的資料加入
        user_state[user_id].data.append(postback_data)
        
    NextQuestion(event.reply_token, user_id)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

