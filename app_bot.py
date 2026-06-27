import os
import json
from flask import Flask, request, jsonify
import requests
import google.generativeai as genai

app = Flask(__name__)

# =================================================================
# 🔑 क्रेडेंशियल्स (आपकी बिल्कुल सही सेटिंग्स)
GREEN_API_ID = "7107664395"
GREEN_API_TOKEN = "4857c575c0ff4023a7aeb6bc6ba1813a04b80438d8624857a3"
GEMINI_API_KEY = "AQ.Ab8RN6LGA4A0fXcNUQP4HbG8EX8WReHdWQNOuOvPDm1yrFQYDg"
# =================================================================

genai.configure(api_key=GEMINI_API_KEY)

def load_student_data():
    db_path = os.path.join('data', 'students.json')
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def send_whatsapp_message(to_number, text):
    url = f"https://api.green-api.com/waInstance{GREEN_API_ID}/sendMessage/{GREEN_API_TOKEN}"
    payload = {
        "chatId": f"{to_number}@c.us",
        "message": text
    }
    headers = {'Content-Type': 'application/json'}
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"मैसेज भेजने में एरर: {e}")

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    webhook_type = data.get("typeWebhook")
    
    # 🚀 सिर्फ आपके द्वारा फोन से भेजे गए (outgoing) मैसेज को ट्रैक करें
    if webhook_type == "outgoingMessageReceived":
        try:
            message_text = data["messageData"]["textMessageData"]["textMessage"].strip()
            chat_id = data["senderData"]["chatId"].split("@")[0]
        except Exception:
            return jsonify({"status": "ignored"}), 200
        
        # 🔐 सीक्रेट कोड चेक: अगर मैसेज '#' से शुरू होता है
        if message_text.startswith('#'):
            student_query = message_text[1:].strip() # '#' हटाकर नाम अलग करें
            
            students = load_student_data()
            students_context = json.dumps(students, indent=2, ensure_ascii=False)
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                तुम 'Grace Study Centre' के पर्सनल व्हाट्सएप असिस्टेंट हो। छात्र डेटा:
                {students_context}
                सवाल: {student_query} की फीस का ब्यौरा दो।
                नियम: पूरी तरह हिंदी में जवाब दो। केवल काम की बात और फीस का सटीक विवरण लिखो।
                """
                response = model.generate_content(prompt)
                ai_reply = response.text
                
                # 🎯 जवाब उसी चैट में वापस जाएगा जहाँ आपने कोड टाइप किया था
                send_whatsapp_message(chat_id, ai_reply)
                
            except Exception as e:
                send_whatsapp_message(chat_id, f"⚠️ जेमिनी एरर: {str(e)}")

    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Grace Study Centre Secret-Command Engine is Running Perfectly!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
