import os
import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# =================================================================
# 🔑 क्रेडेंशियल्स (आपकी बिल्कुल मुफ़्त Groq सेटिंग्स)
GREEN_API_ID = "7107664395"
GREEN_API_TOKEN = "4857c575c0ff4023a7aeb6bc6ba1813a04b80438d8624857a3"
GROQ_API_KEY = "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"
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

def call_groq(prompt):
    """मुफ़्त Groq API को सीधे कॉल करने वाला फंक्शन"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"⚠️ Groq एरर: सर्वर ने जवाब नहीं दिया। (Status Code: {response.status_code})"
    except Exception as e:
        return f"⚠️ कनेक्शन एरर: {str(e)}"

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    webhook_type = data.get("typeWebhook")
    
    # सिर्फ आपके फोन से भेजे गए Outgoing मैसेज को ट्रैक करें
    if webhook_type == "outgoingMessageReceived":
        try:
            message_text = data["messageData"]["textMessageData"]["textMessage"].strip()
            chat_id = data["senderData"]["chatId"].split("@")[0]
        except Exception:
            return jsonify({"status": "ignored"}), 200
        
        # सीक्रेट कोड चेक: अगर मैसेज '#' से शुरू होता है
        if message_text.startswith('#'):
            student_query = message_text[1:].strip()
            
            students = load_student_data()
            students_context = json.dumps(students, indent=2, ensure_ascii=False)
            
            prompt = f"""
            तुम 'Grace Study Centre' के पर्सनल व्हाट्सएप असिस्टेंट हो। छात्र डेटा नीचे दिया गया है:
            {students_context}
            
            सवाल: {student_query} की फीस का पूरा ब्यौरा दो।
            नियम: पूरी तरह हिंदी में जवाब दो। केवल काम की बात और फीस का सटीक विवरण पॉइंट बनाकर लिखो। फालतू बातें मत लिखना।
            """
            
            # Groq से जवाब लाएं
            ai_reply = call_groq(prompt)
            
            # वापस उसी चैट में भेजें
            send_whatsapp_message(chat_id, ai_reply)

    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Grace Study Centre Groq-Engine is Running Perfectly!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
