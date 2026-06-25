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

# एपीआई की (API Keys) निकालना
groq_key = os.environ.get("GROQ_API_KEY", "gsk_jsNWtIwmiR_cmBt0wQrWGdyb3FYKsje1yQBxaid7d1kqn7N7PQt")
cartesia_key = os.environ.get("CARTESIA_API_KEY", "") 

try:
    groq_client = Groq(api_key=groq_key)
except Exception as e:
    st.error(f"Groq Initialization Error: {str(e)}")

# स्टाइलिंग के लिए सीएसएस (CSS)
st.markdown("""
    <style>
    .main-title { font-size: 32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 25px; font-size: 16px; }
    .section-box { padding: 20px; border-radius: 10px; background-color: #F9FAFB; border: 1px solid #E5E7EB; margin-bottom: 20px; }
    div.stButton > button { border-radius: 20px !important; height: 42px !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🏫 Grace Study Centre</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Advanced Hybrid Voice Protocol (Absolute Audio Player Fix)</div>", unsafe_allow_html=True)

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

# डेटाबेस रिकॉर्ड
students_db = {
    "101": {"name": "Aman Sharma", "class": "CLASS- 7th", "weak_points": "Trigonometry ratios mein confusion hai."}
}

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

    if "speech_text" not in st.session_state: 
        st.session_state.speech_text = ""

    col1, col2 = st.columns([0.85, 0.15])
    with col1: 
        user_query = st.text_input("Apna sawal type karein...", value=st.session_state.speech_text, key="text_query", label_visibility="collapsed")
    with col2: 
        audio_data = mic_recorder(start_prompt="🎙️ Boliye", stop_prompt="🛑 Rokiye", key='google_mic_final_v1')

    if audio_data and audio_data.get("bytes"):
        with st.spinner("🎙️ ऑडियो से टेक्स्ट बदला जा रहा है..."):
            try:
                file_placeholder = ("temp_audio.wav", audio_data["bytes"], "audio/wav")
                transcription = groq_client.audio.transcriptions.create(file=file_placeholder, model="whisper-large-v3-turbo")
                if transcription.text.strip():
                    st.session_state.speech_text = transcription.text
                    st.rerun()
            except Exception as e: 
                st.warning("💡 टाइपिंग का उपयोग करके नीचे अपना सवाल लिखें।")

    if user_query:
        # भाषा स्क्रिप्ट निर्धारण
        script_instruction = ""
        tts_lang = 'hi'
        
        if "हिंदी" in lang:
            script_instruction = "You must output 100% in pure Devanagari Hindi script (हिंदी भाषा). Absolutely NO English words. Use proper full stops (।)."
            tts_lang = 'hi'
        elif "ਪੰਜਾਬੀ" in lang:
            script_instruction = "You must output 100% in pure Gurmukhi Punjabi script (ਪੰਜਾਬੀ ਭਾਸ਼ਾ ਭਾਗ). Do NOT write in English or Hindi."
            tts_lang = 'pa'
        else:
            script_instruction = "Write the text strictly in simple standard school English text only."
            tts_lang = 'en'

        if "Gana" in mode:
            prompt_modifier = f"Aap ek school teacher hain. {class_level} ke student {nama} ko samjhayein. {script_instruction} Your output response must be a beautifully structured kid's rhyming poem (Kavita structure) so it can be sung easily."
        else:
            prompt_modifier = f"Aap ek friendly school teacher hain. {class_level} ke student {nama} ko samjhayein. {script_instruction} Simple easy paragraphs without bullets or numbers."
            
        full_prompt = f"{prompt_modifier} Topic: {subject}. Question: {user_query}"

        # ऑडियो और टेक्स्ट के पुराने रीलोडिंग को साफ़ करने के लिए कंटेनर
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
            
            if "Sirf Text" not in mode:
                clean_first = final_clean_engine(first_line)
                tts = gTTS(text=clean_first if clean_first else "आइए समझते हैं।", lang=tts_lang, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                # प्रत्येक ऑडियो प्लेयर को अलग की (Key) दी गई है ताकि पुराना प्लेयर तुरंत रीसेट हो जाए
                st.audio(fp, format="audio/mp3", autoplay=True)
        except: 
            pass

        # चरण २: पूर्ण विवरण ऑडियो ठहराव के साथ
        with st.spinner("⏳ उत्तर लोड हो रहा है..."):
            try:
                time.sleep(1.0)
                full_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"Provide the full detailed answer. Put clear commas and full stops to create speech rhythm. Follow script layout strictly: {script_instruction}."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                detailed_text = full_response.choices[0].message.content
                text_container.markdown(f"**Teacher:** {first_line}\n\n{detailed_text}")
                
                if "Sirf Text" not in mode:
                    clean_detailed = final_clean_engine(detailed_text)
                    
                    # वाक्यों को विभाजित करके ठहराव देना
                    sentences = clean_detailed.replace("।", ".").split(".")
                    
                    for idx, sentence in enumerate(sentences):
                        if len(sentence.strip()) > 2:
                            tts_segment = gTTS(text=sentence.strip(), lang=tts_lang, slow=False)
                            fp_segment = io.BytesIO()
                            tts_segment.write_to_fp(fp_segment)
                            fp_segment.seek(0)
                            # डायनामिक की (Key) ताकि ऑडियो कभी भी अटके नहीं
                            st.audio(fp_segment, format="audio/mp3", key=f"seg_{idx}_{time.time()}")
                            time.sleep(0.6)
            except Exception as e: 
                st.error(f"Handover Error: {str(e)}")

with tab2:
    st.markdown("### 📊 Student Progress Tracker Dashboard Active")
