# CIQ Information Line Bot

This is a Line chatbot that provides CIQ (Customs, Immigration, and Quarantine) information for various airports.

## Features

- Provides detailed CIQ information for various airports
- Easy to use with simple commands (e.g., `/KUL`, `/SIN`)
- Formatted responses for better readability
- Airport-specific details on:
  - Immigration & customs requirements
  - Health declarations
  - Special documents
  - Passenger manifests
  - Special announcements
  - Headcount requirements
  - UTC offset
  - And more!

## Setup

### Local Development

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ciq-line-bot.git
cd ciq-line-bot
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a Line Bot account and get your credentials:
   - Go to [Line Developers Console](https://developers.line.biz/console/)
   - Create a new provider and channel
   - Get your Channel Secret and Channel Access Token

4. Create a `.env` file in the project root with your Line credentials:
```
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
LINE_CHANNEL_SECRET=your_channel_secret
```

5. Run the bot:
```bash
python line_ciq_bot.py
```

6. Set up your webhook URL in the Line Developers Console:
   - Use a service like ngrok to expose your local server: `ngrok http 5000`
   - Set the webhook URL to `https://your-ngrok-url/callback`

### Heroku Deployment

This bot is ready for Heroku deployment:

1. Create a Heroku account and install the Heroku CLI
2. Log in to Heroku:
```bash
heroku login
```

3. Create a new Heroku app:
```bash
heroku create your-app-name
```

4. Set environment variables:
```bash
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
heroku config:set LINE_CHANNEL_SECRET=your_channel_secret
```

5. Deploy to Heroku:
```bash
git push heroku main
```

6. Update the webhook URL in Line Developers Console to your Heroku app URL: `https://your-app-name.herokuapp.com/callback`

## Usage

Send a message to the bot with an airport code starting with '/' (e.g., `/KUL`), and the bot will respond with the CIQ information for that airport.

Example:
- `/KUL` - Get CIQ information for Kuala Lumpur
- `/SIN` - Get CIQ information for Singapore
- `/HKG` - Get CIQ information for Hong Kong

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 