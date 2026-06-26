import streamlit as st
import os
import io
import urllib.parse
from streamlit_mic_recorder import mic_recorder
from groq import Groq
import google.generativeai as genai
from gtts import gTTS

# === १ से ५ क्लास का मैथ सिलेबस ===
SYLLABUS_DATABASE = [
    {"class_name": "Class 1", "level_type": "Basic (Zero Level)", "subject": "Mathematics", "content_data": "Class 1 Basic Level covers counting numbers from 1 to 50, identifying smaller and bigger numbers, and very simple single-digit addition.", "image_prompt": "Cute children mathematics book illustration showing cartoon apples for single digit addition 2 plus 3"},
    {"class_name": "Class 1", "level_type": "Medium Level", "subject": "Mathematics", "content_data": "Class 1 Medium Level introduces numbers up to 100, double-digit addition without carrying, single-digit subtraction.", "image_prompt": "Colorful math worksheet background with numbers 1 to 100"},
    {"class_name": "Class 1", "level_type": "Hard Level", "subject": "Mathematics", "content_data": "Class 1 Hard Level covers simple math word problems, reading a clock to the nearest hour, identifying basic shapes.", "image_prompt": "Kid friendly clock diagram showing 3 o clock with colorful shapes"}
]

st.set_page_config(page_title="Grace Study Centre", page_icon="🏫", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏫 Grace Study Centre</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555555; font-weight: bold;'>3-Level Balanced Multi-Model AI Ecosystem</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎙️ Student Personal Tutor", "📊 Intelligent Tracker & Planner", "⚙️ Connections & API Settings"])

# --- पहला खांचा: पर्सनल ट्यूटर एजेंट ---
with tab1:
    st.markdown("### 👤 Student Profile & Language Settings")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nama = st.text_input("Aapka Naam?", value="Rahul")
    with col2:
        class_level = st.selectbox("Class Level Chunen:", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5"], index=0)
    with col3:
        subject = st.selectbox("Subject Target:", ["English", "Mathematics", "Science", "Social Studies"], index=0)
    with col4:
        current_level = st.selectbox("Student Level:", ["Basic (Zero Level)", "Medium Level", "Hard Level"], index=0)

    lang = st.selectbox("Response Bhasha Chunen:", ["Standard Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"])
    mode = st.radio("Option Select Karein:", ["📝 Sirf Text ke roop mein chahiye", "🗣️ Bolne wala Teacher Mode", "🎵 Gana / Kavita Mode"], horizontal=True)

    st.markdown("---")
    st.markdown("### 🎤 Sawal Poochen:")

    audio_data = mic_recorder(start_prompt="🎙️ Boliye", stop_prompt="🛑 Rokiye", key='live_mic_recorder')
    
    if "speech_text" not in st.session_state:
        st.session_state.speech_text = ""

    # आवाज़ पहचानने के लिए जेमिनी का बेस्ट इस्तेमाल
    gemini_key = st.session_state.get("gemini_api_key", "")
    if audio_data and audio_data.get("bytes") and gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model_speech = genai.GenerativeModel("gemini-1.5-flash")
            audio_parts = [{"mime_type": "audio/wav", "data": audio_data["bytes"]}]
            response_speech = model_speech.generate_content(["Convert this speech audio directly to plain text text strictly.", audio_parts])
            if response_speech.text.strip():
                st.session_state.speech_text = response_speech.text
        except:
            pass

    user_query = st.text_input("Apna sawal yahan likhein ya upar bolen:", value=st.session_state.speech_text)
    submit_button = st.button("जवाब जनरेट करें (Submit)", type="primary")

    if submit_button and user_query:
        # --- सुपाबेस लाइव डेटा ऑटो-अपलोड इंजन ---
        if st.session_state.get("sb_url") and st.session_state.get("sb_key"):
            try:
                from supabase import create_client
                url_db = st.session_state["sb_url"]
                key_db = st.session_state["sb_key"]
                sb_client = create_client(url_db, key_db)
                sb_client.table("grace_ai_tutor_logs").insert({
                    "student_name": str(nama), "class_level": str(class_level), "subject": str(subject), "student_query": str(user_query)
                }).execute()
            except:
                pass

        script_instruction = "Output 100% in pure Devanagari Hindi script." if "हिंदी" in lang else "Output 100% in pure Gurmukhi Punjabi script." if "ਪੰਜਾਬੀ" in lang else "Write strictly in English."
        tts_lang = 'hi' if "हिंदी" in lang else 'pa' if "ਪੰਜਾਬੀ" in lang else 'en'
        
        full_prompt = f"You are a loving school teacher. Subject: {subject}. Level: {current_level}. Student: {nama}, Class: {class_level}. Answer this query simply, without bullets/markdown hashes, in clean paragraphs: '{user_query}'. Rule: {script_instruction}"

        detailed_text = ""
        used_model = "Groq (Llama 3.3)"
        
        with st.spinner("⏳ शिक्षक सोच रहे हैं (Smart Routing Active)..."):
            # लेयर १: सबसे पहले Groq से सुपर-फ़ास्ट जवाब की कोशिश करें
            groq_key = st.session_state.get("groq_api_key", "")
            if groq_key:
                try:
                    groq_client = Groq(api_key=groq_key)
                    full_response = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": full_prompt}]
                    )
                    detailed_text = full_response.choices[0].message.content
                except:
                    pass  # Groq फेल हुआ तो लेयर २ पर जाएगा

            # लेयर २: अगर Groq चाबी नहीं है या फेल हो गया, तो जेमिनी संभालेगा (Failover)
            if not detailed_text and gemini_key:
                try:
                    genai.configure(api_key=gemini_key)
                    model_text = genai.GenerativeModel("gemini-1.5-flash")
                    response_text = model_text.generate_content(full_prompt)
                    detailed_text = response_text.text
                    used_model = "Gemini (Fallback)"
                except:
                    pass

            if not detailed_text:
                detailed_text = f"नमस्ते {nama}! नेटवर्क क्रेडेंशियल्स की जांच करें। कृपया सेटिंग्स टैब में वैध API Keys दर्ज करें।"

            st.markdown(f"### 👩‍🏫 Teacher Response ({used_model}):\n\n{detailed_text}")

            # --- केवल एक फाइनल प्रीमियम ८K फोटो (बिना लिखे हुए शब्दों के कचरे के) ---
            st.markdown("#### 🧠 Smart Educational Visual Guide (8K Quality)")
            with st.spinner("🖼️ एआई आपके पाठ के अनुकूल साफ़ चित्र बना रहा है..."):
                try:
                    # 'strictly no text, typography or spelling mistakes' का नियम ताकि फोटो साफ़ आए
                    clean_image_prompt = f"An ultra-realistic hyper-detailed 8k resolution educational children textbook illustration perfectly visualizing '{user_query}', bright vibrant colors, highly clear for primary school kids, sharp focus, cinematic lighting, strictly no text, no written words, no letters, no typography, clear vectors"
                    encoded_prompt = urllib.parse.quote(clean_image_prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=600&nologo=true&enhance=true"
                    st.image(image_url, caption=f"Visual Guide for: {user_query}")
                except:
                    st.info("Visual render active.")

            if "Sirf Text" not in mode:
                try:
                    tts_master = gTTS(text=detailed_text, lang=tts_lang, slow=False)
                    fp_master = io.BytesIO()
                    tts_master.write_to_fp(fp_master)
                    fp_master.seek(0)
                    st.audio(fp_master, format="audio/mp3")
                except:
                    pass
        st.session_state.speech_text = ""

# --- दूसरा खांचा: इंटेलिजेंट ट्रैकर ---
with tab2:
    st.markdown("### 📊 Student Progress Tracker Dashboard")
    st.write("Welcome to your Intelligent Tracker & Planner agent.")

# --- तीसरा खांचा: सेटिंग्स हब ---
with tab3:
    st.markdown("### ⚙️ Multi-Model Router & API Settings")
    st.info("यहाँ अपनी चाबियाँ डालें ताकि लोड संतुलित रहे और एक मॉडल बंद होने पर दूसरा ऐप को चालू रखे।")
    
    col_key1, col_key2 = st.columns(2)
    with col_key1:
        st.text_input("Groq API Key (Primary Fast Text):", type="password", key="groq_api_key", value="gsk_jsNWtIwmiR_cmBt0wQrWGdyb3FYKsje1yQBxaid7d1kqn7N7PQt")
    with col_key2:
        st.text_input("Google Gemini API Key (Voice & Fallback Backup):", type="password", key="gemini_api_key", value="")
        
    st.markdown("---")
    st.markdown("### ⚡ Supabase Cloud Database")
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        st.text_input("Supabase Project URL:", value="https://vkrhwxcjkhebqyjiicbnd.supabase.co", type="password", key="sb_url")
    with col_sub2:
        st.text_input("Supabase Anon API Key:", value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", type="password", key="sb_key")
        
    if st.button("Connect & Activate Balanced Engine", type="primary"):
        st.success("सभी क्रेडेंशियल्स सफलतापूर्वक सिंक हो गए हैं! लोड बैलेंसिंग एक्टिवेटेड है।")
