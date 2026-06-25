import streamlit as st
import os
import time
import requests
import io
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS

# 1. Page Configuration
st.set_page_config(page_title="Grace Study Centre - AI Ecosystem", page_icon="🏫", layout="wide")

# API Keys Extraction
groq_key = os.environ.get("GROQ_API_KEY", "gsk_jsNWtIwmiR_cmBt0wQrWGdyb3FYKsje1yQBxaid7d1kqn7N7PQt")
cartesia_key = os.environ.get("CARTESIA_API_KEY", "") 

try:
    groq_client = Groq(api_key=groq_key)
except Exception as e:
    st.error(f"Groq Initialization Error: {str(e)}")

# Custom CSS
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
st.markdown("<div class='subtitle'>Advanced Hybrid Voice Protocol (Fix: Absolute Audio Cleaning Active)</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 🔥 JAD SE KHATAM FILTER: JORDAAR TEXT CLEANER
# ------------------------------------------------------------------
def final_clean_engine(text):
    if not text:
        return ""
    
    # Lowercase mein badalna taaki CHOTE-BADE saare akshar catch ho sakein
    clean = text.lower()
    
    # 1. Pichli dikkat wale saare music notes aur kachra shabdon ko gayab karna
    garbage_words = [
        "a flat", "e flat", "b flat", "g flat", "a-flat", "e-flat", 
        "1.", "2.", "3.", "4.", "5.", "to omkar", "omkar beta",
        "omkar,", "omkar:", "uddharan chinh", "brackets", "bracket"
    ]
    for word in garbage_words:
        clean = clean.replace(word, "")
        
    # 2. Saare symbols aur numbers saaf karna
    clean = clean.replace("**", "").replace("*", "").replace('"', '').replace('“', '').replace('”', '')
    clean = clean.replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "")
    clean = clean.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
    
    # Double spaces ko single space mein badalna
    clean = " ".join(clean.split())
    return clean.strip()

# Local Database Simulation
students_db = {
    "101": {"name": "Aman Sharma", "class": "CLASS- 7th", "attendance": 85, "marks": 72, "weak_points": "Trigonometry ratios mein galti karta hai."},
    "102": {"name": "Rohanpreet Singh", "class": "CLASS- 7th", "attendance": 92, "marks": 45, "weak_points": "Algebra ke linear equations mein dikkat hoti hai."},
    "103": {"name": "Simran Kaur", "class": "CLASS- 7th", "attendance": 65, "marks": 88, "weak_points": "Conceptual classes miss ho gayi hain."}
}

def ask_deepseek(prompt):
    try:
        completion = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except: return "DeepSeek Processing completed."

def ask_llama(prompt):
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except: return "Llama Processing completed."

tab1, tab2 = st.tabs(["🎙️ Student Personal Tutor", "📊 Intelligent Tracker & Planner"])

with tab1:
    st.markdown("<div class='section-box'><b>👤 Student Profile Settings</b>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns([1, 1, 1, 1])
    with p_col1: nama = st.text_input("Aapka Naam?", value="Omkar")
    with p_col2: class_level = st.selectbox("Class Level:", ["6th", "7th", "8th", "9th", "10th"], index=2)
    with p_col3: subject = st.text_input("Subject Target?", value="Science")
    with p_col4: lang = st.selectbox("Response Bhasha:", ["Standard Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"])
    st.markdown("</div>", unsafe_allow_html=True)

    mode = st.radio("Option:", ["📝 Sirf Text", "🗣️ Bolne wala Teacher Mode (Emotional)", "🎵 Gana / Kavita Mode (Emotional)"], horizontal=True)

    st.markdown("---")
    st.markdown("### 🎤 Sawal Poochen:")

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
            except Exception as e: st.error(f"Mic Error: {str(e)}")

    if user_query:
        # Strict Prompt Customization
        prompt_modifier = f"Aap ek friendly school teacher hain. {class_level} ke student {nama} ko {lang} mein samjhayein. DO NOT include any structural headers, bullets, or musical scale references like A flat, 1., or E flat in your output text."
        if "Gana" in mode: prompt_modifier += " Provide the response strictly as a rhythmic rhyme story for kids without using notes."
        full_prompt = f"{prompt_modifier} Topic: {subject}. Question: {user_query}"

        text_container = st.empty()
        audio_container = st.empty()
        
        # STEP 1: INSTANT FIRST LINE
        try:
            instant_response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Generate ONLY ONE short conversational line greeting the child and validating the question warmly. Strictly NO numbering, NO markdown, NO music chords like A flat, 1., or E flat."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            first_line = instant_response.choices[0].message.content
            text_container.markdown(f"**Teacher:** {first_line}")
            
            clean_first = final_clean_engine(first_line)
            
            if "Sirf Text" not in mode:
                tts = gTTS(text=clean_first if clean_first else "Aaiye isey samajhte hain.", lang='hi' if 'Hindi' in lang else 'en', slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                audio_container.audio(fp, format="audio/mp3", autoplay=True)
        except: pass

        # STEP 2: FULL DETAILED EXPLANATION 
        with st.spinner("⏳ Handover Engine Active..."):
            try:
                time.sleep(1.2)
                full_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Provide full detailed plain paragraph explanation. Strictly DO NOT use bullets, numbers, points, or musical scale notations like A-flat, E-flat, or 1."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                detailed_text = full_response.choices[0].message.content
                text_container.markdown(f"**Teacher:** {first_line}\n\n{detailed_text}")
                
                # Cleaning full output through final filter engine
                clean_detailed = final_clean_engine(detailed_text)
                
                if "Sirf Text" not in mode:
                    st.info("ℹ️ Streaming full audio block seamlessly.")
                    tts_full = gTTS(text=clean_detailed, lang='hi' if 'Hindi' in lang else 'en', slow=False)
                    fp_full = io.BytesIO()
                    tts_full.write_to_fp(fp_full)
                    fp_full.seek(0)
                    st.audio(fp_full, format="audio/mp3")
            except Exception as e: st.error(f"Handover Error: {str(e)}")

with tab2:
    st.markdown("### 📊 Student Progress Tracker Dashboard Active")
    search_roll = st.text_input("Enter Student Roll Number:", value="101")
