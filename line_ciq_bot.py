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
    
    # Check if special_announcement is a list (new format) or string (old format)
    special_announcement = info['special_announcement']
    
    if not special_announcement or special_announcement == "N":
        # Handle empty case
        response += "• None\n"
    elif isinstance(special_announcement, list):
        # New format: Handle list of announcements directly
        for announcement in special_announcement:
            response += f"• {announcement}\n"
    else:
        # Old format: Handle as string
        # Special case for HKG
        if "Smoking(Public Health) Monkeypox Beware of belongings" in special_announcement:
            response += "• Public Health - Smoking\n"
            response += "• Monkeypox - Beware belongings\n"
        # Check if it's a simple announcement without special formatting needed
        elif special_announcement.count(' ') < 5 and '&' not in special_announcement and 'trafficking' not in special_announcement:
            # Simple announcement - don't split it
            response += f"• {special_announcement}\n"
        else:
            # More complex announcement that needs parsing
            announcement_text = special_announcement
            
            # Handle common separators
            if " Beware of belongings" in announcement_text:
                announcement_text = announcement_text.replace(" Beware of belongings", "")
                has_beware = True
            else:
                has_beware = False
                
            # Try to identify items separated by spaces that should be together
            phrases = []
            
            # Check for some common patterns
            known_phrases = [
                "Drug trafficking", "Weapon carrying", "Automated Clearance",
                "Human Trafficking", "Public Health", "Smoking", "Monkeypox",
                "Customs(FAP)", "Visit Japan Web", "Quarantine", "Currency Declaration",
                "No Smoking in Terminal", "African Fever", "Dengue Fever"
            ]
            
            remaining_text = announcement_text
            for phrase in known_phrases:
                if phrase in remaining_text:
                    phrases.append(phrase)
                    remaining_text = remaining_text.replace(phrase, "")
            
            # Add any remaining words that weren't matched
            remaining_words = [w.strip() for w in remaining_text.split() if w.strip()]
            for word in remaining_words:
                if word not in ["", "&", "and"]:
                    phrases.append(word)
            
            # Output the formatted announcements
            for phrase in phrases:
                response += f"• {phrase}\n"
                
            if has_beware:
                response += "• Beware of belongings\n"
    
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

def test_sin_announcement():
    """Test function specifically for SIN announcements."""
    airport_code = "SIN"
    response = format_ciq_info(airport_code)
    print(response)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run in test mode if 'test' argument is provided
        run_local_test()
    elif len(sys.argv) > 1 and sys.argv[1] == 'test_name':
        # Test just the airport name formatting
        test_airport_name()
    elif len(sys.argv) > 1 and sys.argv[1] == 'test_sin':
        # Test SIN announcement formatting
        test_sin_announcement()
    else:
        # Run the Flask server by default
        app.run(host='0.0.0.0', port=5000) 