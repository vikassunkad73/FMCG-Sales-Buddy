# Sales Coach Agent (MVP)

A WhatsApp-based intelligent sales assistant for Hindi-speaking field reps.

## Key Features
- Supports Hindi or English input
- Answers always in Hindi
- Uses GPT to detect sales context
- Response database from Google Sheets

## Setup
1. Install dependencies:
```
pip install -r requirements.txt
```

2. Add your credentials in a `.env` file

3. Deploy on Render, set Twilio webhook to `/webhook`

4. Update Google Sheet with proper intent tags and Hindi responses.
