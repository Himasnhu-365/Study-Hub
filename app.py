import streamlit as st
from google import genai
import json

st.set_page_config(page_title="Study Hub", page_icon="🔍", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Base App Theme */
    .stApp { background-color: #f0fbfa; font-family: 'Inter', sans-serif; color: #0b4b5c; }
    header { visibility: hidden; }
    
    /* Custom Headers */
    .top-container { text-align: center; margin-bottom: 25px; margin-top: -40px; }
    .logo-pill { border: 1.5px solid #a4dfe5; color: #1693a5; background-color: #ffffff; padding: 8px 24px; border-radius: 30px; font-size: 13px; font-weight: 600; letter-spacing: 1.5px; display: inline-block; margin-bottom: 20px; }
    .main-title { font-size: 2.2rem; font-weight: 600; color: #0b4b5c; margin: 0 0 10px 0; }
    .subtitle { font-size: 15px; color: #558790; margin-bottom: 10px; }
    
    /* Dashed Inputs */
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[role="combobox"] {
        border: 2px dashed #a4dfe5; border-radius: 12px; background-color: #ffffff; 
        color: #0b4b5c; padding: 14px; font-size: 15px; box-shadow: none; transition: 0.3s;
    }
    div[data-testid="stTextInput"] input:focus, div[data-testid="stSelectbox"] div[role="combobox"]:focus {
        border-color: #1693a5;
    }
    
    /* Call to Action Button */
    .stButton>button { 
        background-color: #1693a5; color: white; border: none; border-radius: 8px; 
        font-weight: 600; padding: 12px 20px; width: 100%; font-size: 16px; margin-top: 10px; transition: 0.3s; 
    }
    .stButton>button:hover { background-color: #117a89; color: white; }
    
    /* Text & Radio Alignment */
    div[data-testid="stRadio"] label { color: #558790 !important; font-weight: 500; }
    hr { border-color: #c9ecef; }
    </style>
""", unsafe_allow_html=True)

if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'test_submitted' not in st.session_state:
    st.session_state.test_submitted = False
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

st.markdown("""
    <div class="top-container">
        <div class="logo-pill">🔍 STUDY HUB</div>
        <h1 class="main-title">Understand Concepts, Simply.</h1>
        <div class="subtitle">Enter your syllabus topics to understand them in simpler language.</div>
    </div>
""", unsafe_allow_html=True)

exam_target = st.selectbox("Exam", ["Class 12 Boards", "NDA", "NEET", "Uttarakhand Police Constable"], label_visibility="collapsed")
topic = st.text_input("Topic", placeholder="Drop topic here (e.g., Electrostatics, Matrices)", label_visibility="collapsed")

st.markdown("<p style='text-align: center; color: #6c989e; font-size: 13px; margin-top: -15px; margin-bottom: 20px;'>Supports physics, math, general knowledge · Instant generation</p>", unsafe_allow_html=True)

mode = st.radio("Mode", ["Simplify Concept (Notes)", "Full Mock Test (MCQs)"], horizontal=True, label_visibility="collapsed")

if st.button("Generate Notes"):
    if not topic:
        st.warning("Please enter a topic first.")
    else:
        st.session_state.quiz_data = None
        st.session_state.test_submitted = False
        st.session_state.user_answers = {}
        
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)
            
            if mode == "Full Mock Test (MCQs)":
                prompt = f"""Generate a 5-question multiple choice mock test for '{exam_target}' on '{topic}'.
                Return ONLY valid JSON: [{{"question": "Q text", "options": ["A", "B", "C", "D"], "answer": "Option Text", "explanation": "Text"}}]"""
                
                with st.spinner("Analyzing topic..."):
                    response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
                    try:
                        raw_json = response.text.replace("```json", "").replace("```", "").strip()
                        st.session_state.quiz_data = json.loads(raw_json)
                    except:
                        st.error("Format error. Try again.")
            
            else:
                prompt = f"Act as an educator for '{exam_target}'. Topic: '{topic}'. Keep it extremely clean, highly accurate, use markdown bullet points."
                with st.spinner("Analyzing topic..."):
                    def stream_data():
                        res = client.models.generate_content_stream(model="gemini-3.6-flash", contents=prompt)
                        for chunk in res:
                            if chunk.text: yield chunk.text
                    
                    st.markdown("---")
                    full_notes = st.write_stream(stream_data())
                
                st.download_button(
                    label="Download Material",
                    data=full_notes,
                    file_name=f"{exam_target}_{topic}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                    
        except Exception as e:
            st.error(f"Error connecting to AI: {e}")

if st.session_state.quiz_data and mode == "Full Mock Test (MCQs)":
    st.markdown("---")
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"**{i+1}. {q['question']}**")
        st.session_state.user_answers[i] = st.radio("Options:", q['options'], key=f"q_{i}", index=None, disabled=st.session_state.test_submitted, label_visibility="collapsed")
        st.write("")
        
    if not st.session_state.test_submitted:
        if st.button("Analyze Reports"):
            st.session_state.test_submitted = True
            st.rerun() 
            
    if st.session_state.test_submitted:
        st.markdown("---")
        score = 0
        for i, q in enumerate(st.session_state.quiz_data):
            if st.session_state.user_answers.get(i) == q['answer']:
                score += 1
                st.success(f"**Q{i+1} Correct**")
            else:
                st.error(f"**Q{i+1} Incorrect** (Answer: {q['answer']})")
            st.caption(f"Explanation: {q['explanation']}")
                
        st.markdown(f"<h3 style='text-align:center; color:#1693a5;'>Final Score: {score} / 5</h3>", unsafe_allow_html=True)
        if st.button("Reset Analysis"):
            st.session_state.quiz_data = None
            st.session_state.test_submitted = False
            st.rerun()
