import streamlit as st
from google import genai
import json

# 1. Page Config
st.set_page_config(page_title="AI Study Hub Pro", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# 2. Premium CSS (Glassmorphism & Glowing UI)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif !important; }
    .title-text {
        font-size: 3.5rem; font-weight: 800; text-align: center;
        background: linear-gradient(to right, #ff00cc, #3333ff, #00ffcc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: hue 10s infinite linear; margin-bottom: 5px;
    }
    .sub-title { text-align: center; color: #a0a0a0; font-size: 1.2rem; font-weight: 300; margin-bottom: 40px; }
    @keyframes hue { from { filter: hue-rotate(0deg); } to { filter: hue-rotate(360deg); } }
    
    .stButton>button {
        background: linear-gradient(90deg, #ff00cc 0%, #3333ff 100%);
        color: white; border: none; border-radius: 50px;
        padding: 12px 24px; font-size: 1.2rem; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase;
        box-shadow: 0 0 15px rgba(51, 51, 255, 0.4); transition: all 0.4s ease; margin-top: 20px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #3333ff 0%, #ff00cc 100%);
        box-shadow: 0 0 25px rgba(255, 0, 204, 0.7); transform: translateY(-4px) scale(1.02);
    }
    div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label { font-weight: 600 !important; color: #e0e0e0; font-size: 1.1rem; }
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[role="combobox"] {
        border-radius: 12px; border: 2px solid #2d2d3a; background-color: #1a1a24; color: white; transition: all 0.3s;
    }
    div.row-widget.stRadio > div { background: #1a1a24; padding: 15px 25px; border-radius: 15px; border: 1px solid #2d2d3a; display: flex; justify-content: center; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'test_submitted' not in st.session_state:
    st.session_state.test_submitted = False
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

# 4. Clean Sidebar Setup (API Key Box Removed)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=100) 
    st.title("⚙️ Engine Control")
    st.markdown("---")
    st.success("🔒 System Status: **Online**")
    st.info("Engine: **Gemini 3.6 Flash** ⚡\n\nMode: **Secure Cloud**")

# 5. Header
st.markdown('<div class="title-text">AI STUDY HUB PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interactive Mock Tests & Smart Notes</div>', unsafe_allow_html=True)

# 6. UI Layout
col1, col2 = st.columns(2)
with col1:
    exam_target = st.selectbox("🎯 Target Exam", options=["Class 9", "Class 10 Boards", "Class 11", "Class 12 Boards", "NDA", "NEET", "JEE Main", "CUET", "Uttarakhand Police Constable"])
with col2:
    topic = st.text_input("🧠 Specific Topic", placeholder="e.g., Electrostatics & Optics")

st.write("") 
mode = st.radio("What do you want to generate?", ["📝 Full Mock Test (MCQs)", "🧠 Simplify Concept (Notes)", "📋 Formula Cheat Sheet"], horizontal=True)

# 7. GENERATOR LOGIC
if st.button("🚀 IGNITE GENERATOR", use_container_width=True):
    if not topic:
        st.warning("⚠️ System Alert: Topic ka naam likhna zaroori hai.")
    else:
        st.session_state.quiz_data = None
        st.session_state.test_submitted = False
        st.session_state.user_answers = {}
        
        try:
            # Backend se automatic secret uthayega
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)
            
            # Mock Test Logic
            if mode == "📝 Full Mock Test (MCQs)":
                prompt = f"""Generate a 5-question multiple choice mock test for '{exam_target}' on '{topic}'.
                You MUST return ONLY valid JSON. No markdown, no intro. Format exactly like this:
                [
                    {{"question": "Q text", "options": ["A", "B", "C", "D"], "answer": "Correct Option Text", "explanation": "Reasoning..."}}
                ]"""
                
                with st.status("⚡ Generating Interactive Quiz...", expanded=True) as status:
                    response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
                    try:
                        raw_json = response.text.replace("```json", "").replace("```", "").strip()
                        st.session_state.quiz_data = json.loads(raw_json)
                        status.update(label="✅ QUIZ READY!", state="complete", expanded=False)
                    except json.JSONDecodeError:
                        st.error("⚠️ AI format error. Please click Ignite again.")
            
            # Notes & Formula Logic with Download Button
            else:
                prompt = f"Act as an expert educator for '{exam_target}'. Topic: '{topic}'. Action: {mode}. Use markdown, bullet points, and bold text."
                with st.status("⚡ Writing Smart Notes...", expanded=True) as status:
                    def stream_data():
                        res = client.models.generate_content_stream(model="gemini-3.6-flash", contents=prompt)
                        for chunk in res:
                            if chunk.text: yield chunk.text
                    
                    full_notes = st.write_stream(stream_data())
                    status.update(label="✅ COMPLETE!", state="complete", expanded=False)
                
                st.write("") 
                st.download_button(
                    label="📥 Download & Save Notes (.txt File)",
                    data=full_notes,
                    file_name=f"{exam_target}_{topic}_Notes.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                    
        except Exception as e:
            st.error(f"❌ Connection Failed: Make sure GEMINI_API_KEY is added in Streamlit Secrets. Detail: {e}")

# --- 8. INTERACTIVE QUIZ RENDERER ---
if st.session_state.quiz_data and mode == "📝 Full Mock Test (MCQs)":
    st.markdown("---")
    st.markdown("### 🎯 Live CBT Mode Active")
    
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        st.session_state.user_answers[i] = st.radio(
            "Select option:", 
            q['options'], 
            key=f"q_{i}", 
            index=None, 
            disabled=st.session_state.test_submitted
        )
        st.write("")
        
    if not st.session_state.test_submitted:
        if st.button("✅ Submit Test & Show Score", use_container_width=True):
            st.session_state.test_submitted = True
            st.rerun() 
            
    if st.session_state.test_submitted:
        st.markdown("---")
        st.header("📊 AI Performance Analysis")
        score = 0
        
        for i, q in enumerate(st.session_state.quiz_data):
            user_ans = st.session_state.user_answers.get(i)
            if user_ans == q['answer']:
                score += 1
                st.success(f"**Q{i+1} Correct!** 🎉")
            else:
                st.error(f"**Q{i+1} Incorrect.** ❌ \n\n*Your answer: {user_ans} | Correct: {q['answer']}*")
            
            with st.expander("💡 View Explanation"):
                st.write(q['explanation'])
                
        st.markdown(f"### 🏆 Final Score: {score} / 5")
        
        if st.button("🔄 Clear Score & Retake"):
            st.session_state.quiz_data = None
            st.session_state.test_submitted = False
            st.rerun()