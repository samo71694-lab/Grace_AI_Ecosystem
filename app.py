import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# Page Configuration
st.set_page_config(page_title="Grace Study Centre - AI Portal", layout="wide")

# API Key Configuration
PRIMARY_KEY = "AIzaSy..."  # <-- Yahan apni asli Gemini API Key paste karein
genai.configure(api_key=PRIMARY_KEY)

# Advanced Mobile-Friendly CSS for Side-by-Side Google Bar
st.markdown("""
    <style>
    .main-title { font-size: 38px !important; font-weight: bold; color: #FF4B4B; text-align: center; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 30px; }
    
    /* Mobile aur Desktop dono par elements ko zabardasti ek hi row mein lane ke liye */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: flex-end !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
    }
    
    /* Input box ke container ko bada karne ke liye */
    [data-testid="stHorizontalBlock"] > div:nth-child(1) {
        flex: 4 !important;
        min-width: 0px !important;
    }
    
    /* Mic button ke container ko fit rakhne ke liye */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        flex: 1 !important;
        min-width: 75px !important;
    }
    
    /* Mic button styling */
    div.stButton > button {
        margin-bottom: 4px !important;
        border-radius: 20px !important;
        height: 42px !important;
        width: 100% !important;
        padding: 0px !important;
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

# Row Layout for Input and Mic Button
col1, col2 = st.columns([0.80, 0.20])

with col1:
    # Text input fills automatically when speech_text updates
    user_query = st.text_input(
        "Apna sawal yahan type karein ya bagal mein mic dabakar bolein...", 
        value=st.session_state.speech_text,
        key="text_query",
        label_visibility="collapsed" # Extra space hatane ke liye label hide kiya hai
    )

with col2:
    # Compact Mic Button directly next to the input
    audio_data = mic_recorder(
        start_prompt="🎙️ Boliye",
        stop_prompt="🛑 Rokiye",
        key='google_mic'
    )

# Audio Processing Feedback
if audio_data:
    try:
        st.info("🔄 Audio process ho raha hai...")
        st.session_state.speech_text = "What is kharif crops" 
        st.rerun() # Page ko instant rerun karega taaki box mein text turant dikhe
        
    except Exception as e:
        st.error(f"Mic processing error: {str(e)}")

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
            
            # Clear state after successful run
            st.session_state.speech_text = ""
            
        except Exception as e:
            st.error(f"Error occurring during generation: {str(e)}")