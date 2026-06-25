import streamlit as st
import os
import time
import requests
import io
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS

# १. पेज का कॉन्फ़िगरेशन
st.set_page_config(page_title="Grace Study Centre - AI Ecosystem", page_icon="🏫", layout="wide")

# एपीआई की (API Keys)
groq_key = os.environ.get("GROQ_API_KEY", "gsk_jsNWtIwmiR_cmBt0wQrWGdyb3FYKsje1yQBxaid7d1kqn7N7PQt")
cartesia_key = os.environ.get("CARTESIA_API_KEY", "") 

try:
    groq_client = Groq(api_key=groq_key)
except Exception as e:
    st.error(f"Groq Initialization Error: {str(e)}")

# सीएसएस (CSS) स्टाइलिंग
st.markdown("""
    <style>
    .main-title { font-size: 32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 25px; font-size: 16px; }
    .section-box { padding: 20px; border-radius: 10px; background-color: #F9FAFB; border: 1px solid #E5E7EB; margin-bottom: 20px; }
    div.stButton > button { border-radius: 20px !important; height: 42px !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🏫 Grace Study Centre</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Advanced Hybrid Voice Protocol (Single Player Audio Implementation)</div>", unsafe_allow_html=True)

# फाइनल ऑडियो टेक्स्ट क्लीनर इंजन
def final_clean_engine(text):
    if not text:
        return ""
    clean = text.lower()
    garbage_words = [
        "a flat", "e flat", "b flat", "g flat", "a-flat", "e-flat", 
        "1.", "2.", "3.", "4.", "5.", "to omkar", "omkar beta",
        "omkar,", "omkar:", "uddharan chinh", "brackets", "bracket", "verse", "chorus", "hello"
    ]
    for word in garbage_words:
        clean = clean.replace(word, "")
        
    clean = clean.replace("**", "").replace("*", "").replace('"', '').replace('“', '').replace('”', '')
    clean = clean.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
    return clean.strip()

# मेमोरी मैनेजमेंट के लिए सेशन State
if "speech_text" not in st.session_state:
    st.session_state.speech_text = ""

tab1, tab2 = st.tabs(["🎙️ Student Personal Tutor", "📊 Intelligent Tracker & Planner"])

with tab1:
    st.markdown("<div class='section-box'><b>👤 Student Profile Settings (छात्र प्रोफाइल सेटिंग)</b>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns([1, 1, 1, 1])
    with p_col1: nama = st.text_input("Aapka Naam?", value="Omkar")
    with p_col2: class_level = st.selectbox("Class Level:", ["6th", "7th", "8th", "9th", "10th"], index=2)
    with p_col3: subject = st.text_input("Subject Target?", value="Science")
    with p_col4: lang = st.selectbox("Response Bhasha:", ["Standard Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"])
    st.markdown("</div>", unsafe_allow_html=True)

    mode = st.radio("Option (विकल्प):", ["📝 Sirf Text", "🗣️ Bolne wala Teacher Mode (Emotional)", "🎵 Gana / Kavita Mode (Emotional)"], horizontal=True)

    st.markdown("---")
    st.markdown("### 🎤 Sawal Poochen (सवाल पूछें):")

    # माइक इनपुट प्रोसेसिंग
    audio_data = mic_recorder(start_prompt="🎙️ रिकॉर्ड करने के लिए यहाँ दबाएँ", stop_prompt="🛑 रोकने के लिए यहाँ दबाएँ", key='stable_mic_recorder_master')

    if audio_data and audio_data.get("bytes"):
        try:
            file_placeholder = ("temp_audio.wav", audio_data["bytes"], "audio/wav")
            transcription = groq_client.audio.transcriptions.create(file=file_placeholder, model="whisper-large-v3-turbo")
            if transcription.text.strip():
                st.session_state.speech_text = transcription.text
        except:
            pass

    # इनपुट बॉक्स
    user_query = st.text_input("आपका सवाल (माइक से रिकॉर्डेड या टाइप किया हुआ):", value=st.session_state.speech_text)

    # सबमिट बटन
    submit_button = st.button("जवाब जनरेट करें (Submit Question)", type="primary")

    if submit_button and user_query:
        # भाषा और लिपि का सख्त नियम
        script_instruction = ""
        tts_lang = 'hi'
        
        if "हिंदी" in lang:
            script_instruction = "You must output 100% in pure Devanagari Hindi script (हिंदी भाषा). Absolutely NO English alphabets allowed. Use proper full stops (।)."
            tts_lang = 'hi'
        elif "ਪੰਜਾਬੀ" in lang:
            script_instruction = "You must output 100% in pure Gurmukhi Punjabi script (ਪੰਜਾਬੀ ਭਾਸ਼ਾ ਭਾਗ). Do NOT write in English or Hindi. Output purely using Punjabi symbols (ੳ ਅ ੲ ਸ ਹ)."
            tts_lang = 'pa'
        else:
            script_instruction = "Write the text strictly in standard plain school English text only."
            tts_lang = 'en'

        if "Gana" in mode:
            prompt_modifier = f"Aap ek school teacher hain. {class_level} ke student {nama} ko samjhayein. {script_instruction} Your output response must be a beautifully structured kid's rhyming poem (Kavita structure) so it can be sung easily. Keep it short, maximum 2 stanzas."
        else:
            prompt_modifier = f"Aap ek friendly school teacher hain. {class_level} ke student {nama} ko samjhayein. {script_instruction} Simple easy paragraphs without bullets or numbers. Keep it concise so it is easy to read."
            
        full_prompt = f"{prompt_modifier} Topic: {subject}. Question: {user_query}"

        text_container = st.empty()
        
        # चरण १: तुरंत पहली लाइन बोलना (Greeting Line)
        try:
            instant_response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"Generate ONLY ONE short introductory greeting line. You must strictly output 100% in the chosen language script rules: {script_instruction}. Maximum 8 words."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            first_line = instant_response.choices[0].message.content
            text_container.markdown(f"**Teacher:** {first_line}")
        except: 
            first_line = "आइए इसे समझते हैं।"

        # चरण २: पूर्ण विवरण और कंबाइंड सिंगल प्लेयर ऑडियो (Single Master Audio Player)
        with st.spinner("⏳ उत्तर लोड हो रहा है..."):
            try:
                full_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"Provide the full detailed answer text body based on style requested. Put clear commas and full stops to create speech rhythm. Follow script layout strictly: {script_instruction}."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                detailed_text = full_response.choices[0].message.content
                
                # स्क्रीन पर पूरा टेक्स्ट प्रिंट करना
                text_container.markdown(f"**Teacher:** {first_line}\n\n{detailed_text}")
                
                if "Sirf Text" not in mode:
                    # पूरे टेक्स्ट को एक साथ जोड़कर साफ करना
                    full_speech_text = f"{first_line}. {detailed_text}"
                    clean_full_text = final_clean_engine(full_speech_text)
                    
                    # 🎯 जादू: पूरा टेक्स्ट एक ही मास्टर ऑडियो प्लेयर में कंबाइन होगा
                    tts_master = gTTS(text=clean_full_text, lang=tts_lang, slow=False)
                    fp_master = io.BytesIO()
                    tts_master.write_to_fp(fp_master)
                    fp_master.seek(0)
                    
                    # स्क्रीन पर केवल एक ही मास्टर प्लेयर दिखाई देगा
                    st.audio(fp_master, format="audio/mp3")
                    
            except Exception as e: 
                st.error(f"Handover Error: {str(e)}")

        # इनपुट मेमोरी साफ़ करना
        st.session_state.speech_text = ""

with tab2:
    st.markdown("### 📊 Student Progress Tracker Dashboard Active")
