from flask import Flask, request, jsonify
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

AIRTABLE_PAT = os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args["hub.challenge"], 200
        return "Verification token mismatch", 403
    return "Hello world", 200


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    phone_number = message.get("from")
                    text = message.get("text", {}).get("body", "")

                    print(f"\n📩 Incoming message from {phone_number}: {text}")

                    if not text:
                        send_message(phone_number, "माफ़ कीजिए, मैं सिर्फ़ टेक्स्ट मैसेज पढ़ सकता हूँ।")
                        continue

                    reply_text = find_reply(text)
                    print(f"💬 Replying with: {reply_text}")
                    send_message(phone_number, reply_text)

    except Exception as e:
        print("❌ Error handling message:", e)

    return "OK", 200


def find_reply(user_query):
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}?maxRecords=50"
    response = requests.get(url, headers=headers)
    
    print("\n📦 Airtable Response:", response.text)

    records = response.json().get("records", [])
    for record in records:
        question = record["fields"].get("Question", "")
        if user_query.strip().lower() in question.lower():
            return record["fields"].get("Refined Answer (Hindi)", "उत्तर उपलब्ध नहीं है।")
    return "माफ़ कीजिए, मैं इस प्रश्न का उत्तर नहीं ढूंढ पाया।"


def send_message(to_number, message):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    res = requests.post(url, headers=headers, json=payload)
    print("📤 WhatsApp API Response:", res.text)


if __name__ == '__main__':
    app.run(debug=True)