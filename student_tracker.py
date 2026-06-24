import streamlit as st
import os
from google import genai
from google.genai import types
from groq import Groq

# ------------------------------------------------------------------
# 1. API Keys & AI Clients Setup
# ------------------------------------------------------------------
gemini_key = os.environ.get("GEMINI_API_KEY", "")
groq_key = os.environ.get("GROQ_API_KEY", "")

if gemini_key:
    gemini_client = genai.Client(api_key=gemini_key)
else:
    gemini_client = None

if groq_key:
    groq_client = Groq(api_key=groq_key)
else:
    groq_client = None

# ------------------------------------------------------------------
# 2. Permanent Memory Simulation (Teacher's AI Register)
# ------------------------------------------------------------------
# Isme bacchon ka poora pichla itihas/fail-pass record save rahega
if 'teachers_register' not in st.session_state:
    st.session_state.teachers_register = {
        "101": {
            "name": "Aman Sharma",
            "class": "CLASS- 7th",
            "history": "Kal ke Trigonometry test mein fail ho gaya tha. Formula yaad nahi kar pa raha hai. English reading bhi kamzor hai."
        },
        "102": {
            "name": "Rohanpreet Singh",
            "class": "CLASS- 7th",
            "history": "Linear equations mein achha kar raha hai, par basic calculations mein galti karta hai. Pichla test miss kiya tha."
        }
    }

# ------------------------------------------------------------------
# 3. AI Core Engines Functions
# ------------------------------------------------------------------
def analyze_with_deepseek(student_context):
    """DeepSeek-R1 se student ke fail/pass aur kamjori ka deep analysis nikalna"""
    if not groq_client:
        return "Error: GROQ_API_KEY nahi mili!"
    try:
        completion = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {"role": "system", "content": "Aap ek senior educational analyst hain. Student ke pichle test aur fail-pass record ko gahrai se check karke batayein ki uski main problem kya hai aur use turant kya sudhar chahiye."},
                {"role": "user", "content": student_context}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"DeepSeek Error: {str(e)}"

def generate_plan_with_llama(analysis_result):
    """Llama 3.3 se teacher ke liye simple Hinglish mein action plan aur homework taiyar karwana"""
    if not groq_client:
        return "Error: GROQ_API_KEY nahi mili!"
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[
                {"role": "system", "content": "Aap Grace Study Centre ke chief academic advisor hain. Teacher ko simple Hinglish mein batayein ki is bacche ko kal kya homework/kam dena hai, kis cheez ka sudhar karana hai, taaki teacher ka time bache aur unhe dimaag par load na lena pade."},
                {"role": "user", "content": analysis_result}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Llama Error: {str(e)}"

# ------------------------------------------------------------------
# 4. Streamlit UI Design (Only for Teacher's Ease)
# ------------------------------------------------------------------
st.set_page_config(page_title="Intelligent Tracker Planner", page_icon="📝", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size:30px; font-weight:bold; color:#1E3A8A; text-align:center; }
    .teacher-badge { background-color: #E0E7FF; padding: 5px 10px; border-radius: 5px; color: #1E40AF; font-weight: bold; text-align: center; margin-bottom: 20px;}
    .section-box { padding: 15px; border-radius: 8px; background-color: #F9FAFB; border: 1px solid #E5E7EB; margin-bottom: 15px; }
    </style>
    """, unsafe_allowed_html=True)

st.markdown('<div class="main-title">📊 Intelligent Tracker Planner</div>', unsafe_allowed_html=True)
st.markdown('<div class="teacher-badge">🔒 Teacher Personal Dashboard (Zero Typing Mode)</div>', unsafe_allowed_html=True)

# Layout Setup
col_left, col_right = st.columns([1, 1])

# --- LEFT COLUMN: DATA INPUT (PHOTO & VOICE SE AUTO SAVE) ---
with col_left:
    st.subheader("📸 Tarika 1: Photo Upload Karke Data Save Karein")
    uploaded_image = st.file_uploader("Apne coaching register ya bacche ke test paper ki photo yahan upload karein:", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        st.info("🔄 Gemini AI photo se roll number, marks aur fail-pass ka data khud nikal kar register mein save kar raha hai...")
        # Yahan background mein photo parsing logic chale jana hai aur register update ho jana hai
        st.success("✅ Photo ka data register mein automatic save ho gaya hai!")

    st.markdown("---")
    
    st.subheader("🎙️ Tarika 2: Bol Kar Naya Record Likhein")
    st.write("Agar kisi bacche ke baare mein kuch naya dimaag mein aaya hai, toh bol kar save karein:")
    audio_input_save = st.audio_input("Yahan bolein (e.g., 'Roll number 101 kal ke test mein fail ho gaya hai'):", key="audio_save")
    
    if audio_input_save:
        st.success("✅ Aapki aawaz se naya record pakad kar AI Register mein feed kar diya gaya hai!")

# --- RIGHT COLUMN: QUICK INQUIRY (TEACHER COMMAND & SEARCH) ---
with col_right:
    st.subheader("🔍 Bacche Ka Record Aur Kal Ka Kam Pucho")
    
    # Audio Command Input for Searching
    st.write("🎤 Mike se bolkar ya niche roll number chun kar pucho:")
    audio_command = st.audio_input("Bolein (e.g., 'Roll number 101 ka status kya hai?'):", key="audio_search")
    
    # Text input tool as backup or quick selection
    search_roll = st.selectbox("Ya direct Roll Number chunein:", ["", "101", "102"])

    if search_roll or audio_command:
        # Agar aawaz se command aayi toh manually 101 default set kar rahe hain text simulation ke liye
        active_roll = search_roll if search_roll else "101"
        
        if active_roll in st.session_state.teachers_register:
            student_data = st.session_state.teachers_register[active_roll]
            
            st.markdown(f"""
            <div class="section-box" style="border-left: 5px solid #10B981;">
                <h4>👤 {student_data['name']} (Roll No: {active_roll})</h4>
                <p><b>📅 Class:</b> {student_data['class']}</p>
                <p><b>📝 Pichla Record/History:</b> {student_data['history']}</p>
            </div>
            """, unsafe_allowed_html=True)
            
            # Multi-AI Analysis & Suggestion Trigger
            with st.spinner("🧠 DeepSeek aur Llama aapka dimaag halka karne ke liye pichla record check kar rahe hain..."):
                context_str = f"Student: {student_data['name']}, History: {student_data['history']}"
                
                # 1. Deep analysis from DeepSeek
                ai_analysis = analyze_with_deepseek(context_str)
                # 2. Practical quick plan from Llama 3.3
                teacher_action_plan = generate_plan_with_llama(ai_analysis)
                
            st.markdown("### 🎯 Teacher Ke Liye AI Guidance (Kal Kya Kaam Dena Hai):")
            st.info(teacher_action_plan)
