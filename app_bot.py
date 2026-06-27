import os
import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# =================================================================
# 🔑 क्रेडेंशियल्स (आपकी बिल्कुल सही सेटिंग्स)
GREEN_API_ID = "7107664395"
GREEN_API_TOKEN = "4857c575c0ff4023a7aeb6bc6ba1813a04b80438d8624857a3"
GEMINI_API_KEY = "AQ.Ab8RN6L4DDji2EX4hL4dGE9qazyRJlSDy04Cco5LuPKOKzZFKQ"
# =================================================================

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

def call_gemini_direct(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers_token = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers_token)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        
        url_with_key = f"{url}?key={GEMINI_API_KEY}"
        response_key = requests.post(url_with_key, json=payload, headers={"Content-Type": "application/json"})
        if response_key.status_code == 200:
            return response_key.json()['candidates'][0]['content']['parts'][0]['text']
            
        return f"⚠️ जेमिनी एरर: कोड ने दोनों तरीके ट्राई किए पर काम नहीं बना। (Status: {response_key.status_code})"
        
    except Exception as e:
        return f"⚠️ कनेक्शन एरर: {str(e)}"

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    webhook_type = data.get("typeWebhook")
    
    if webhook_type == "outgoingMessageReceived":
        try:
            message_text = data["messageData"]["textMessageData"]["textMessage"].strip()
            chat_id = data["senderData"]["chatId"].split("@")[0]
        except Exception:
            return jsonify({"status": "ignored"}), 200
        
        if message_text.startswith('#'):
            student_query = message_text[1:].strip()
            
            students = load_student_data()
            students_context = json.dumps(students, indent=2, ensure_ascii=False)
            
            prompt = f"""
            तुम 'Grace Study Centre' के पर्सनल व्हाट्सएप असिस्टेंट हो। छात्र डेटा:
            {students_context}
            सवाल: {student_query} की फीस का ब्यौरा दो।
            नियम: पूरी तरह हिंदी में जवाब दो। केवल काम की बात और फीस का सटीक विवरण लिखो।
            """
            
            ai_reply = call_gemini_direct(prompt)
            send_whatsapp_message(chat_id, ai_reply)

    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Grace Study Centre Smart Direct-Engine is Running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
