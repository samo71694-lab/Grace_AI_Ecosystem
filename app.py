import streamlit as st
import os
import time
import requests
import io
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS

# १. पेज का कॉन्फ़िगरेशन (मोबाइल और कंप्यूटर दोनों के लिए)
st.set_page_config(page_title="Grace Study Centre - AI Ecosystem", page_icon="🏫", layout="wide")

# रेंडर एनवायरनमेंट से एपीआई की (API Keys) निकालना
groq_key = os.environ.get("GROQ_API_KEY", "gsk_jsNWtIwmiR_cmBt0wQrWGdyb3FYKsje1yQBxaid7d1kqn7N7PQt")
cartesia_key = os.environ.get("CARTESIA_API_KEY", "") 

try:
    groq_client = Groq(api_key=groq_key)
except Exception as e:
    st.error(f"Groq Initialization Error: {str(e)}")

# ऐप को सुंदर बनाने के लिए सीएसएस (CSS)
st.markdown("""
    <style>
    .main-title { font-size: 32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 25px; font-size: 16px; }
    .section-box { padding: 20px; border-radius: 10px; background-color: #F9FAFB; border: 1px solid #E5E7EB; margin-bottom: 20px; }
    .card-box { padding: 15px; border-radius: 8px; background-color: #F3F4F6; border-left: 5px solid #1E3A8A; margin-bottom: 15px; }
    div.stButton > button { border-radius: 20px !important; height: 42px !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🏫 Grace Study Centre</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Advanced Hybrid Voice Protocol (100% Shuddh Hindi Version)</div>", unsafe_allow_html=True)

# फालतू अंग्रेजी के शब्दों को हटाने के लिए क्लीनर इंजन
def final_clean_engine(text):
    if not text:
        return ""
    clean = text.lower()
    
    # हटाने वाले शब्दों की सूची
    garbage_words = [
        "a flat", "e flat", "b flat", "g flat", "a-flat", "e-flat", 
        "1.", "2.", "3.", "4.", "5.", "to omkar", "omkar beta",
        "omkar,", "omkar:", "uddharan chinh", "brackets", "bracket", "verse", "chorus"
    ]
    for word in garbage_words:
        clean = clean.replace(word, "")
        
    clean = clean.replace("**", "").replace("*", "").replace('"', '').replace('“', '').replace('”', '')
    clean = clean.replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "")
    clean = clean.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
    
    clean = " ".join(clean.split())
    return clean.strip()

# डेटाबेस सिमुलेशन (छात्रों का रिकॉर्ड)
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

    if "speech_text" not in st.session_state: st.session_state.speech_text = ""

    col1, col2 = st.columns([0.85, 0.15])
    with col1: user_query = st.text_input("Apna sawal type karein...", value=st.session_state.speech_text, key="text_query", label_visibility="collapsed")
    with col2: audio_data = mic_recorder(start_prompt="🎙️ Boliye", stop_prompt="🛑 Rokiye", key='google_mic')

    if audio_data and audio_data.get("bytes"):
        with st.spinner("🎙️ Processing..."):
            try:
                file_placeholder = ("temp_audio.wav", audio_data["bytes"], "audio/wav")
                transcription = groq_client.audio.transcriptions.create(file=file_placeholder, model="whisper-large-v3-turbo")
                st.session_state.speech_text = transcription.text
                st.rerun()
            except Exception as e: 
                st.warning("⚠️ Browser Mic access issue. Alternately, you can type below directly.")

    if user_query:
        # भाषा और लिपि का सख्त नियम
        script_instruction = ""
        tts_lang = 'hi'
        if "हिंदी" in lang:
            script_instruction = "STRICTLY respond in pure Devanagari Hindi Script (हिंदी अक्षर और देवनागरी लिपि). Absolutely NO English alphabets, NO Hinglish, NO WhatsApp language allowed. Use proper full stops (।) and commas (,) for voice pauses."
            tts_lang = 'hi'
        else:
            script_instruction = "Respond in standard clear English. Use commas and full stops accurately."
            tts_lang = 'en'

        if "Gana" in mode:
            prompt_modifier = f"Aap ek school teacher hain. {class_level} ke student {nama} ko samjhayein. {script_instruction} Your entire output response must strictly be a beautifully structured kid's rhyming poem (Kavita) with strict commas so it can be sung easily. Do not write essays or simple lines."
        else:
            prompt_modifier = f"Aap ek friendly school teacher hain. {class_level} ke student {nama} ko samjhayein. {script_instruction} Straight simple paragraphs without bullets or numbers."
            
        full_prompt = f"{prompt_modifier} Topic: {subject}. Question: {user_query}"

        text_container = st.empty()
        audio_container = st.empty()
        
        # चरण १: तुरंत पहली लाइन बोलना (Instant First Line)
        try:
            instant_response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"Generate ONLY ONE short introductory greeting sentence in this language script format: {script_instruction}. Maximum 10 words. Absolutely no English."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            first_line = instant_response.choices[0].message.content
            text_container.markdown(f"**Teacher:** {first_line}")
            
            if "Sirf Text" not in mode:
                clean_first = final_clean_engine(first_line)
                tts = gTTS(text=clean_first if clean_first else "आइए इसे समझते हैं।", lang=tts_lang, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                audio_container.audio(fp, format="audio/mp3", autoplay=True)
        except: pass

        # चरण २: पूर्ण विवरण और सांस लेने का ठहराव (Full Detailed Explanation with Pauses)
        with st.spinner("⏳ Handover Pipeline Active..."):
            try:
                time.sleep(1.2)
                full_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"Provide the full response answer text based on style requested. Put distinct commas and full stops clearly to create artificial breath pauses. {script_instruction}. No English music nodes."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                detailed_text = full_response.choices[0].message.content
                text_container.markdown(f"**Teacher:** {first_line}\n\n{detailed_text}")
                
                if "Sirf Text" not in mode:
                    clean_detailed = final_clean_engine(detailed_text)
                    
                    # पूर्ण विराम (।) और कॉमा के आधार पर वाक्यों को अलग करके ठहराव देना
                    sentences = clean_detailed.replace("।", ".").split(".")
                    for idx, sentence in enumerate(sentences):
                        if len(sentence.strip()) > 2:
                            tts_segment = gTTS(text=sentence.strip(), lang=tts_lang, slow=False)
                            fp_segment = io.BytesIO()
                            tts_segment.write_to_fp(fp_segment)
                            fp_segment.seek(0)
                            st.audio(fp_segment, format="audio/mp3")
                            # प्राकृतिक सांस लेने के लिए ०.६ सेकंड का ठहराव (Pause)
                            time.sleep(0.6)
            except Exception as e: st.error(f"Handover Error: {str(e)}")

with tab2:
    st.markdown("### 📊 Student Progress Tracker Dashboard Active")
