import streamlit as st
from google import genai
import json

st.set_page_config(page_title="Study Hub", page_icon="🔍", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Force Light App Theme to override Streamlit Dark Mode */
    .stApp, .stApp > header { background-color: #f0fbfa !important; font-family: 'Inter', sans-serif !important; }
    
    /* Custom Headers */
    .top-container { text-align: center; margin-bottom: 25px; margin-top: -40px; }
    .logo-pill { border: 1.5px solid #a4dfe5 !important; color: #1693a5 !important; background-color: #ffffff !important; padding: 8px 24px; border-radius: 30px; font-size: 13px; font-weight: 600; letter-spacing: 1.5px; display: inline-block; margin-bottom: 20px; }
    .main-title { font-size: 2.2rem !important; font-weight: 600 !important; color: #0b4b5c !important; margin: 0 0 10px 0 !important; }
    .subtitle { font-size: 15px !important; color: #558790 !important; margin-bottom: 10px !important; }
    
    /* Force Light Mode on Inputs & Dropdowns */
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[role="combobox"] {
        border: 2px dashed #a4dfe5 !important; border-radius: 12px !important; 
        background-color: #ffffff !important; color: #0b4b5c !important; 
        padding: 14px !important; font-size: 15px !important; box-shadow: none !important;
    }
    
    /* Fix invisible Placeholder & Radio Text */
    div[data-testid="stTextInput"] input::placeholder { color: #a4dfe5 !important; }
    div[data-testid="stRadio"] label p { color: #0b4b5c !important; font-weight: 600 !important; }
    
    /* Call to Action Button */
    .stButton>button { 
        background-color: #1693a5 !important; border: none !important; border-radius: 8px !important; 
        font-weight: 600 !important; padding: 12px 20px !important; width: 100% !important; 
    }
    .stButton>button p { color: #ffffff !important; font-size: 16px !important; margin: 0 !important; }
    .stButton>button:hover { background-color: #117a89 !important; }
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

# Yahan use_container_width=True add kiya hai taaki button full size ho jaye
if st.button("Generate Notes", use_container_width=True):
