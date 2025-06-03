from flask import Flask, request, abort
from sheet_lookup import get_response_for_intent
from twilio.twiml.messaging_response import MessagingResponse
from openai import Completion, api_key
import os

app = Flask(__name__)
api_key = os.getenv("OPENAI_API_KEY")

# List of valid intent tags
INTENT_TAGS = [
    "retailer_no_demand_maaza",
    "improve_visibility_low_performance",
    "drive_brand_pack",
    "cooler_purity_issue",
    "default_fallback"
]

def detect_intent_with_gpt(message):
    import openai
    openai.api_key = api_key

    prompt = f"""You are a sales assistant helping field sales reps.
Given the following message (in Hindi or English), classify it into one of these intent tags:
{', '.join(INTENT_TAGS)}

Message: \"{message}\"
Intent tag:
"""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=15,
            temperature=0
        )
        intent = response.choices[0].text.strip()
        return intent if intent in INTENT_TAGS else "default_fallback"
    except Exception as e:
        return "default_fallback"

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')

    intent = detect_intent_with_gpt(incoming_msg)
    response_text = get_response_for_intent(intent)

    # Fallback clarification
    if intent == "default_fallback":
        response_text = (
            "माफ कीजिए, मैं पूरी तरह समझ नहीं पाया। क्या आप इनमें से किसी एक की बात कर रहे हैं?
"
            "👉 विजिबिलिटी की समस्या
👉 माजा नहीं बिक रहा
👉 कूलर स्टॉक

कृपया कीवर्ड भेजें।"
        )

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(response_text)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
