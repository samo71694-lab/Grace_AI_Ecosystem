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
st.markdown("<div class='subtitle'>Advanced Hybrid Voice Protocol (Language Sync Fixed)</div>", unsafe_allow_html=True)

# FINAL AUDIO TEXT CLEANER ENGINE
def final_clean_engine(text):
    if not text:
        return ""
    clean = text.lower()
    
    # Absolute list of unwanted chords and symbols
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
        # Dynamic Script Enforcement based on selection
        script_instruction = ""
        tts_lang = 'hi'
        
        if "हिंदी" in lang:
            script_instruction = "STRICTLY write the text in Devanagari Hindi script (हिंदी भाषा और देवनागरी लिपि). Absolutely NO English alphabets, NO Hinglish, NO WhatsApp language allowed."
            tts_lang = 'hi'
        elif "ਪੰਜਾਬੀ" in lang:
            script_instruction = "STRICTLY write the text in Gurmukhi Punjabi script (ਪੰਜਾਬੀ ਭਾਸ਼ਾ). Absolutely NO English alphabets."
            tts_lang = 'pa'
        else:
            script_instruction = "Write the text strictly in standard professional English."
            tts_lang = 'en'

        # SUPER STRICT PROMPT FOR LANGUAGE AND SYSTEM STYLE
        if "Gana" in mode:
            prompt_modifier = f"Aap ek school teacher hain. {class_level} ke student {nama} ko samjhayein. {script_instruction} Aapka pura jawab STRICTLY bacchon jaisi mast rhyming kavita (poem) ke roop mein hona chahiye jisme geet jaisa swar ho. Bilkul seedha simple text ya paragraph mat likhna. Strictly no headings, no numbers, no musical scales like A flat, 1., or E flat."
        else:
            prompt_modifier = f"Aap ek friendly school teacher hain. {class_level} ke student {nama} ko samjhayein. {script_instruction} Clean paragraph format mein likhein. Strictly NO structural headers, NO bullets, NO numbers like 1, 2, 3 or musical scale notations."
            
        full_prompt = f"{prompt_modifier} Topic: {subject}. Question: {user_query}"

        text_container = st.empty()
        audio_container = st.empty()
        
        # STEP 1: INSTANT FIRST LINE
        try:
            instant_response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"Generate ONLY ONE short introductory line greeting the child warmly. You must respond strictly in the requested script language system: {script_instruction}. Max 12 words. Strictly NO numbering, NO musical chords like A flat or 1."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            first_line = instant_response.choices[0].message.content
            text_container.markdown(f"**Teacher:** {first_line}")
            
            clean_first = final_clean_engine(first_line)
            
            if "Sirf Text" not in mode:
                tts = gTTS(text=clean_first if clean_first else "Aaiye isey samajhte hain.", lang=tts_lang, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                audio_container.audio(fp, format="audio/mp3", autoplay=True)
        except: pass

        # STEP 2: FULL DETAILED EXPLANATION (KAVITA OR PARAGRAPH)
        with st.spinner("⏳ Handover Engine Active..."):
            try:
                time.sleep(1.2)
                full_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"Generate the full main explanation body text based on the style requested. You must output 100% in the chosen script language format: {script_instruction}. Strictly NO points, NO headers, NO symbols, NO music notes like A-flat, E-flat, or 1."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                detailed_text = full_response.choices[0].message.content
                text_container.markdown(f"**Teacher:** {first_line}\n\n{detailed_text}")
                
                clean_detailed = final_clean_engine(detailed_text)
                
                if "Sirf Text" not in mode:
                    tts_full = gTTS(text=clean_detailed, lang=tts_lang, slow=False)
                    fp_full = io.BytesIO()
                    tts_full.write_to_fp(fp_full)
                    fp_full.seek(0)
                    st.audio(fp_full, format="audio/mp3")
            except Exception as e: st.error(f"Handover Error: {str(e)}")

with tab2:
    st.markdown("### 📊 Student Progress Tracker Dashboard Active")
    search_roll = st.text_input("Enter Student Roll Number:", value="101")
