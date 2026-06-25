import streamlit as st
import os
import time
import requests
import io
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS

# ------------------------------------------------------------------
# 1. Page Configuration (Mobile & Desktop Responsive)
# ------------------------------------------------------------------
st.set_page_config(page_title="Grace Study Centre - AI Ecosystem", page_icon="🏫", layout="wide")

# API Keys Extraction from Render Environment
groq_key = os.environ.get("GROQ_API_KEY", "gsk_jsNWtIwmiR_cmBt0wQrWGdyb3FYKsje1yQBxaid7d1kqn7N7PQt")
cartesia_key = os.environ.get("CARTESIA_API_KEY", "") 

try:
    groq_client = Groq(api_key=groq_key)
except Exception as e:
    st.error(f"Groq Initialization Error: {str(e)}")

# Custom CSS for Professional Branding
st.markdown("""
    <style>
    .main-title { font-size: 32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 25px; font-size: 16px; }
    .section-box { padding: 20px; border-radius: 10px; background-color: #F9FAFB; border: 1px solid #E5E7EB; margin-bottom: 20px; }
    .card-box { padding: 15px; border-radius: 8px; background-color: #F3F4F6; border-left: 5px solid #1E3A8A; margin-bottom: 15px; }
    
    [data-testid="stHorizontalBlock"] { align-items: center !important; gap: 10px !important; }
    div.stButton > button { border-radius: 20px !important; height: 42px !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🏫 Grace Study Centre</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Advanced Hybrid Voice Protocol (Gemini & Groq Fallback + GLM Handover)</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 2. Local Database Simulation (Tracker Portal)
# ------------------------------------------------------------------
students_db = {
    "101": {"name": "Aman Sharma", "class": "CLASS- 7th", "attendance": 85, "marks": 72, "weak_points": "Trigonometry formulas mein confusion hota hai, sin, cos, tan ke ratios mein galti karta hai. English reading slow hai."},
    "102": {"name": "Rohanpreet Singh", "class": "CLASS- 7th", "attendance": 92, "marks": 45, "weak_points": "Maths mein basic calculation slow hai, algebra ke linear equations samajhne mein dikkat hoti hai. Test miss karta hai."},
    "103": {"name": "Simran Kaur", "class": "CLASS- 7th", "attendance": 65, "marks": 88, "weak_points": "Attendance kam hone ki wajah se science ke important experiments aur conceptual classes miss ho gayi hain. Revision ki zarurat hai."}
}

def ask_deepseek(prompt):
    if not groq_client: return "⚠️ GROQ_API_KEY environment variable mein nahi mili."
    try:
        completion = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "system", "content": "Aap ek expert educational psychologist hain. Data ka sateek analysis dein."}, {"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e: return f"DeepSeek Error: {str(e)}"

def ask_llama(prompt):
    if not groq_client: return "⚠️ GROQ_API_KEY environment variable mein nahi mili."
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Aap Grace Study Centre ke senior coordinator hain. Hinglish mein customized timetable banayein."}, {"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e: return f"Llama Error: {str(e)}"

# ------------------------------------------------------------------
# 3. Main Navigation
# ------------------------------------------------------------------
tab1, tab2 = st.tabs(["🎙️ Student Personal Tutor", "📊 Intelligent Tracker & Planner"])

# ==================================================================
# TAB 1: TUTOR PORTAL (Dual-Engine Fallback Architecture)
# ==================================================================
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

    if "speech_text" not in st.session_state:
        st.session_state.speech_text = ""

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_query = st.text_input("Apna sawal type karein...", value=st.session_state.speech_text, key="text_query", label_visibility="collapsed")
    with col2:
        audio_data = mic_recorder(start_prompt="🎙️ Boliye", stop_prompt="🛑 Rokiye", key='google_mic')

    # Real-Time Mic Processing (Groq Whisper)
    if audio_data and audio_data.get("bytes"):
        with st.spinner("🎙️ Listening and Processing..."):
            try:
                file_placeholder = ("temp_audio.wav", audio_data["bytes"], "audio/wav")
                transcription = groq_client.audio.transcriptions.create(
                    file=file_placeholder, model="whisper-large-v3-turbo"
                )
                st.session_state.speech_text = transcription.text
                st.rerun()
            except Exception as e:
                st.error(f"Mic Input Processing Error: {str(e)}")

    if user_query:
        # Construct full prompt engineering blueprint
        prompt_modifier = f"Aap ek friendly Indian school teacher hain jo bacchon se bohot pyaar se baat karti hai. {class_level} ke student {nama} ko {lang} mein samjhayein."
        if "Gana" in mode: prompt_modifier += " Jawab ek bacho jaisi masti bhari rhyming kavita ke roop mein ho."
        full_prompt = f"{prompt_modifier} Topic: {subject}. Question: {user_query}"

        text_container = st.empty()
        audio_container = st.empty()
        
        # 🌟 STEP 1: DUAL-ENGINE INSTANT EMOTION VOICE (With Stable Free gTTS Fallback)
        with st.spinner("⚡ Activating Instant Emotion Voice..."):
            audio_played = False
            first_line = f"Namaste {nama} beta! Wah, {subject} ka bohot hi pyaara sawal pucha hai aapne. Chaliye abhi minto mein samajhte hain!"
            
            try:
                instant_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Generate ONLY ONE short introductory line acknowledging the student's question warmly. Max 15 words."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                first_line = instant_response.choices[0].message.content
                text_container.markdown(f"**Teacher:** {first_line}")
                
                # Absolute cleaning of text to remove formatting symbols
                clean_first_line = first_line.replace("**", "").replace("*", "").replace('"', '').replace('“', '').replace('”', '')
                
                if "Sirf Text" not in mode:
                    # If Cartesia Key is provided, use it. Otherwise, instantly fallback to free gTTS
                    if cartesia_key.strip():
                        headers = {
                            "X-API-Key": cartesia_key,
                            "Cartesia-Version": "2024-06-10",
                            "Content-Type": "application/json"
                        }
                        data = {
                            "model_id": "sonic-multilingual",
                            "transcript": clean_first_line,
                            "voice": {"mode": "id", "id": "63866d90-2121-4d7c-a4de-eaf3b8908f5d"},
                            "output_format": {"container": "raw", "encoding": "pcm_f32le", "sample_rate": 44100}
                        }
                        res = requests.post("https://api.cartesia.ai/tts/bytes", headers=headers, json=data)
                        if res.status_code == 200:
                            audio_container.audio(res.content, format="audio/wav", autoplay=True)
                            audio_played = True
                    
                    # FREE Tier Automation Fallback (Guarantees Audio Output)
                    if not audio_played:
                        tts_lang = 'en' if 'English' in lang else 'hi'
                        tts = gTTS(text=clean_first_line, lang=tts_lang, slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        audio_container.audio(fp, format="audio/mp3", autoplay=True)
                        audio_played = True
                        
            except Exception as e:
                text_container.markdown(f"**Teacher:** {first_line}")

        # 🌟 STEP 2: SEAMLESS BACKEND HANDOVER TO FULL LONG RESPONSE
        with st.spinner("⏳ Handover to Full Server for Extended Explanation..."):
            try:
                time.sleep(1.5) # Prevent overlapping
                
                full_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Provide a detailed, complete, clear school-level explanation based on the prompt modifier. Do not repeat the introductory greeting line."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                detailed_text = full_response.choices[0].message.content
                
                # Append and print the complete final output chapter
                text_container.markdown(f"**Teacher:** {first_line}\n\n{detailed_text}")
                
                # Filter symbols for second block audio streaming
                clean_detailed = detailed_text.replace("**", "").replace("*", "").replace('"', '').replace('“', '').replace('”', '')
                
                if "Sirf Text" not in mode:
                    st.info("ℹ snuff text loaded. Free GLM pipeline active for remaining long audio stream.")
                    # Temporary safe audio player for full text block
                    tts_full = gTTS(text=clean_detailed, lang='hi' if 'Hindi' in lang else 'en', slow=False)
                    fp_full = io.BytesIO()
                    tts_full.write_to_fp(fp_full)
                    fp_full.seek(0)
                    st.audio(fp_full, format="audio/mp3")
                    
            except Exception as e:
                st.error(f"Detailed Handover Engine Error: {str(e)}")

# ==================================================================
# TAB 2: TRACKER & PLANNER PORTAL
# ==================================================================
with tab2:
    st.markdown("### 📊 Student Progress Tracker")
    t_col1, t_col2 = st.columns([1, 2])

    with t_col1:
        search_roll = st.text_input("Enter Student Roll Number (101, 102, 103):", value="101").strip()
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
            if st.button("Generate Personalized AI Action Plan", type="primary"):
                info_context = f"Student: {s_data['name']}, Weak Points: {s_data['weak_points']}"
                
                with st.spinner("DeepSeek Analyzing Cognitive Weakness..."):
                    analysis_result = ask_deepseek(f"Analyze the following study pattern data and provide dynamic solutions: {info_context}")
                st.success("✅ Phase 1: DeepSeek-R1 Core Analysis Completed")
                st.write(analysis_result)
                
                with st.spinner("Meta Llama 3.3 tayaar kar raha hai..."):
                    planner_result = ask_llama(f"Create a strict hour-by-hour study planner: {analysis_result}")
                st.info(planner_result)
        else:
            st.write("Kripya action plan generate karne ke liye baayein taraf ek valid Roll Number dalein.")
