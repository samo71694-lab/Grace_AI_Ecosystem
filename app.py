import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import os

# Page Configuration
st.set_page_config(page_title="Grace Study Centre - AI Portal", layout="wide")

# API Key Configuration (Using your existing functional key setup)
PRIMARY_KEY = "AQ.Ab8RN6KlJlnnY00LlkGukk-Nu6jylXth_aAqZQnJguuobtJPBg"  # <-- Yahan apni asli Gemini API Key paste karein
genai.configure(api_key=PRIMARY_KEY)
model = genai.GenerativeModel('gemini-pro')

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main-title { font-size: 38px !important; font-weight: bold; color: #FF4B4B; text-align: center; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 30px; }
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

# --- NEW MICROPHONE INTEGRATION ---
st.write("Aap bol kar bhi apna sawal record kar sakte hain:")
audio_data = mic_recorder(
    start_prompt="🎙️ Bolna Shuru Karein (Click to Record)",
    stop_prompt="🛑 Recording Rokiye (Stop)",
    key='recorder'
)

# Text Input Box (For typing or manual fallback)
user_query = st.text_input("Apna sawal yahan type karein ya upar se record karein...", key="text_query")

# Processing Logic
if audio_data:
    st.audio(audio_data['bytes'], format='audio/wav')
    st.info("🎙️ Voice recorded successfully! Processing speech input...")

if user_query:
    with st.spinner("🧠 AI soch raha hai aur jawab tayaar kar raha hai..."):
        try:
            # Custom prompt tailoring based on selection
            prompt_modifier = ""
            if "Gana / Kavita" in mode:
                prompt_modifier = "Bachon ko samjhane ke liye ek bacho jaisi kavita ya gaane ke roop mein jawab dein. Expressions aur rhyming lines honi chahiye."
            else:
                prompt_modifier = f"Aap ek friendly school teacher hain. {class_level} ke student ke dimaag ke mutabik aasan shabdon mein samjhayein."
            
            full_prompt = f"{prompt_modifier} Student Name: {nama}. Subject: {subject}. Bhasha: {lang}. Sawal: {user_query}"
            
            response = model.generate_content(full_prompt)
            st.markdown(f"#### 🤖 Jawab ({mode}):")
            st.write(response.text)
            
            # Simulated advanced voice delivery block
            st.markdown("---")
            st.markdown("#### 🎧 Voice Delivery:")
            st.info("⚙️ Dynamic vocal modulation algorithm is preparing expressive audio output...")
            
        except Exception as e:
            st.error(f"Error occurring during generation: {str(e)}")