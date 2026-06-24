import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# Page Configuration
st.set_page_config(page_title="Grace Study Centre - AI Portal", layout="wide")

# API Key Configuration
PRIMARY_KEY = "AQ.Ab8RN6KlJlnnY00LlkGukk-Nu6jylXth_aAqZQnJguuobtJPBg"  # <-- Yahan apni asli Gemini API Key paste kar dena
genai.configure(api_key=PRIMARY_KEY)

# Advanced CSS for Exact Google Search Bar Alignment
st.markdown("""
    <style>
    .main-title { font-size: 38px !important; font-weight: bold; color: #FF4B4B; text-align: center; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 30px; }
    
    div[data-testid="stColumn"] {
        display: flex;
        align-items: flex-end !important;
        justify-content: center;
    }
    
    div.stButton > button {
        margin-bottom: 4px !important;
        border-radius: 20px !important;
        height: 42px !important;
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

# Initialize session state for input tracking
if "speech_text" not in st.session_state:
    st.session_state.speech_text = ""

# Google style layout columns
col1, col2 = st.columns([0.88, 0.12])

with col2:
    audio_data = mic_recorder(
        start_prompt="🎙️ Boliye",
        stop_prompt="🛑 Rokiye",
        key='google_mic'
    )

# Real Speech-to-Text Processing Logic
if audio_data:
    try:
        audio_bytes = audio_data['bytes']
        audio_parts = [{"mime_type": "audio/wav", "data": audio_bytes}]
        
        st.info("🔄 Aawaz ko text mein badla ja raha hai...")
        stt_model = genai.GenerativeModel('gemini-1.5-flash')
        stt_response = stt_model.generate_content([
            "Aapka kaam is audio ko sunkar ise text mein badalna (transcribe) hai. Sirf wahi likhein jo bola gaya hai, koi extra gyaan mat dein.", 
            audio_parts[0]
        ])
        st.session_state.speech_text = stt_response.text.strip()
        
    except Exception as e:
        st.error(f"Mic processing error: {str(e)}")

with col1:
    user_query = st.text_input(
        "Apna sawal yahan type karein ya bagal mein mic dabakar bolein...", 
        value=st.session_state.speech_text,
        key="text_query"
    )

# Main AI Text Generation
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
            st.session_state.speech_text = ""
            
        except Exception as e:
            st.error(f"Error occurring during generation: {str(e)}")