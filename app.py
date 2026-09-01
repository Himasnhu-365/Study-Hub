import streamlit as st
from google import genai
import json

st.set_page_config(page_title="Study Hub", page_icon="📓", layout="centered")

st.markdown("""
    <style>
    /* Ultra-Minimalist Flat UI */
    .stButton>button {
        background-color: #111111;
        color: #ffffff;
        border: 1px solid #111111;
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        color: #111111;
        border: 1px solid #111111;
    }
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[role="combobox"] {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        background-color: #f8fafc;
        color: #0f172a;
    }
    hr { margin-top: 1em; margin-bottom: 1em; }
    </style>
""", unsafe_allow_html=True)

if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'test_submitted' not in st.session_state:
    st.session_state.test_submitted = False
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

st.title("📓 Study Hub")
st.markdown("Minimalist AI Tutor for Focused Learning.")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    exam_target = st.selectbox("Target Exam", ["Class 12 Boards", "NDA", "NEET", "CUET", "Class 10 Boards"])
with col2:
    topic = st.text_input("Topic", placeholder="e.g., Electrostatics")

mode = st.radio("Mode", ["Simplify Concept (Notes)", "Formula Cheat Sheet", "Full Mock Test (MCQs)"], horizontal=True)

if st.button("Generate", use_container_width=True):
    if not topic:
        st.warning("Topic name is required.")
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
                
                with st.spinner("Generating CBT..."):
                    response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
                    try:
                        raw_json = response.text.replace("```json", "").replace("```", "").strip()
                        st.session_state.quiz_data = json.loads(raw_json)
                    except:
                        st.error("Format error. Try again.")
            
            else:
                prompt = f"Act as an educator for '{exam_target}'. Topic: '{topic}'. Action: {mode}. Keep it extremely clean, highly accurate, use markdown bullet points."
                with st.spinner("Writing notes..."):
                    def stream_data():
                        res = client.models.generate_content_stream(model="gemini-3.6-flash", contents=prompt)
                        for chunk in res:
                            if chunk.text: yield chunk.text
                    
                    st.markdown("---")
                    full_notes = st.write_stream(stream_data())
                
                st.download_button(
                    label="Download Document (.txt)",
                    data=full_notes,
                    file_name=f"{exam_target}_{topic}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                    
        except Exception as e:
            st.error(f"Error: {e}")

if st.session_state.quiz_data and mode == "Full Mock Test (MCQs)":
    st.markdown("---")
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"**{i+1}. {q['question']}**")
        st.session_state.user_answers[i] = st.radio("Options:", q['options'], key=f"q_{i}", index=None, disabled=st.session_state.test_submitted, label_visibility="collapsed")
        st.write("")
        
    if not st.session_state.test_submitted:
        if st.button("Submit Assessment", use_container_width=True):
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
                
        st.subheader(f"Final Score: {score} / 5")
        if st.button("Reset Test"):
            st.session_state.quiz_data = None
            st.session_state.test_submitted = False
            st.rerun()
