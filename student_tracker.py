import streamlit as st

# Custom CSS for Student Tracker
st.markdown("""
    <style>
    .card-box { padding: 15px; border-radius: 8px; background-color: #F3F4F6; border-left: 5px solid #1E3A8A; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# Shared Database Simulation
students_db = {
    "101": {"name": "Aman Sharma", "class": "CLASS- 7th", "attendance": 85, "marks": 72, "weak_points": "Trigonometry formulas mein confusion hota hai, sin, cos, tan ke ratios mein galti karta hai. English reading slow hai."},
    "102": {"name": "Rohanpreet Singh", "class": "CLASS- 7th", "attendance": 92, "marks": 45, "weak_points": "Maths mein basic calculation slow hai, algebra ke linear equations samajhne mein dikkat hoti hai. Test miss karta hai."},
    "103": {"name": "Simran Kaur", "class": "CLASS- 7th", "attendance": 65, "marks": 88, "weak_points": "Attendance kam hone ki wajah se science ke important experiments aur conceptual classes miss ho gayi hain. Revision ki zarurat hai."}
}

st.markdown("### 📊 Internal Student Tracker Database")
search_roll = st.text_input("Enter Student Roll Number to Fetch Data:", value="101", key="internal_tracker_search").strip()

if search_roll in students_db:
    s_data = students_db[search_roll]
    st.markdown(f"""
    <div class="card-box">
        <b>👤 Student Name:</b> {s_data['name']}<br>
        <b>📅 Allocated Class:</b> {s_data['class']}<br>
        <b>📈 System Attendance:</b> {s_data['attendance']}%<br>
        <b>🎯 Mock Exam Score:</b> {s_data['marks']}/100
    </div>
    """, unsafe_allow_html=True)
    st.warning(f"**System Flagged Weak Points:**\n{s_data['weak_points']}")
else:
    st.error("❌ Student Roll Number not found in backend simulation.")
