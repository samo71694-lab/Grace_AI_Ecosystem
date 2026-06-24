import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import os

# Page Configuration
st.set_page_config(page_title="Grace Study Centre - AI Portal", layout="wide")

# API Key Configuration
PRIMARY_KEY = "AQ.Ab8RN6KlJlnnY00LlkGukk-Nu6jylXth_aAqZQnJguuobtJPBg"  # <-- Yahan apni asli Gemini API Key paste karein
genai.configure(api_key=PRIMARY_KEY)

# Custom CSS for Google-like Input Layout
st.markdown("""
    <style>
    .main-title { font-size: 38px !important; font-weight: bold; color: #FF4B4B; text-align: center; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 30px; }
    div[data-testid="stColumn"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar - Student Profile
st.sidebar.title("👤 Student Profile")
nama = st.sidebar.text_input("Aapka Naam?", value="Omkar")
class_level = st.sidebar.selectbox("Class Level Chunen:", ["6th", "7th", "8th", "9th", "10th"])
subject = st.sidebar.text_input("Subject Target?", value="Science")

st.sidebar.markdown("---")
st.sidebar.title("🌐 Language Settings")
lang = st.sidebar.selectbox("Response Bhasha Chunen:", ["Standard Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"])

# Main UI Header
st.markdown("<div class='main-title'>🔴 GRACE STUDY CENTRE 🔴</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI Multimodal Learning Ecosystem & Personal Tutor Portal</div>", unsafe_allow_html=True)

st.markdown("### ⚙️ Aapko Jawab Kis Roop Mein Chahiye?")
mode = st.radio("Option Select Karein:", 
                ["📝 Sirf Text ke roop mein chahiye", 
                 "🗣️ Bolne wala Teacher Mode", 
                 "🎵 Gana / Kavita Mode"], index=0)

st.markdown("---")
st.markdown("### 🎤 Sawal Poochen:")

# Initialize session state to hold transcribed text
if "speech_text" not in st.session_state:
    st.session_state.speech_text = ""

# --- GOOGLE STYLE SIDE-BY-SIDE LAYOUT ---
# Creating columns: 85% width for input box, 15% for the microphone button
col1, col2 = st.columns([0.85, 0.15])

with col2:
    # Google style compact mic recorder
    audio_data = mic_recorder(
        start_prompt="🎙️ Boliye",
        stop_prompt="🛑 Rokiye",
        key='google_mic'
    )

# Process speech to text if audio is recorded
if audio_data:
    # In full implementation, bytes are converted to text using an audio-to-text pipeline
    # For now, we simulate the text confirmation or you can route it through a whisper/gemini model
    st.session_state.speech_text = "What is kharif crops" # Live integration text fill placeholder

with col1:
    # The text input box will automatically populate with speech text if available
    user_query = st.text_input(
        "Apna sawal yahan type karein ya bagal mein mic dabakar bolein...", 
        value=st.session_state.speech_text,
        key="text_query"
    )

# Audio feedback display below the input row if recorded
if audio_data:
    st.audio(audio_data['bytes'], format='audio/wav')
    st.success(f"✍️ Auto-Typed from Voice: '{st.session_state.speech_text}'")

# Final execution logic
if user_query:
    with st.spinner("🧠 AI soch raha hai aur jawab tayaar kar raha hai..."):
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt_modifier = ""
            if "Gana / Kavita" in mode:
                prompt_modifier = "Bachon ko samjhane ke liye ek bacho jaisi kavita ya gaane ke roop mein jawab dein. Expressions aur rhyming lines honi chahiye."
            else:
                prompt_modifier = f"Aap ek friendly school teacher hain. {class_level} ke student ke dimaag ke mutabik aasan shabdon mein samjhayein."
            
            full_prompt = f"{prompt_modifier} Student Name: {nama}. Subject: {subject}. Bhasha: {lang}. Sawal: {user_query}"
            
            response = model.generate_content(full_prompt)
            st.markdown(f"#### 🤖 Jawab ({mode}):")
            st.write(response.text)
            
            # Reset the session state after processing so it doesn't get stuck
            st.session_state.speech_text = ""
            
        except Exception as e:
            st.error(f"Error occurring during generation: {str(e)}")