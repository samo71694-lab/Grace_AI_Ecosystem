import os
import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# =================================================================
# 🔑 क्रेडेंशियल्स (आपकी मुफ़्त Groq सेटिंग्स)
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
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            try:
                error_msg = response.json().get('error', {}).get('message', 'Unknown Error')
            except:
                error_msg = response.text
            return f"⚠️ Groq सर्वर दिक्कत ({response.status_code}): {error_msg}"
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
        
        # मुख्य चेकिंग: अगर मैसेज '#' से शुरू होता है
        if message_text.startswith('#'):
            user_command = message_text[1:].strip()
            
            students = load_student_data()
            students_context = json.dumps(students, indent=2, ensure_ascii=False)
            
            # एआई के लिए महा-प्रॉम्प्ट जो सारे ऑप्शन्स को हैंडल करेगा
            prompt = f"""
            तुम 'Grace Study Centre' कोचिंग के डायरेक्टर ओंकार भाई के पर्सनल व्हाट्सएप बिजनेस असिस्टेंट हो।
            तुम्हारे पास छात्रों का यह डेटाबेस है:
            {students_context}
            
            ओंकार भाई का इनपुट है: "{user_command}"
            
            तुम्हें नीचे दिए गए नियमों के अनुसार केवल सरल, बोलचाल की हिंदी में जवाब देना है:
            
            1. अगर इनपुट खाली है, या 'menu' या 'मेन्यू' है, तो उन्हें मुख्य मेन्यू भेजें:
               "🏫 *ग्रेस स्टडी सेंटर असिस्टेंट मेन्यू* 🏫
               
               ओंकार भाई, आप क्या करना चाहते हैं? नीचे दिए गए तरीके से टाइप करें:
               
               1️⃣ *#1 [बच्चे का नाम]* - उसकी फीस और पूरी डिटेल आसान शब्दों में जानने के लिए।
               2️⃣ *#2 [नाम, क्लास, फीस]* - नए बच्चे को लिस्ट में जोड़ने का तरीका और डेटा पाने के लिए।
               3️⃣ *#3 [बच्चे का नाम] [कारण]* - पेरेंट्स के लिए एक बढ़िया व्हाट्सएप मैसेज लिखवाने के लिए।
               4️⃣ *#4 [आपका सवाल]* - कोचिंग की ग्रोथ और वायरल मार्केटिंग के लाइव सुझाव पाने के लिए।"

            2. अगर इनपुट '1' से शुरू होता है या सीधे किसी बच्चे का नाम है (जैसे: "1 परवेज" या "परवेज"):
               - छात्र डेटा में से उस बच्चे को ढूंढो। 
               - फीस बताते समय 'पाठ्यचर्या शुल्क' या 'पंजीकरण' जैसे कठिन शब्दों का उपयोग बिल्कुल मत करो! 
               - सीधे लिखो: 'महीने की फीस (Tuition Fee)' और 'एडमिशन फीस'। बिल्कुल आसान हिंदी में पॉइंट बनाकर जवाब दो।

            3. अगर इनपुट '2' से शुरू होता है (जैसे: "2 अमित क्लास 7 फीस 500"):
               - चूंकि रेंडर सर्वर रीस्टार्ट होने पर डेटा मिट जाता है, इसलिए ओंकार भाई को बताएं कि इस नए बच्चे को हमेशा के लिए गिटहब की 'data/students.json' फ़ाइल में कैसे जोड़ना है।
               - उन्हें अमित का डेटा एक सही JSON फ़ॉर्मेट कोड ब्लॉक में बनाकर दो, ताकि वो उसे गिटहब में पेस्ट कर सकें।

            4. 如果 इनपुट '3' से शुरू होता है (जैसे: "3 परवेज फीस बाकी है"):
               - ओंकार भाई के लिए पेरेंट्स को भेजने वाला एक बेहद सम्मानजनक, पेशेवर और असरदार व्हाट्सएप मैसेज हिंदी में तैयार करो। अंत में कोचिंग का नाम 'Grace Study Centre' लिखो।

            5. अगर इनपुट '4' से शुरू होता है (जैसे: "4 नए छात्र कैसे लाएं"):
               - ग्रेस स्टडी सेंटर के स्तर के अनुसार छात्रों की संख्या बढ़ाने, बैनर/लोगो वायरल मार्केटिंग करने और कोचिंग को आगे बढ़ाने के 3-4 प्रैक्टिकल और धांसू बिजनेस सुझाव दो।
            """
            
            ai_reply = call_groq(prompt)
            send_whatsapp_message(chat_id, ai_reply)

    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Grace Study Centre Multi-Option Groq Engine is Live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
