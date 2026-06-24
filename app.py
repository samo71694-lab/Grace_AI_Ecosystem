import streamlit as st
import os
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
from groq import Groq

# ------------------------------------------------------------------
# 1. Page & API Configurations
# ------------------------------------------------------------------
st.set_page_config(page_title="Grace Study Centre - AI Ecosystem", page_icon="🏫", layout="wide")

PRIMARY_KEY = "AIzaSyBnY00L1kGukk-Nu6jy1Xth_aAqZQnJguuobtJPBg"
genai.configure(api_key=PRIMARY_KEY)

groq_key = os.environ.get("GROQ_API_KEY", "")
if groq_key:
    groq_client = Groq(api_key=groq_key)
else:
    groq_client = None

# Advanced CSS Styling
st.markdown("""
    <style>
    .main-title { font-size: 38px !important; font-weight: bold; color: #FF4B4B; text-align: center; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 30px; }
    .card-box { padding: 15px; border-radius: 8px; background-color: #F3F4F6; border-left: 5px solid #1E3A8A; margin-bottom: 15px; }
    
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: flex-end !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) { flex: 4 !important; min-width: 0px !important; }
    [data-testid="stHorizontalBlock"] > div:nth-child(2) { flex: 1 !important; min-width: 75px !important; }
    
    div.stButton > button {
        margin-bottom: 4px !important;
        border-radius: 20px !important;
        height: 42px !important;
        width: 100% !important;
        padding: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 2. Local Database Simulation (Students Tracker Data)
# ------------------------------------------------------------------
students_db = {
    "101": {
        "name": "Aman Sharma",
        "class": "CLASS- 7th",
        "attendance": 85,
        "marks": 72,
        "weak_points": "Trigonometry formulas mein confusion hota hai, sin, cos, tan ke ratios mein galti karta hai. English reading slow hai.",
    },
    "102": {
        "name": "Rohanpreet Singh",
        "class": "CLASS- 7th",
        "attendance": 92,
        "marks": 45,
        "weak_points": "Maths mein basic calculation slow hai, algebra ke linear equations samajhne mein dikkat hoti hai. Test miss karta hai.",
    },
    "103": {
        "name": "Simran Kaur",
        "class": "CLASS- 7th",
        "attendance": 65,
        "marks": 88,
        "weak_points": "Attendance kam hone ki wajah se science ke important experiments aur conceptual classes miss ho gayi hain. Revision ki zarurat hai.",
    },
}

# ------------------------------------------------------------------
# 3. Multi-AI Core Engine Functions (Groq-Based)
# ------------------------------------------------------------------
def ask_deepseek(prompt):
    if not groq_client:
        return "⚠️ Error: GROQ_API_KEY Render ke Environment Variables mein nahi mili! Kripya Render settings check karein."
    try:
        completion = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {"role": "system", "content": "Aap ek expert educational psychologist aur data analyst hain. Bacche ke data ko gahrai se samajhein aur uski kamjori ka sateek conceptual analysis dein."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"DeepSeek Engine Error: {str(e)}"

def ask_llama(prompt):
    if not groq_client:
        return "⚠️ Error: GROQ_API_KEY Render ke Environment Variables mein nahi mili! Kripya Render settings check karein."
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[
                {"role": "system", "content": "Aap Grace Study Centre ke ek experienced senior principal aur strict coordinator hain. Aapko bacche ke liye bilkul practical, ghante-dar-ghante (hourly) ka agle din ka study plan aur timetable likhna hai. Language bilkul simple Hinglish honi chahiye jo bacche aur parents aasani se samajh sakein. Thoda strict rakhna par dulaar aur hausla bhi dena."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Llama Engine Error: {str(e)}"

# ------------------------------------------------------------------
# 4. Main Multi-Agent Navigation Tabs
# ------------------------------------------------------------------
tab1, tab2 = st.tabs(["🎙️ Student Personal Tutor", "📊 Intelligent Tracker & Planner"])

# ==================================================================
# TAB 1: MAIN LEARNING TUTOR PORTAL (Pehle wala Agent)
# ==================================================================
with tab1:
    st.sidebar.title("👤 Student Profile")
    nama = st.sidebar.text_input("Aapka Naam?", value="Omkar")
    class_level = st.sidebar.selectbox("Class Level Chunen:", ["6th", "7th", "8th", "9th", "10th"])
    subject = st.sidebar.text_input("Subject Target?", value="Science")

    st.sidebar.markdown("---")
    st.sidebar.title("🌐 Language Settings")
    lang = st.sidebar.selectbox("Response Bhasha Chunen:", ["Standard Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"])

    st.markdown("### ⚙️ Aapko Jawab Kis Roop Mein Chahiye?")
    mode = st.radio("Option Select Karein:", 
                    ["📝 Sirf Text ke roop mein chahiye", "🗣️ Bolne wala Teacher Mode", "🎵 Gana / Kavita Mode"], index=0)

    st.markdown("---")
    st.markdown("### 🎤 Sawal Poochen:")

    if "speech_text" not in st.session_state:
        st.session_state.speech_text = ""

    col1, col2 = st.columns([0.80, 0.20])

    with col1:
        user_query = st.text_input(
            "Apna sawal yahan type karein ya bagal mein mic dabakar bolein...", 
            value=st.session_state.speech_text,
            key="text_query",
            label_visibility="collapsed"
        )

    with col2:
        audio_data = mic_recorder(start_prompt="🎙️ Boliye", stop_prompt="🛑 Rokiye", key='google_mic')

    if audio_data:
        try:
            st.info("🔄 Audio process ho raha hai...")
            st.session_state.speech_text = "What is kharif crops" 
            st.rerun()
        except Exception as e:
            st.error(f"Mic processing error: {str(e)}")

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
                st.error(f"Error during generation: {str(e)}")

# ==================================================================
# TAB 2: INTELLIGENT TRACKER AGENT (Aapka Naya Agent)
# ==================================================================
with tab2:
    st.markdown("### 📊 Student Progress Tracker & Personalized Multi-AI Study Planner")
    
    t_col1, t_col2 = st.columns([1, 2])

    with t_col1:
        st.subheader("🔍 Student Search Portal")
        search_roll = st.text_input("Enter Student Roll Number (e.g., 101, 102, 103):", value="101", key="tracker_search").strip()
        
        if search_roll in students_db:
            s_data = students_db[search_roll]
            
            st.markdown(f"""
            <div class="card-box">
                <b>👤 Name:</b> {s_data['name']}<br>
                <b>📅 Class:</b> {s_data['class']}<br>
                <b>📈 Current Attendance:</b> {s_data['attendance']}%<br>
                <b>🎯 Mock Test Marks:</b> {s_data['marks']}/100
            </div>
            """, unsafe_allow_html=True)
            
            st.warning(f"**⚠️ Focus Areas (Weak Points):**\n{s_data['weak_points']}")
        else:
            st.error("❌ Yeh Roll Number database mein nahi mila! Kripya 101, 102 ya 103 check karein.")

    with t_col2:
        st.subheader("🤖 AI Automated Agent Engine")
        
        if search_roll in students_db:
            s_data = students_db[search_roll]
            st.info("💡 Yeh system automatic alag-alag AI models (DeepSeek-R1 aur Llama 3.3) ko unki expert field ke hisab se task allocate karta hai.")
            
            if st.button("Generate Personalized AI Action Plan", type="primary", key="btn_tracker"):
                info_context = (
                    f"Student Name: {s_data['name']}, Class: {s_data['class']}, "
                    f"Attendance: {s_data['attendance']}%, Marks: {s_data['marks']}/100, "
                    f"Weak Points: {s_data['weak_points']}"
                )
                
                with st.spinner("🧠 1. DeepSeek-R1 data ka conceptual analysis aur reason dhoondh raha hai..."):
                    ds_prompt = f"Analyze this student data and pinpoint exactly where they need core conceptual help: {info_context}"
                    analysis_result = ask_deepseek(ds_prompt)
                
                st.success("✅ Phase 1: DeepSeek-R1 Core Analysis Completed")
                with st.expander("👁️ View Psychological & Conceptual Analysis", expanded=True):
                    st.write(analysis_result)
                    
                st.markdown("---")
                
                with st.spinner("📅 2. Meta Llama 3.3 agle din ka customized timetable taiyar kar raha hai..."):
                    llama_prompt = (
                        f"Create a strict, encouraging next-day study plan and hour-by-hour timetable in simple Hinglish based on this analysis: {analysis_result}. "
                        f"Address the student directly as a strict but loving mentor from Grace Study Centre."
                    )
                    planner_result = ask_llama(llama_prompt)
                
                st.success("✅ Phase 2: Meta Llama 3.3 Next-Day Study Planner Active")
                st.markdown("### 📋 Personalized Study Plan & Timetable (Hinglish)")
                st.info(planner_result)
        else:
            st.write("Kripya action plan generate karne ke liye baayein taraf ek valid Roll Number dalein.")
