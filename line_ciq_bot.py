from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from ciq_data import ciq_data
from dotenv import load_dotenv
import sys

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
    
    response = f"✈️ *{airport_code} INFORMATION* ✈️\n\n"
    response += f"🏢 *{info['airport_name']}*\n\n"
    
    response += "📋 *FORMS:*\n"
    response += f"• Immigration - {info['immigration_form']}\n"
    response += f"• Customs - {info['customs_form']}\n"
    response += f"• Health - {info['health_declaration']}\n\n"
    
    response += "📄 *SPECIAL DOCS:*\n"
    response += f"• Security Checklist - {info['special_document']}\n"
    response += f"• A/C Disinsection - {info.get('A/C Disinsection', 'N/A')}\n"
    response += f"• GD - {info.get('GD', 'N/A')}\n\n"
    
    response += "🚨 *ANNOUNCEMENT:*\n"
    if info['special_announcement']:
        # Handle specifically for HKG format
        if "Smoking(Public Health) Monkeypox Beware of belongings" in info['special_announcement']:
            response += "• Public Health - Smoking\n"
            response += "• Monkeypox - Beware belongings\n"
        else:
            # Generic handling for other announcements
            announcements = info['special_announcement'].replace(" Beware of belongings", "")
            items = [item.strip() for item in announcements.split() if item.strip()]
            for item in items:
                response += f"• {item}\n"
            if "Beware of belongings" in info['special_announcement']:
                response += "• Beware of belongings\n"
    else:
        response += "• None\n"
    
    response += "\nℹ️ *OTHER INFO:*\n"
    response += f"• Headcount - {info['headcount']}\n"
    response += f"• Step Down Imm. - {info['step_down_immigration']}\n"
    response += f"• Wheelchair - {info['wchr']}\n"
    response += f"• UTC: {info['utc_offset']}"
    
    if info['remark'] and info['remark'].strip():
        response += f"\n\n📝 *REMARK:*\n{info['remark']}"
    
    return response

@app.route("/", methods=['GET'])
def home():
    return "Line Bot is running!"

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
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
    # If text doesn't start with '/', don't send any response
    # This allows other conversations to happen without showing an error

def run_local_test():
    """Run a local test of the bot without using the Line API."""
    print("CIQ Line Bot Tester")
    print("==================")
    print("Type an airport code with leading '/' (e.g., /KUL) or 'exit' to quit")
    
    while True:
        try:
            user_input = input("\nEnter command: ").strip().upper()
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            if user_input.startswith('/'):
                airport_code = user_input[1:]
                response = format_ciq_info(airport_code)
                print("\n" + response)
            # If user input doesn't start with '/', don't show any message
            # This allows other conversations to happen without showing an error
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def test_airport_name():
    """Test function specifically for checking airport name."""
    airport_code = "KUL"
    response = format_ciq_info(airport_code)
    print(response)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run in test mode if 'test' argument is provided
        run_local_test()
    elif len(sys.argv) > 1 and sys.argv[1] == 'test_name':
        # Test just the airport name formatting
        test_airport_name()
    else:
        # Run the Flask server by default
        app.run(host='0.0.0.0', port=5000) 