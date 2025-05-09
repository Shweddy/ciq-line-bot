from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from ciq_data import ciq_data
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Line Bot API credentials
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def format_ciq_info(airport_code):
    """Format CIQ information for a given airport code."""
    if airport_code not in ciq_data:
        return f"Sorry, I don't have information for airport code {airport_code}."
    
    info = ciq_data[airport_code]
    response = f"CIQ Information for {airport_code}:\n\n"
    
    for key, value in info.items():
        # Format the key to be more readable
        formatted_key = key.replace('_', ' ').title()
        response += f"{formatted_key}: {value}\n"
    
    return response

@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip().upper()
    
    # Check if the message starts with '/'
    if text.startswith('/'):
        airport_code = text[1:]  # Remove the '/' and get the airport code
        response = format_ciq_info(airport_code)
    else:
        response = "Please enter an airport code starting with '/' (e.g., /KUL)"
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 