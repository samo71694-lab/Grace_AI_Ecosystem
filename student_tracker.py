import streamlit as st
import json
import os
import google.generativeai as genai
from groq import Groq

# Data save karne ke liye file
DATA_FILE = "student_data.json"

# Function: Data load karne ke liye
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Function: Data ko permanently save karne ke liye
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Data load karna
students_db = load_data()

# --- AI API SETUP ---
# Background se API Keys uthana ya fir direct paste karna
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_KEY_HERE")

# Models ko initialize karna
genai.configure(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY != "YOUR_GROQ_KEY_HERE" else None

# --- SMART AI ROUTER SYSTEM FUNCTIONS ---

# 1. Simple Task & Voice ke liye Gemini 1.5 Flash
def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

# 2. Logic aur Weak Point Analysis ke liye DeepSeek-R1 via Groq
def ask_deepseek(prompt):
    if not groq_client:
        return "Groq API Key nahi mili! Kripya update karein."
    try:
        completion = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"DeepSeek Error: {str(e)}"

# 3. Text & Study Planner Generation ke liye Meta Llama 3.3 via Groq
def ask_llama(prompt):
    if not groq_client:
        return "Groq API Key nahi mili! Kripya update karein."
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Llama Error: {str(e)}"


# --- STREAMLIT UI ---
st.title("📚 Grace Study Centre - Intelligent Tracker")
st.write("Welcome Omkar ji! Aapka Multi-AI System chalne ke liye taiyar hai.")

tab1, tab2 = st.tabs(["📝 Data Entry Form", "🤖 AI Study Planner"])

with tab1:
    st.header("Student Data Entry")
    
    student_name = st.text_input("Bacche ka Naam (Student Name):")
    student_class = st.selectbox("Class Chunein:", ["CLASS- 6th", "CLASS- 7th", "Other"])
    roll_number = st.text_input("Roll Number:")

    attendance_status = st.radio("Attendance:", ["Present", "Absent"])
    test_given = st.selectbox("Kya bacche ne Test diya?", ["Haan (Yes)", "Nahi (No)"])

    if test_given == "Haan (Yes)":
        test_marks = st.number_input("Test Marks (Out of 100):", min_value=0, max_value=100, step=1)
        weak_points = st.text_area("Weak Points (Baccha kahan kamjor hai?):")
    else:
        test_marks = 0
        weak_points = "Test nahi diya"

    if st.button("Save Student Data"):
        if student_name and roll_number:
            students_db[roll_number] = {
                "name": student_name,
                "class": student_class,
                "attendance": attendance_status,
                "test_given": test_given,
                "marks": test_marks,
                "weak_points": weak_points
            }
            save_data(students_db)
            st.success(f"{student_name} ka data kamyabi se save ho gaya!")
        else:
            st.error("Kripya Naam aur Roll Number zaroor bharein!")

with tab2:
    st.header("🧠 Smart AI Study Planner & Analysis")
    
    st.subheader("🔍 Student Ka Data Check Karein")
    search_roll = st.text_input("Analysis ke liye Roll Number enter karein:")
    
    if search_roll in students_db:
        s_data = students_db[search_roll]
        st.write(f"**Naam:** {s_data['name']} | **Class:** {s_data['class']}")
        st.write(f"**Attendance:** {s_data['attendance']} | **Marks:** {s_data['marks']}/100")
        st.write(f"**Kamjori (Weak Points):** {s_data['weak_points']}")
        
        # Sawaal puchne ka tarika
        st.subheader("✍️ Ask AI (Kuch bhi puchein)")
        student_query = st.text_input("Apna sawaal likhein ya Plan poochein:", value="Is bacche ka weak point check karke agle din ka study plan banao.")
        
        if st.button("Generate AI Plan with Integrated Models"):
            # Yahan hamara system automatic alag-alag models ko task de raha hai
            with st.spinner("AI Router dimaag laga raha hai..."):
                
                # Context banana bache ke data ka
                info_context = f"Student Name: {s_data['name']}, Class: {s_data['class']}, Marks: {s_data['marks']}, Weak points: {s_data['weak_points']}. Query: {student_query}"
                
                st.markdown("---")
                # 1. DeepSeek se deep analysis nikalna
                st.subheader("🔬 DeepSeek-R1 (Deep Analysis & Reason)")
                analysis_result = ask_deepseek(f"Analyze this student data and pinpoint exactly where they need core conceptual help: {info_context}")
                st.write(analysis_result)
                
                # 2. Llama se agle din ka customized professional time-table banwana
                st.subheader("📅 Meta Llama 3.3 (Next-Day Study Planner)")
                planner_result = ask_llama(f"Create a strict, encouraging next-day study plan and timetable in simple Hinglish based on this analysis: {analysis_result}")
                st.write(planner_result)
                
    elif search_roll:
        st.error("Yeh Roll Number database mein nahi mila!")