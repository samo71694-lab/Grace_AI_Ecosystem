import os
import json
from flask import Flask, request, jsonify
import requests
import google.generativeai as genai

app = Flask(__name__)

# =================================================================
# 🔑 क्रेडेंशियल्स
GREEN_API_ID = "7107664395"
GREEN_API_TOKEN = "4857c575c0ff4023a7aeb6bc6ba1813a04b80438d8624857a3" # अपना ग्रीन API टोकन यहाँ डालें
GEMINI_API_KEY = "AQ.Ab8RN6I-tIfhBNJn5J60TRP_LjadX7ByjOlo3hQXiMqwIYJu1Q"
OMKAR_SIR_NUMBER = "919569912633"
# =================================================================

genai.configure(api_key=GEMINI_API_KEY)
BOT_MEMORY = {}

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
    
    if data.get("typeWebhook") == "incomingMessageReceived":
        try:
            sender = data["senderData"]["sender"].split("@")[0]
            message_text = data["messageData"]["textMessageData"]["textMessage"].strip()
        except Exception:
            return jsonify({"status": "ignored"}), 200
        
        if sender == OMKAR_SIR_NUMBER:
            students = load_student_data()
            students_context = json.dumps(students, indent=2, ensure_ascii=False)
            
            if message_text == '1' and sender in BOT_MEMORY:
                pending_job = BOT_MEMORY[sender]
                send_whatsapp_message(pending_job["parent_phone"], pending_job["draft_message"])
                send_whatsapp_message(OMKAR_SIR_NUMBER, f"✅ सफलता! {pending_job['student_name']} के पैरेंट को फीस रिमाइंडर भेज दिया गया है।")
                del BOT_MEMORY[sender]
                return jsonify({"status": "success"})
                
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                तुम 'Grace Study Centre' के पर्सनल व्हाट्सएप असिस्टेंट हो। छात्र डेटा:
                {students_context}
                सवाल: {message_text}
                नियम: पूरी तरह हिंदी में जवाब दो। अगर किसी छात्र की फीस पूछी है, तो विवरण के अंत में अनिवार्य रूप से यह लिखें: "👉 पैरेंट को यह मैसेज भेजने के लिए केवल '1' लिखकर रिप्लाई करें।"
                """
                response = model.generate_content(prompt)
                ai_reply = response.text
                
                for roll, info in students.items():
                    if info["name"].lower() in message_text.lower() or message_text.lower() in info["name"].lower():
                        BOT_MEMORY[sender] = {
                            "student_name": info["name"],
                            "parent_phone": info.get("parent_phone", ""),
                            "draft_message": ai_reply.replace("👉 पैरेंट को यह मैसेज भेजने के लिए केवल '1' लिखकर रिप्लाई करें।", "").strip()
                        }
                        break
                
                send_whatsapp_message(OMKAR_SIR_NUMBER, ai_reply)
                
            except Exception as e:
                send_whatsapp_message(OMKAR_SIR_NUMBER, f"⚠️ जेमिनी एरर: {str(e)}")

    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Grace Study Centre Cloud Engine is Running Perfectly!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
