import os
import json
from flask import Flask, request, jsonify
import requests
from supabase import create_client, Client

app = Flask(__name__)

# =================================================================
# 🔑 सभी क्रेडेंशियल्स (व्हाट्सएप, एआई और सुपाबेस तिजोरी)
GREEN_API_ID = "7107664395"
GREEN_API_TOKEN = "4857c575c0ff4023a7aeb6bc6ba1813a04b80438d8624857a3"
GROQ_API_KEY = "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"

SUPABASE_URL = "https://gqipeewkjskmgrdkcybf.supabase.co"
SUPABASE_KEY = "sb_publishable_2ObpeusHj4lGZg5NNrKihA_a9ok-l-z"

# सुपाबेस क्लाइंट चालू करना
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# =================================================================

# व्हाट्सएप पर बातचीत की स्थिति (State) याद रखने के लिए मेमोरी बॉक्स
USER_STATES = {}

def send_whatsapp_message(to_number, text):
    url = f"https://api.green-api.com/waInstance{GREEN_API_ID}/sendMessage/{GREEN_API_TOKEN}"
    payload = {"chatId": f"{to_number}@c.us", "message": text}
    headers = {'Content-Type': 'application/json'}
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"मैसेज भेजने में एरर: {e}")

def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"⚠️ Groq सर्वर दिक्कत: {response.status_code}"
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

        # ---- पिलर 1: स्टेप-बाय-स्टेप डेटा एंट्री (Interactive Form System) ----
        if chat_id in USER_STATES:
            state = USER_STATES[chat_id]
            step = state["step"]
            
            if step == 1:
                state["data"]["name"] = message_text
                state["step"] = 2
                send_whatsapp_message(chat_id, "📝 अमित भाई, अब बच्चे का *रोल नंबर* टाइप करके भेजें:")
                return jsonify({"status": "success"}), 200
                
            elif step == 2:
                state["data"]["roll_number"] = message_text
                state["step"] = 3
                send_whatsapp_message(chat_id, "🏫 बच्चे की *क्लास (Class)* टाइप करें:")
                return jsonify({"status": "success"}), 200
                
            elif step == 3:
                state["data"]["class"] = message_text
                state["step"] = 4
                send_whatsapp_message(chat_id, "💰 महीने की *ट्यूशन फीस (Monthly Fee)* कितनी है? सिर्फ नंबर लिखें:")
                return jsonify({"status": "success"}), 200
                
            elif step == 4:
                state["data"]["monthly_fee"] = message_text
                state["step"] = 5
                send_whatsapp_message(chat_id, "🎟️ *एडमिशन फीस (Admission Fee)* कितनी है? (अगर नहीं है तो 0 लिखें):")
                return jsonify({"status": "success"}), 200
                
            elif step == 5:
                state["data"]["admission_fee"] = message_text
                state["step"] = 6
                send_whatsapp_message(chat_id, "⚠️ बच्चे का कोई *बकाया बैलेंस (Pending Balance)* है? (नहीं तो 0 लिखें):")
                return jsonify({"status": "success"}), 200
                
            elif step == 6:
                state["data"]["pending_balance"] = message_text
                state["step"] = 7
                send_whatsapp_message(chat_id, "✍️ बच्चे के बारे में कोई *डिस्क्रिप्शन या नोट* लिखना चाहते हैं? (जैसे: 'अच्छा पढ़ता है' या 'No'):")
                return jsonify({"status": "success"}), 200
                
            elif step == 7:
                state["data"]["description"] = message_text
                state["step"] = 8
                send_whatsapp_message(chat_id, "📸 बच्चे की *फोटो का लिंक (URL)* भेजें (अगर अभी फोटो नहीं है तो 'No' लिख दें):")
                return jsonify({"status": "success"}), 200
                
            elif step == 8:
                state["data"]["photo_url"] = message_text if message_text.lower() != 'no' else ""
                
                # सुपाबेस की तिजोरी (Table) में डेटा सुरक्षित डालना
                try:
                    supabase.table("grace_students").insert(state["data"]).execute()
                    success_text = f"🎉 *मुबारक हो ओंकार भाई!* 🎉\n\n छात्र *{state['data']['name']}* का पूरा बायोडाटा ग्रेस स्टडी सेंटर की सुपाबेस तिजोरी में हमेशा के लिए सुरक्षित सेव कर दिया गया है।"
                    send_whatsapp_message(chat_id, success_text)
                except Exception as e:
                    send_whatsapp_message(chat_id, f"❌ सुपाबेस में सेव करने में दिक्कत आई: {e}")
                
                # डेटा एंट्री खत्म, मेमोरी साफ़ करें
                del USER_STATES[chat_id]
                return jsonify({"status": "success"}), 200

        # ---- सामान्य मेन्यू और कमांड्स ----
        if message_text.startswith('#'):
            user_command = message_text[1:].strip()
            
            # कमांड: नया बच्चा जोड़ना शुरू करें
            if user_command.lower() in ['add', 'जोड़ो', '2']:
                USER_STATES[chat_id] = {"step": 1, "data": {}}
                send_whatsapp_message(chat_id, "🏫 *ग्रेस स्टडी सेंटर डिजिटल फॉर्म चालू* 🏫\n\nओंकार भाई, सबसे पहले नए बच्चे का *पूरा नाम* टाइप करके रिप्लाई करें:")
                return jsonify({"status": "success"}), 200

            # सुपाबेस से लाइव डेटा निकालकर एआई को देना
            try:
                db_response = supabase.table("grace_students").select("*").execute()
                students_list = db_response.data
            except Exception:
                students_list = []
            
            students_context = json.dumps(students_list, indent=2, ensure_ascii=False)
            
            prompt = f"""
            तुम 'Grace Study Centre' कोचिंग के डायरेक्टर ओंकार भाई के पर्सनल व्हाट्सएप बिजनेस असिस्टेंट हो।
            तुम्हारे पास सुपाबेस डेटाबेस से लाइव आया हुआ छात्रों का यह रिकॉर्ड है:
            {students_context}
            
            ओंकार भाई का इनपुट है: "{user_command}"
            
            तुम्हें नीचे दिए गए नियमों के अनुसार केवल सरल, बोलचाल की हिंदी में जवाब देना है:
            
            1. अगर इनपुट खाली है, या 'menu' है, तो उन्हें मुख्य मेन्यू भेजें:
               "🏫 *ग्रेस स्टडी सेंटर असिस्टेंट मेन्यू* 🏫
               
               ओंकार भाई, नीचे दिए गए तरीके से कोड टाइप करें:
               🔹 *#add* - नए बच्चे का सारा बायोडाटा स्टेप-बाय-स्टेप भरने के लिए।
               🔹 *#[बच्चे का नाम]* - उसकी फीस, क्लास और बकाया जानने के लिए (जैसे: #Parvej)।
               🔹 *#3 [नाम] [कारण]* - पेरेंट्स के लिए व्हाट्सएप मैसेज लिखवाने के लिए।
               🔹 *#4 [आपका सवाल]* - कोचिंग की ग्रोथ और वायरल मार्केटिंग के लाइव सुझाव के लिए।"

            2. अगर ओंकार भाई किसी बच्चे का नाम पूछते हैं:
               - रिकॉर्ड में से उस बच्चे को ढूंढो और उसकी महीने की फीस, एडमिशन फीस और बकाया बैलेंस (Pending Balance) पॉइंट बनाकर आसान शब्दों में बताओ।

            3. यदि वे कोई अन्य व्यावसायिक सवाल (जैसे #4 कोचिंग बढ़ाना) पूछते हैं:
               - ग्रेस स्टडी सेंटर के विकास के लिए अपना पूरा दिमाग लगाकर 3-4 प्रैक्टिकल और वायरल मार्केटिंग सुझाव दो।
            """
            
            ai_reply = call_groq(prompt)
            send_whatsapp_message(chat_id, ai_reply)

    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Grace Study Centre Smart Supabase Engine is Live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
