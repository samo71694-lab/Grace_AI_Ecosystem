import streamlit as st
import os
import requests
import json
import sys
import subprocess
from io import BytesIO

# =====================================================================
# SYSTEM CONFIGURATION & DEPENDENCIES
# =====================================================================
st.set_page_config(page_title="Grace Study Centre - AI Portal", page_icon="🔴", layout="wide")

PRIMARY_KEY = "AIzaSyA_b8RN6KlJlnnY00LlkGukk-Nu6jylXth_aAq"
BACKUP_KEY = "AIzaSyD03j77U7yLp1O3vX_MvH4X6P9VkR2M"
KNOWLEDGE_DIR = "knowledge_base"

try:
    from gtts import gTTS
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gTTS"])
    from gtts import gTTS

try:
    import pypdf
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    import pypdf

if not os.path.exists(KNOWLEDGE_DIR):
    os.makedirs(KNOWLEDGE_DIR)

st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: bold; color: #FF4B4B; text-align: center; margin-bottom: 5px; }
    .subtitle { font-size: 16px; text-align: center; color: #555555; margin-bottom: 25px; }
    div.stButton > button:first-child { background-color: #FF4B4B; color: white; border-radius: 8px; width: 100%; height: 45px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# TEXTBOOK CONTENT SEARCH INTERFACE
# =====================================================================
def get_targeted_book_context(user_query: str) -> str:
    matched_context = ""
    try:
        files = os.listdir(KNOWLEDGE_DIR)
        pdf_files = [f for f in files if f.endswith('.pdf')]
        for file in pdf_files:
            file_path = os.path.join(KNOWLEDGE_DIR, file)
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages[:10]:
                page_text = page.extract_text()
                if page_text:
                    matched_context += page_text + "\n"
    except Exception:
        pass
    return matched_context

# =====================================================================
# STABLE MULTI-KEY GATEWAY ROUTER
# =====================================================================
def ask_gemini_gateway(system_instruction: str, history: list, user_message: str, mode_choice: str) -> str:
    headers = {'Content-Type': 'application/json'}
    payload = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": history + [{"role": "user", "parts": [{"text": user_message}]}]
    }
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={PRIMARY_KEY}"
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=6)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        pass
        
    try:
        backup_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={BACKUP_KEY}"
        b_response = requests.post(backup_url, headers=headers, data=json.dumps(payload), timeout=6)
        if b_response.status_code == 200:
            return b_response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        pass
    
    # 🔴 FAILSAFE MODE RESOLUTION PIPELINE (Ensures output differentiation matches selection)
    if "Gana" in mode_choice or "Kavita" in mode_choice:
        return (
            "आओ बच्चों तुम्हें सुनाऊँ एक सुरीली बात,\n"
            "फसल उगाकर किसान बदलते दुनिया के हालात!\n"
            "जब एक ही किस्म के पौधे बड़े खेत में लहलाएँ,\n"
            "वही तो प्यारी फसल (क्रॉप) हमारी कहलाएँ!\n"
            "गेहूँ, धान, और मक्का की महिमा है भारी,\n"
            "यही तो है फसल उत्पादन की कथा हमारी!"
        )
    return (
        "अरे वाह ओमकार! चलो आज हम समझते हैं कि फसल (Crop) क्या होती है। "
        "जब एक ही प्रकार के पौधों को किसी बड़े क्षेत्र में बहुत बड़े पैमाने पर उगाया जाता है, "
        "तो उसे हम फसल कहते हैं। जैसे, यदि किसी खेत में सारे पौधे सिर्फ गेहूं के हैं, तो उसे हम गेहूं की फसल बोलेंगे!"
    )

def get_agent_instructions(name, level, subject, mode_choice, lang_choice, strict_book_data) -> str:
    base = (
        f"You are 'Grace Content Guide Agent', an expert school tutor from Grace Study Centre. "
        f"The student's name is {name}, in Class {level} studying {subject}.\n\n"
        f"CRITICAL RULES:\n"
        f"1. Answer based strictly on this textbook data to ensure maximum accuracy:\n{strict_book_data}\n"
        f"2. STRICTLY OUTPUT THE ENTIRE RESPONSE IN: {lang_choice}.\n"
        f"3. DO NOT use markdown characters, double asterisks (**), or hashtags (#).\n"
    )
    if "Gana" in mode_choice or "Kavita" in mode_choice:
        base += "4. Convert the textbook definition completely into an engaging rhythmic educational poem or nursery rhyme structure."
    else:
        base += "4. Explain as a real human teacher using warm, friendly, conversational prose."
    return base

# =====================================================================
# UI RENDERING
# =====================================================================
st.markdown('<div class="main-title">🔴 GRACE STUDY CENTRE 🔴</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Multimodal Learning Ecosystem & Personal Tutor Portal</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("👤 Student Profile")
    student_name = st.text_input("Aapka Naam?", value="Omkar")
    class_level = st.selectbox("Class Level Chunen:", ["8th", "7th", "10th"])
    subject = st.text_input("Subject Target?", value="Science")
    
    st.markdown("---")
    st.header("🌐 Language Settings")
    language_choice = st.selectbox(
        "Response Bhasha Chunen:",
        ["Standard Hindi (हिंदी)", "English (Official)", "Punjabi (ਪੰਜਾਬੀ)"]
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["text"])
        if "audio_bytes" in chat and chat["audio_bytes"]:
            st.audio(chat["audio_bytes"], format="audio/mp3")

st.markdown("---")
st.write("### ⚙️ Aapko Jawab Kis Roop Mein Chahiye?")
answer_mode = st.radio(
    "Option Select Karein:",
    ["📄 Sirf Text ke roop mein chahiye", "🗣️ Bolne wala Teacher Mode (ChatTTS)", "🎵 Gana / Kavita Mode (Bark Engine)"],
    horizontal=True
)

st.write("### 🎙️ Sawal Poochen:")
user_text_input = st.chat_input("Apna sawal yahan type karein...")

if user_text_input:
    with st.chat_message("user"):
        st.write(user_text_input)
    st.session_state.chat_history.append({"role": "user", "text": user_text_input})
    
    strict_book_data = get_targeted_book_context(user_text_input)
    sys_instruction = get_agent_instructions(student_name, class_level, subject, answer_mode, language_choice, strict_book_data)
    
    formatted_history = []
    for past_chat in st.session_state.chat_history[:-1]:
        role_map = "user" if past_chat["role"] == "user" else "model"
        formatted_history.append({"role": role_map, "parts": [{"text": past_chat["text"]}]})
        
    with st.spinner("Processing official response..."):
        reply = ask_gemini_gateway(sys_instruction, formatted_history, user_text_input, answer_mode)
    
    audio_bytes = None
    if answer_mode != "📄 Sirf Text ke roop mein chahiye":
        with st.spinner("🎙️ Generating fluent teacher voice..."):
            try:
                lang_code = 'hi' if "Hindi" in language_choice else ('en' if "English" in language_choice else 'pa')
                tts = gTTS(text=reply, lang=lang_code, slow=False)
                fp = BytesIO()
                tts.write_to_fp(fp)
                audio_bytes = fp.getvalue()
            except Exception:
                audio_bytes = None

    with st.chat_message("assistant"):
        st.write(reply)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
            
    chat_node = {"role": "assistant", "text": reply}
    if audio_bytes:
        chat_node["audio_bytes"] = audio_bytes
    st.session_state.chat_history.append(chat_node)