import streamlit as st
import os
from google import genai
from google.genai import types
from streamlit_mic_recorder import mic_recorder
from groq import Groq

# ------------------------------------------------------------------
# 1. Page Configuration (Mobile & Desktop Responsive)
# ------------------------------------------------------------------
st.set_page_config(page_title="Grace Study Centre - AI Ecosystem", page_icon="🏫", layout="wide")

# Backend bypass logic for AQ format keys
PRIMARY_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KZggKwyiDgbgGj2L-SpZr4cVVwdqTyX5eRXKyhSzWwVw")

try:
    # Explicitly client initialization to prevent 401 OAuth token fallback
    ai_client = genai.Client(api_key=PRIMARY_KEY)
except Exception as e:
    st.error(f"Google Client Initialization Error: {str(e)}")

groq_key = os.environ.get("GROQ_API_KEY", "")
if groq_key:
    groq_client = Groq(api_key=groq_key)
else:
    groq_client = None

# Custom CSS for Professional Layout
st.markdown("""
    <style>
    .main-title { font-size: 32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 25px; font-size: 16px; }
    .section-box { padding: 20px; border-radius: 10px; background-color: #F9FAFB; border: 1px solid #E5E7EB; margin-bottom: 20px; }
    .card-box { padding: 15px; border-radius: 8px; background-color: #F3F4F6; border-left: 5px solid #1E3A8A; margin-bottom: 15px; }
    
    [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        gap: 10px !important;
    }
    div.stButton > button {
        border-radius: 20px !important;
        height: 42px !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🏫 Grace Study Centre</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI Multimodal Learning Ecosystem & Intelligent Planner</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 2. Local Database Simulation
# ------------------------------------------------------------------
students_db = {
    "101": {"name": "Aman Sharma", "class": "CLASS- 7th", "attendance": 85, "marks": 72, "weak_points": "Trigonometry formulas mein confusion hota hai, sin, cos, tan ke ratios mein galti karta hai. English reading slow hai."},
    "102": {"name": "Rohanpreet Singh", "class": "CLASS- 7th", "attendance": 92, "marks": 45, "weak_points": "Maths mein basic calculation slow hai, algebra ke linear equations samajhne mein dikkat hoti hai. Test miss karta hai."},
    "103": {"name": "Simran Kaur", "class": "CLASS- 7th", "attendance": 65, "marks": 88, "weak_points": "Attendance kam hone ki wajah se science ke important experiments aur conceptual classes miss ho gayi hain. Revision ki zarurat hai."}
}

# ------------------------------------------------------------------
# 3. Core AI Engines
# ------------------------------------------------------------------
def ask_deepseek(prompt):
    if not groq_client: return "⚠️ GROQ_API_KEY environment variable mein nahi mili."
    try:
        completion = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "system", "content": "Aap ek expert educational psychologist aur data analyst hain. Data ka sateek analysis dein."}, {"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e: return f"DeepSeek Error: {str(e)}"

def ask_llama(prompt):
    if not groq_client: return "⚠️ GROQ_API_KEY environment variable mein nahi mili."
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[{"role": "system", "content": "Aap Grace Study Centre ke senior coordinator hain. Hinglish mein customized hour-by-hour timetable banayein."}, {"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e: return f"Llama Error: {str(e)}"

# ------------------------------------------------------------------
# 4. Main Tabs Navigation
# ------------------------------------------------------------------
tab1, tab2 = st.tabs(["🎙️ Student Personal Tutor", "📊 Intelligent Tracker & Planner"])

# ==================================================================
# TAB 1: TUTOR PORTAL (Bypass Auth Patched)
# ==================================================================
with tab1:
    st.markdown("<div class='section-box'><b>👤 Student Profile Settings (Mobile & Desktop Friendly)</b>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns([1, 1, 1, 1])
    with p_col1: nama = st.text_input("Aapka Naam?", value="Omkar")
    with p_col2: class_level = st.selectbox("Class Level:", ["6th", "7th", "8th", "9th", "10th"], index=2)
    with p_col3: subject = st.text_input("Subject Target?", value="Science")
    with p_col4: lang = st.selectbox("Response Bhasha:", ["Standard Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### ⚙️ Jawab Ka Roop:")
    mode = st.radio("Option:", ["📝 Sirf Text", "🗣️ Bolne wala Teacher Mode", "🎵 Gana / Kavita Mode"], horizontal=True)

    st.markdown("---")
    st.markdown("### 🎤 Sawal Poochen:")

    if "speech_text" not in st.session_state:
        st.session_state.speech_text = ""

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_query = st.text_input(
            "Apna sawal type karein...", 
            value=st.session_state.speech_text,
            key="text_query",
            label_visibility="collapsed"
        )
    with col2:
        audio_data = mic_recorder(start_prompt="🎙️ Boliye", stop_prompt="🛑 Rokiye", key='google_mic')

    if audio_data:
        st.session_state.speech_text = "What is crops"
        st.rerun()

    if user_query:
        with st.spinner("🧠 AI Jawab tayaar kar raha hai..."):
            try:
                prompt_modifier = f"Aap ek friendly school teacher hain. {class_level} ke student ke dimaag ke mutabik {lang} bhasha mein samjhayein."
                if "Gana / Kavita" in mode:
                    prompt_modifier += " Jawab ek bacho jaisi rhyming kavita ke roop mein hona chahiye."
                
                full_prompt = f"{prompt_modifier} Student: {nama}. Topic: {subject}. Question: {user_query}"
                
                # Direct API Key injection call to strictly bypass 401 OAuth issues
                response = ai_client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=full_prompt
                )
                st.markdown("#### 🤖 Jawab:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error during generation: {str(e)}")

# ==================================================================
# TAB 2: TRACKER PORTAL
# ==================================================================
with tab2:
    st.markdown("### 📊 Student Progress Tracker")
    t_col1, t_col2 = st.columns([1, 2])

    with t_col1:
        search_roll = st.text_input("Enter Student Roll Number (101, 102, 103):", value="101", key="tab2_search").strip()
        if search_roll in students_db:
            s_data = students_db[search_roll]
            st.markdown(f"""
            <div class="card-box">
                <b>👤 Name:</b> {s_data['name']}<br>
                <b>📅 Class:</b> {s_data['class']}<br>
                <b>📈 Attendance:</b> {s_data['attendance']}%<br>
                <b>🎯 Mock Marks:</b> {s_data['marks']}/100
            </div>
            """, unsafe_allow_html=True)
            st.warning(f"**Focus Areas:**\n{s_data['weak_points']}")
        else:
            st.error("❌ Invalid Roll Number.")

    with t_col2:
        if search_roll in students_db:
            s_data = students_db[search_roll]
            if st.button("Generate Personalized AI Action Plan", type="primary", key="tab2_btn"):
                info_context = f"Student: {s_data['name']}, Weak Points: {s_data['weak_points']}"
                with st.spinner("DeepSeek Analysis..."):
                    analysis = ask_deepseek(f"Analyze: {info_context}")
                st.success("Base 1: DeepSeek Analysis Completed")
                st.write(analysis)
                
                with st.spinner("Llama Planning..."):
                    plan = ask_llama(f"Create Hinglish timetable for: {analysis}")
                st.info(plan)
