import streamlit as st
import os
import time
import requests
import io
import urllib.parse
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS

# सुपाबेस लाइब्रेरी इम्पोर्ट करना
from supabase import create_client, Client
# आपकी बनाई हुई सिलेबस फाइल इम्पोर्ट करना
try:
    from syllabus_data import SYLLABUS_DATABASE
except:
    SYLLABUS_DATABASE = []

# १. पेज का कॉन्फ़िगरेशन
st.set_page_config(page_title="Grace Study Centre - AI Ecosystem", page_icon="🏫", layout="wide")

# एपीआई की (API Keys) निकालना
groq_key = os.environ.get("GROQ_API_KEY", "gsk_jsNWtIwmiR_cmBt0wQrWGdyb3FYKsje1yQBxaid7d1kqn7N7PQt")
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")

# क्लाइंट्स को एक्टिव करना
try:
    groq_client = Groq(api_key=groq_key)
except Exception as e:
    st.error(f"Groq Initialization Error: {str(e)}")

supabase_active = False
if supabase_url and supabase_key:
    try:
        supabase_client: Client = create_client(supabase_url, supabase_key)
        supabase_active = True
    except:
        pass

# सीएसएस (CSS) स्टाइलिंग
st.markdown("""
    <style>
    .main-title { font-size: 32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #555555; margin-bottom: 25px; font-size: 16px; }
    .section-box { padding: 20px; border-radius: 10px; background-color: #F9FAFB; border: 1px solid #E5E7EB; margin-bottom: 20px; }
    div.stButton > button { border-radius: 20px !important; height: 42px !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🏫 Grace Study Centre</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Supabase Connected AI RAG Engine (100% Stable Database Protocol)</div>", unsafe_allow_html=True)

# फाइनल ऑडियो टेक्स्ट क्लीनर इंजन
def final_clean_engine(text):
    if not text:
        return ""
    clean = text.lower()
    garbage_words = ["a flat", "e flat", "b flat", "g flat", "a-flat", "e-flat", "1.", "2.", "3.", "4.", "5."]
    for word in garbage_words:
        clean = clean.replace(word, "")
    return clean.strip()

if "speech_text" not in st.session_state:
    st.session_state.speech_text = ""

tab1, tab2, tab3 = st.tabs(["🎙️ Student Personal Tutor", "📊 Intelligent Tracker & Planner", "⚙️ Admin Database Sync"])

with tab1:
    st.markdown("<div class='section-box'><b>👤 Student Profile Settings (छात्र प्रोफाइल设置)</b>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns([1, 1, 1, 1])
    with p_col1: nama = st.text_input("Aapka Naam?", value="Omkar")
    with p_col2: class_level = st.selectbox("Class Level:", ["Nursery", "LKG", "UKG", "Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "6th", "7th", "8th", "9th", "10th"], index=3)
    with p_col3: subject = st.text_input("Subject Target?", value="Mathematics")
    with p_col4: current_student_level = st.selectbox("Student Level (बच्चे का स्तर):", ["Basic (Zero Level)", "Medium Level", "Hard Level"])
    st.markdown("</div>", unsafe_allow_html=True)

    lang = st.selectbox("Response Bhasha:", ["Standard Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English"])
    mode = st.radio("Option (विकल्प):", ["📝 Sirf Text", "🗣️ Bolne wala Teacher Mode (Emotional)", "🎵 Gana / Kavita Mode (Emotional)"], horizontal=True)

    st.markdown("---")
    st.markdown("### 🎤 Sawal Poochen (सवाल पूछें):")

    audio_data = mic_recorder(start_prompt="🎙️ रिकॉर्ड करने के लिए यहाँ दबाएँ", stop_prompt="🛑 रोकने के लिए यहाँ दबाएँ", key='supabase_mic_recorder')

    if audio_data and audio_data.get("bytes"):
        try:
            file_placeholder = ("temp_audio.wav", audio_data["bytes"], "audio/wav")
            transcription = groq_client.audio.transcriptions.create(file=file_placeholder, model="whisper-large-v3-turbo")
            if transcription.text.strip():
                st.session_state.speech_text = transcription.text
        except:
            pass

    user_query = st.text_input("आपका सवाल:", value=st.session_state.speech_text)
    submit_button = st.button("जवाब जनरेट करें (Submit Question)", type="primary")

    if submit_button and user_query:
        db_context = ""
        db_image_prompt = ""
        
        if supabase_active:
            try:
                response = supabase_client.table("syllabus").select("*").eq("class_name", class_level).eq("subject", subject).eq("level_type", current_student_level).execute()
                if response.data:
                    db_context = response.data[0].get("content_data", "")
                    db_image_prompt = response.data[0].get("image_prompt", "")
            except Exception as db_err:
                st.warning(f"Database Fetch Warning: {str(db_err)}")

        script_instruction = "Output 100% in pure Devanagari Hindi script." if "हिंदी" in lang else "Output 100% in pure Gurmukhi Punjabi script." if "ਪੰਜਾਬੀ" in lang else "Write strictly in English."
        tts_lang = 'hi' if "हिंदी" in lang else 'pa' if "ਪੰਜਾਬੀ" in lang else 'en'

        system_base_prompt = f"Aap ek friendly school teacher hain. Aapko sirf is verified data ke aadhar par hi bacche ko padhana hai: '{db_context}'. Agar query is data se bahar ki hai, tab bhi isi topic se joda easy answer dein."
        full_prompt = f"{system_base_prompt} Student Name: {nama}, Class: {class_level}, Level: {current_student_level}. Question: {user_query}. Rule: {script_instruction}"

        col_left, col_right = st.columns([0.6, 0.4])

        with col_left:
            text_container = st.empty()
            text_container.markdown("⏳ शिक्षक सोच रहे हैं...")

        with col_right:
            image_placeholder = st.empty()

        try:
            full_response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful school teacher. Follow script layout strictly. Never use bullets, hashes, or numbers. Keep paragraphs easy for kids."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            detailed_text = full_response.choices[0].message.content
            
            with col_left:
                text_container.markdown(f"**Teacher:**\n\n{detailed_text}")

            final_img_prompt = db_image_prompt if db_image_prompt else f"Educational clean textbook diagram for school children showing: {user_query}, labeled text vectors."
            encoded_prompt = urllib.parse.quote(final_img_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=800&nologo=true"
            
            with col_right:
                image_placeholder.image(image_url, caption=f"Satik Diagram: {subject}", use_container_width=True)

            if "Sirf Text" not in mode:
                clean_full_text = final_clean_engine(detailed_text)
                tts_master = gTTS(text=clean_full_text if clean_full_text else "आइए समझते हैं।", lang=tts_lang, slow=False)
                fp_master = io.BytesIO()
                tts_master.write_to_fp(fp_master)
                fp_master.seek(0)
                with col_left:
                    st.audio(fp_master, format="audio/mp3")
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")

        st.session_state.speech_text = ""

with tab2:
    st.markdown("### 📊 Student Progress Tracker Dashboard Active")

with tab3:
    st.markdown("### ⚙️ Supabase Data Synchronization Portal")
    if not supabase_active:
        st.error("❌ सुपाबेस API कीज़ अभी रेंडर (Render) पर सेट नहीं की गई हैं।")
    else:
        st.success("✅ सुपाबेस डेटाबेस सर्वर सफलतापूर्वक कनेक्टेड है!")
        if st.button("🚀 गिटहब सिलेबस डेटा को सुपाबेस पर अपलोड करें (Sync Data)"):
            if not SYLLABUS_DATABASE:
                st.error("Syllabus data file is empty or missing.")
            else:
                with st.spinner("⏳ डेटा अपलोड हो रहा है..."):
                    try:
                        supabase_client.table("syllabus").delete().neq("id", 0).execute()
                        for row in SYLLABUS_DATABASE:
                            supabase_client.table("syllabus").insert({
                                "class_name": row["class_name"],
                                "level_type": row["level_type"],
                                "subject": row["subject"],
                                "content_data": row["content_data"],
                                "image_prompt": row["image_prompt"]
                            }).execute()
                        st.success("🎉 बधाई हो ओंकार जी! आपका पूरा क्लास-वाइज़ और लेवल-वाइज़ सिलेबस सुपाबेस सर्वर पर लाइव अपलोड हो गया है!")
                    except Exception as upload_err:
                        st.error(f"Upload Error: {str(upload_err)}")
