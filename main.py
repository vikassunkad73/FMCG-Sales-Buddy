from flask import Flask, request, jsonify
import requests
import os
import json
import difflib
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

    if response.status_code != 200:
        return "डाटा लोड करने में समस्या हो रही है। कृपया बाद में प्रयास करें।"

    records = response.json().get("records", [])
    questions = [record["fields"].get("Question", "") for record in records]

    # Find best match
    matches = difflib.get_close_matches(user_query, questions, n=1, cutoff=0.5)

    if matches:
        best_match = matches[0]
        for record in records:
            if record["fields"].get("Question", "") == best_match:
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