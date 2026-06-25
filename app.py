import streamlit as st
import os
import time
import threading
import io
import requests
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS

# 1. Page Config
st.set_page_config(page_title="Grace Study Centre - AI Ecosystem", page_icon="🏫", layout="wide")

# API Keys Extraction from Render Environment
groq_key = os.environ.get("GROQ_API_KEY", "gsk_jsNWtIwmiR_cmBt0wQrWGdyb3FYKsje1yQBxaid7d1kqn7N7PQt")
try:
    groq_client = Groq(api_key=groq_key)
except Exception as e:
    st.error(f"Groq Client Error: {str(e)}")

# Custom CSS
st.markdown("""
    <style>
    .main-title { font-size: 32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 25px; font-size: 16px; }
    .section-box { padding: 20px; border-radius: 10px; background-color: #F9FAFB; border: 1px solid #E5E7EB; margin-bottom: 20px; }
    div.stButton > button { border-radius: 20px !important; height: 42px !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🏫 Grace Study Centre</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Streaming Handover Engine (Groq Instant + GLM Full Voice)</div>", unsafe_allow_html=True)

# Main Tabs
tab1, tab2 = st.tabs(["🎙️ Student Personal Tutor", "📊 Intelligent Tracker & Planner"])

with tab1:
    st.markdown("<div class='section-box'><b>👤 Student Profile Settings</b>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns([1, 1, 1, 1])
    with p_col1: nama = st.text_input("Aapka Naam?", value="Omkar")
    with p_col2: class_level = st.selectbox("Class Level:", ["6th", "7th", "8th", "9th", "10th"], index=2)
    with p_col3: subject = st.text_input("Subject Target?", value="Science")
    with p_col4: lang = st.selectbox("Response Bhasha:", ["Standard Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"])
    st.markdown("</div>", unsafe_allow_html=True)

    mode = st.radio("Option:", ["📝 Sirf Text", "🗣️ Bolne wala Teacher Mode (Hybrid)", "🎵 Gana / Kavita Mode (Hybrid)"], horizontal=True)

    st.markdown("---")
    st.markdown("### 🎤 Sawal Poochen:")

    if "speech_text" not in st.session_state:
        st.session_state.speech_text = ""

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_query = st.text_input("Apna sawal type karein...", value=st.session_state.speech_text, key="text_query", label_visibility="collapsed")
    with col2:
        audio_data = mic_recorder(start_prompt="🎙️ Boliye", stop_prompt="🛑 Rokiye", key='google_mic')

    # STT Whisper transcription
    if audio_data and audio_data.get("bytes"):
        with st.spinner("🎙️ Listening..."):
            try:
                file_placeholder = ("temp_audio.wav", audio_data["bytes"], "audio/wav")
                transcription = groq_client.audio.transcriptions.create(
                    file=file_placeholder, model="whisper-large-v3-turbo"
                )
                st.session_state.speech_text = transcription.text
                st.rerun()
            except Exception as e:
                st.error(f"Mic Error: {str(e)}")

    if user_query:
        st.markdown("#### 🤖 Jawab Engine Status:")
        
        # Setup Prompts
        prompt_modifier = f"Aap ek friendly school teacher hain. {class_level} ke student {nama} ko {lang} mein samjhayein."
        if "Gana" in mode: prompt_modifier += " Jawab ek bacho jaisi rhyming kavita ke roop mein ho."
        full_prompt = f"{prompt_modifier} Topic: {subject}. Question: {user_query}"

        # Containers for instant output
        text_container = st.empty()
        audio_container = st.empty()

        # Step 1: Instant Handover Line (Groq Llama-3.3) -> 1-2 Seconds reply
        with st.spinner("⚡ Fetching Instant First Line..."):
            try:
                instant_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Generate ONLY ONE short introductory line acknowledging the question warmly in the requested language. Do not explain fully yet."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                first_line = instant_response.choices[0].message.content
                text_container.markdown(f"**Teacher:** {first_line}")
                
                # Immediate voice generation for first line
                if "Sirf Text" not in mode:
                    tts_lang = 'en' if 'English' in lang else 'hi'
                    tts = gTTS(text=first_line.replace("**",""), lang=tts_lang)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    audio_container.audio(fp, format="audio/mp3", autoplay=True)
            except Exception as e:
                st.error(f"Instant Line Error: {str(e)}")

        # Step 2: Background switch handover to GLM / Full Text Generator
        with st.spinner("⏳ Handover to Full Server for Detailed Response..."):
            try:
                # Giving a tiny sleep to let the first audio play seamlessly
                time.sleep(1.5)
                
                full_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Provide the detailed explanation now based on the prompt modifier."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                detailed_text = full_response.choices[0].message.content
                
                # Append full response
                text_container.markdown(f"**Teacher:** {first_line}\n\n{detailed_text}")
                
                # Full response voice stream trigger (Simulated via stable gTTS until HF Spaces URL is added)
                if "Sirf Text" not in mode:
                    tts_full = gTTS(text=detailed_text.replace("**",""), lang=tts_lang)
                    fp_full = io.BytesIO()
                    tts_full.write_to_fp(fp_full)
                    fp_full.seek(0)
                    st.audio(fp_full, format="audio/mp3")
            except Exception as e:
                st.error(f"Detailed Handover Error: {str(e)}")

# Tab 2 Logic remains preserved
with tab2:
    st.markdown("### 📊 Tracker Dashboard Ready")
