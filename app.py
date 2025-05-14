from flask import Flask, request, abort
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging.models import (
    ReplyMessageRequest, TextMessage, AudioMessage as LineAudioMessage
)
import openai
import os
from openai import OpenAI

app = Flask(__name__)

# 從環境變數獲取 Channel Access Token 和 Channel Secret
channel_access_token = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('YOUR_CHANNEL_SECRET')
openai_api_key = os.getenv('YOUR_OPENAI_API_KEY')

# Line Bot 的 Channel Access Token 和 Channel Secret
configuration = Configuration(access_token=channel_access_token)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(channel_secret)

# OpenAI API 金鑰
openai.api_key = openai_api_key

# 初始化 OpenAI 客戶端
client = OpenAI(api_key=openai_api_key)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        app.logger.error(f"Invalid signature: {str(e)}")
        app.logger.error(f"Received signature: {signature}")
        app.logger.error(f"Channel Secret: {handler.parser.secret}")
        abort(400)
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        abort(500)
    return 'OK', 200

@handler.add(MessageEvent, message=LineAudioMessage)
def handle_audio_message(event):
    # 取得語音內容
    content = messaging_api.get_message_content(message_id=event.message.id)
    audio_path = f"{event.message.id}.m4a"
    with open(audio_path, 'wb') as fd:
        for chunk in content.iter_content():
            fd.write(chunk)

    # 使用 OpenAI 進行語音轉文字
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )

    # 刪除臨時語音文件
    os.remove(audio_path)

    # 回傳轉換後的文字
    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=transcript.text)]
        )
    )

if __name__ == "__main__":
    app.run()
