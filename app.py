from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

#Load variable lokal
channel_secret = os.getenv('CHANNEL_SECRET', None)
channel_access_token = os.getenv('CHANNEL_ACCESS', None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

#Bare minimum
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 200


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	#Simple Echo
	line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )
if __name__ == "__main__":
    app.run()