import streamlit as st
import os
import json
import atexit
import time
import re
from datetime import datetime
from dotenv import load_dotenv
import pytesseract
from groq_service import GroqLLM
from data_extractor import DataExtractor, JobSearcher
from generators_combined import PortfolioGenerator, ResumeGenerator, CoverLetterGenerator
from interview_simulator import InterviewSimulator, InterviewUI

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

body, .stApp {
    background: linear-gradient(135deg, #0a0a0a 0%, #1e293b 60%, #2563eb 100%) !important;
    font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    color: #f8fafc;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
    background: linear-gradient(135deg, rgba(10, 10, 10, 0.7) 0%, rgba(37, 99, 235, 0.18) 100%);
    border-radius: 24px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(37, 99, 235, 0.15);
    margin: 1rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    color: #e0e7ef !important;
}

.stApp p, .stApp div, .stApp span, .stApp label {
    color: #cbd5e1 !important;
}

.card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(37, 99, 235, 0.13) 100%);
    border: 1px solid rgba(37, 99, 235, 0.18);
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(37, 99, 235, 0.08);
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    color: #f8fafc;
}

.stButton > button {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 0.8rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.18);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(37, 99, 235, 0.28);
}

.stFileUploader {
    border: 2px dashed rgba(37, 99, 235, 0.3);
    border-radius: 16px;
    background: rgba(37, 99, 235, 0.05);
    padding: 2rem;
    text-align: center;
    color: #e0e7ef !important;
}

.stFileUploader:hover {
    border-color: #2563eb;
    background: rgba(37, 99, 235, 0.1);
}

.stMetric {
    background: rgba(30, 41, 59, 0.95);
    border: 1px solid rgba(37, 99, 235, 0.18);
    color: #f8fafc !important;
}

.stMetric:hover {
    box-shadow: 0 4px 20px rgba(37, 99, 235, 0.13);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
}

.sidebar-nav .stRadio > div {
    gap: 0.7rem;
}

.sidebar-nav .stRadio > div > label {
    background: linear-gradient(135deg, #0a0a0a 0%, #2563eb 100%) !important;
    color: #e0e7ef !important;
    border: 2px solid rgba(37, 99, 235, 0.22) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.2rem !important;
    margin-bottom: 0.7rem !important;
    font-size: 1.13rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    transition: all 0.2s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 2px 12px rgba(37,99,235,0.10) !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.5rem !important;
    outline: none !important;
    position: relative;
    overflow: hidden;
}

.sidebar-nav .stRadio > div > label:hover {
    background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
    color: #fff !important;
    border-color: #2563eb !important;
    transform: scale(1.04) translateY(-2px);
    box-shadow: 0 6px 24px rgba(37,99,235,0.18) !important;
}

.sidebar-nav .stRadio > div > label[data-checked="true"] {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%) !important;
    color: #fff !important;
    border-color: #2563eb !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 18px rgba(37,99,235,0.22) !important;
}

/* Hide the default radio dot */
.sidebar-nav .stRadio input[type="radio"] {
    display: none;
}
</style>
''', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('''
    <style>
    .sidebar-title {
        color: #2563eb !important;
        font-size: 2.1rem;
        font-weight: 900;
        text-align: center;
        padding: 1.1rem 0.5rem 1.1rem 0.5rem;
        margin-bottom: 2.2rem;
        border-radius: 18px;
        border: 2px solid rgba(37, 99, 235, 0.22);
        background: linear-gradient(135deg, rgba(37,99,235,0.13) 0%, rgba(10,10,10,0.7) 100%);
        box-shadow: 0 6px 32px rgba(37,99,235,0.13);
        letter-spacing: -1.5px;
        text-shadow: 0 2px 12px rgba(37,99,235,0.18);
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    }
    .sidebar-nav .stRadio > div {
        gap: 0.7rem;
    }
    .sidebar-nav .stRadio > div > label {
        background: linear-gradient(135deg, #0a0a0a 0%, #2563eb 100%) !important;
        color: #e0e7ef !important;
        border: 2px solid rgba(37, 99, 235, 0.22) !important;
        border-radius: 14px !important;
        padding: 1.1rem 1.2rem !important;
        margin-bottom: 0.7rem !important;
        font-size: 1.13rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
        transition: all 0.2s cubic-bezier(0.4,0,0.2,1) !important;
        box-shadow: 0 2px 12px rgba(37,99,235,0.10) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
        outline: none !important;
        position: relative;
        overflow: hidden;
    }
    .sidebar-nav .stRadio > div > label:hover {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
        color: #fff !important;
        border-color: #2563eb !important;
        transform: scale(1.04) translateY(-2px);
        box-shadow: 0 6px 24px rgba(37,99,235,0.18) !important;
    }
    .sidebar-nav .stRadio > div > label[data-checked="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%) !important;
        color: #fff !important;
        border-color: #2563eb !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 18px rgba(37,99,235,0.22) !important;
    }
    /* Hide the default radio dot */
    .sidebar-nav .stRadio input[type="radio"] {
        display: none;
    }
    </style>
    <div class="sidebar-title">
        ResuMate<br><span style="font-size:1.1rem;font-weight:600;letter-spacing:0.5px;color:#60a5fa;">AI Career Assistant</span>
    </div>
    <div class="sidebar-nav">
    ''', unsafe_allow_html=True)
    page = st.radio(
        "",
        [
            "📤 Data Input",
            "💬 Chat with Resume", 
            "🌐 Portfolio Generator",
            "📄 Resume Generator",
            "✉️ Cover Letter Generator",
            "🔍 Job Search",
            "🎤 Interview Simulator",
        ],
        key="main_nav_radio",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Display the main introductory section only if not verified
if not st.session_state.get("verification_completed", False):
    st.markdown("""
<div style='text-align: center; margin-bottom: 1.5rem; padding: 1.5rem 1rem;
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
            border-radius: 24px; border: 1px solid rgba(16, 185, 129, 0.3);
            backdrop-filter: blur(20px);'>
    <h1 style='font-size: 2.8rem; font-weight: 800; 
                color: #f8fafc !important;
                text-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
                margin-bottom: 0.5rem; letter-spacing: -0.5px;'>
        ResuMate - AI Career Assistant
    </h1>
    <div style='font-size: 1.3rem; color: #cbd5e1; font-weight: 500; max-width: 600px; margin: 0 auto;'>
        Transform your career journey with cutting-edge AI tools for portfolios, resumes, and interview preparation
    </div>
    <div style='margin-top: 1.5rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;'>
        <span style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    color: white; padding: 0.4rem 1rem; border-radius: 20px; 
                    font-size: 0.9rem; font-weight: 600;'>
            ✨ AI-Powered
        </span>
        <span style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
                    color: white; padding: 0.4rem 1rem; border-radius: 20px; 
                    font-size: 0.9rem; font-weight: 600;'>
            🎯 Professional
        </span>
        <span style='background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); 
                    color: white; padding: 0.4rem 1rem; border-radius: 20px; 
                    font-size: 0.9rem; font-weight: 600;'>
            🚀 Modern
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

def format_salary_in_inr(salary_str):
    import re
    try:
        numbers = re.findall(r'\d+', salary_str.replace(',', ''))
        if not numbers:
            return salary_str
        if len(numbers) == 1:
            num = int(numbers[0])
            return f"₹{num:,.0f}"
        elif len(numbers) >= 2:
            num1, num2 = int(numbers[0]), int(numbers[1])
            return f"₹{num1:,.0f} - ₹{num2:,.0f}"
    except Exception:
        pass
    return salary_str

def initialize_services():
    groq_service = GroqLLM(GROQ_API_KEY)
    data_extractor = DataExtractor()
    portfolio_gen = PortfolioGenerator()
    resume_gen = ResumeGenerator()
    cover_letter_gen = CoverLetterGenerator()
    job_searcher = JobSearcher()
    interview_sim = InterviewSimulator(groq_service)
    return groq_service, data_extractor, portfolio_gen, resume_gen, cover_letter_gen, job_searcher, interview_sim

services = initialize_services()
groq_service = services[0]
data_extractor = services[1]
portfolio_gen = services[2]
resume_gen = services[3]
cover_letter_gen = services[4]
job_searcher = services[5]
interview_sim = services[6]

if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = {}
if "verification_completed" not in st.session_state:
    st.session_state.verification_completed = False
if "qa_completed" not in st.session_state:
    st.session_state.qa_completed = False
if "resume_content" not in st.session_state:
    st.session_state.resume_content = None
if "generated_portfolio" not in st.session_state:
    st.session_state.generated_portfolio = None
if "cover_letter_content" not in st.session_state:
    st.session_state.cover_letter_content = None
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def data_input_page(data_extractor):
    st.markdown("""
    <h1 style='text-align:left; font-size:2.7rem; font-weight:900; color:#2563eb; letter-spacing:-1px; margin-bottom:0.5em; text-shadow:0 2px 12px rgba(37,99,235,0.18); font-family:Inter,sans-serif; cursor: pointer; transition: color 0.2s ease;'
    onmouseover="this.style.color='#60a5fa'" onmouseout="this.style.color='#2563eb'">
        📤 Data Input
    </h1>
    """, unsafe_allow_html=True)
    st.markdown("Upload your resume to automatically extract and edit your profile information.")
    
    st.subheader("📄 Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Upload your CV/Resume for automatic data extraction", 
        type=["pdf", "docx", "jpg", "jpeg", "png"],
        help="Upload your resume and we'll automatically extract your information"
    )
    
    if uploaded_file and not st.session_state.verification_completed:
        with st.spinner("🤖 Extracting and analyzing your resume..."):
            extracted_text = data_extractor.extract_from_file(uploaded_file)
            
            if extracted_text:
                groq_service = initialize_services()[0]
                if groq_service:
                    parsed_data = groq_service.parse_resume_data(extracted_text)
                    st.session_state.extracted_data = parsed_data
                    st.session_state.user_data.update(parsed_data)
                    st.session_state.verification_completed = True
                    st.success("✅ Resume processed successfully!")
                    st.rerun()
                else:
                    st.error("Failed to initialize AI service")
            else:
                st.error("Failed to extract text from file")
    
    if st.session_state.verification_completed and st.session_state.extracted_data:
        st.subheader("✏️ Review and Edit Your Information")
        st.info("Review the automatically extracted information and edit as needed:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name_col1, name_col2 = st.columns([3, 1])
            with name_col1:
                current_name = st.session_state.user_data.get('name', 'Not found')
                st.text_input("Full Name", value=current_name, key="edit_name", disabled=True)
            with name_col2:
                if st.button("✏️", key="edit_name_btn", help="Edit Name"):
                    st.session_state.editing_name = True
            
            if st.session_state.get('editing_name', False):
                new_name = st.text_input("Enter new name:", value=current_name, key="new_name")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Save", key="save_name"):
                        st.session_state.user_data['name'] = new_name
                        st.session_state.editing_name = False
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel", key="cancel_name"):
                        st.session_state.editing_name = False
                        st.rerun()
            
            email_col1, email_col2 = st.columns([3, 1])
            with email_col1:
                current_email = st.session_state.user_data.get('email', 'Not found')
                st.text_input("Email", value=current_email, key="edit_email", disabled=True)
            with email_col2:
                if st.button("✏️", key="edit_email_btn", help="Edit Email"):
                    st.session_state.editing_email = True
            
            if st.session_state.get('editing_email', False):
                new_email = st.text_input("Enter new email:", value=current_email, key="new_email")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Save", key="save_email"):
                        st.session_state.user_data['email'] = new_email
                        st.session_state.editing_email = False
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel", key="cancel_email"):
                        st.session_state.editing_email = False
                        st.rerun()
            
            phone_col1, phone_col2 = st.columns([3, 1])
            with phone_col1:
                current_phone = st.session_state.user_data.get('phone', 'Not found')
                st.text_input("Phone", value=current_phone, key="edit_phone", disabled=True)
            with phone_col2:
                if st.button("✏️", key="edit_phone_btn", help="Edit Phone"):
                    st.session_state.editing_phone = True
            
            if st.session_state.get('editing_phone', False):
                new_phone = st.text_input("Enter new phone:", value=current_phone, key="new_phone")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Save", key="save_phone"):
                        st.session_state.user_data['phone'] = new_phone
                        st.session_state.editing_phone = False
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel", key="cancel_phone"):
                        st.session_state.editing_phone = False
                        st.rerun()
        
        with col2:
            title_col1, title_col2 = st.columns([3, 1])
            with title_col1:
                current_title = st.session_state.user_data.get('title', 'Not found')
                st.text_input("Job Title", value=current_title, key="edit_title", disabled=True)
            with title_col2:
                if st.button("✏️", key="edit_title_btn", help="Edit Title"):
                    st.session_state.editing_title = True
            
            if st.session_state.get('editing_title', False):
                new_title = st.text_input("Enter new title:", value=current_title, key="new_title")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Save", key="save_title"):
                        st.session_state.user_data['title'] = new_title
                        st.session_state.editing_title = False
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel", key="cancel_title"):
                        st.session_state.editing_title = False
                        st.rerun()
            
            education_col1, education_col2 = st.columns([3, 1])
            with education_col1:
                current_education = st.session_state.user_data.get('education', 'Not found')
                st.text_area("Education", value=current_education, key="edit_education", disabled=True, height=100)
            with education_col2:
                if st.button("✏️", key="edit_education_btn", help="Edit Education"):
                    st.session_state.editing_education = True
            
            if st.session_state.get('editing_education', False):
                new_education = st.text_area("Enter new education:", value=current_education, key="new_education", height=100)
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Save", key="save_education"):
                        st.session_state.user_data['education'] = new_education
                        st.session_state.editing_education = False
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel", key="cancel_education"):
                        st.session_state.editing_education = False
                        st.rerun()
        
        st.subheader("🛠️ Skills")
        skills_col1, skills_col2 = st.columns([3, 1])
        with skills_col1:
            current_skills = st.session_state.user_data.get('skills', [])
            skills_str = ', '.join(current_skills) if isinstance(current_skills, list) else str(current_skills)
            st.text_area("Skills", value=skills_str, key="edit_skills", disabled=True, height=80)
        with skills_col2:
            if st.button("✏️", key="edit_skills_btn", help="Edit Skills"):
                st.session_state.editing_skills = True
        
        if st.session_state.get('editing_skills', False):
            new_skills = st.text_area("Enter skills (comma-separated):", value=skills_str, key="new_skills", height=80)
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 Save", key="save_skills"):
                    skills_list = [skill.strip() for skill in new_skills.split(',') if skill.strip()]
                    st.session_state.user_data['skills'] = skills_list
                    st.session_state.editing_skills = False
                    st.rerun()
            with col_cancel:
                if st.button("❌ Cancel", key="cancel_skills"):
                    st.session_state.editing_skills = False
                    st.rerun()
        
        st.subheader("💼 Work Experience")
        exp_col1, exp_col2 = st.columns([3, 1])
        with exp_col1:
            current_experience = st.session_state.user_data.get('experience', 'Not found')
            st.text_area("Experience", value=current_experience, key="edit_experience", disabled=True, height=120)
        with exp_col2:
            if st.button("✏️", key="edit_experience_btn", help="Edit Experience"):
                st.session_state.editing_experience = True
        
        if st.session_state.get('editing_experience', False):
            new_experience = st.text_area("Enter your experience:", value=current_experience, key="new_experience", height=120)
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 Save", key="save_experience"):
                    st.session_state.user_data['experience'] = new_experience
                    st.session_state.editing_experience = False
                    st.rerun()
            with col_cancel:
                if st.button("❌ Cancel", key="cancel_experience"):
                    st.session_state.editing_experience = False
                    st.rerun()
        
        st.subheader("📋 Profile Summary")
        summary_data = {
            'Name': st.session_state.user_data.get('name', 'N/A'),
            'Email': st.session_state.user_data.get('email', 'N/A'), 
            'Phone': st.session_state.user_data.get('phone', 'N/A'),
            'Title': st.session_state.user_data.get('title', 'N/A'),
            'Skills Count': len(st.session_state.user_data.get('skills', [])),
            'Verification': 'Resume Upload ✅'
        }
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fields Completed", len([v for v in summary_data.values() if v != 'N/A']), "out of 6")
        with col2:
            st.metric("Skills Extracted", summary_data['Skills Count'])
        with col3:
            if st.button("🔄 Re-upload Resume"):
                st.session_state.verification_completed = False
                st.session_state.extracted_data = {}
                st.rerun()
        
        extracted_projects = st.session_state.user_data.get('projects', [])
        if extracted_projects:
            st.subheader("🚀 Projects Extracted from Resume")
            st.info(f"Found {len(extracted_projects)} project(s) in your resume. These will be automatically included in your portfolio generation.")
            
            for i, project in enumerate(extracted_projects, 1):
                with st.expander(f"📁 Project {i}: {project.get('title', 'Untitled Project')}", expanded=False):
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        if st.session_state.get(f'editing_project_{i}', False):
                            with st.form(f"edit_project_form_{i}"):
                                st.markdown("**✏️ Edit Project Details:**")
                                new_title = st.text_input("Project Title:", value=project.get('title', ''), key=f"edit_title_{i}")
                                new_description = st.text_area("Description:", value=project.get('description', ''), height=100, key=f"edit_desc_{i}")
                                new_technologies = st.text_input("Technologies:", value=project.get('technologies', 'Not specified'), key=f"edit_tech_{i}")
                                new_duration = st.text_input("Duration:", value=project.get('duration', 'Not specified'), key=f"edit_duration_{i}")
                                
                                col_save, col_cancel = st.columns(2)
                                with col_save:
                                    save_changes = st.form_submit_button("💾 Save Changes", type="primary")
                                with col_cancel:
                                    cancel_edit = st.form_submit_button("❌ Cancel")
                                
                                if save_changes:
                                    st.session_state.user_data['projects'][i-1] = {
                                        'title': new_title,
                                        'description': new_description,
                                        'technologies': new_technologies,
                                        'duration': new_duration
                                    }
                                    st.session_state[f'editing_project_{i}'] = False
                                    st.success(f"✅ Project '{new_title}' updated successfully!")
                                    st.rerun()                                
                                if cancel_edit:
                                    st.session_state[f'editing_project_{i}'] = False
                                    st.rerun()
                        
                        else:
                            st.write(f"**Description:** {project.get('description', 'No description available')}")
                            if project.get('technologies', 'Not specified') != 'Not specified':
                                st.write(f"**Technologies:** {project.get('technologies')}")
                            if project.get('duration', 'Not specified') != 'Not specified':
                                st.write(f"**Duration:** {project.get('duration')}")
                    
                    with col_actions:
                        if not st.session_state.get(f'editing_project_{i}', False):
                            if st.button("✏️", key=f"edit_project_btn_{i}", help="Edit this project"):
                                st.session_state[f'editing_project_{i}'] = True
                                st.rerun()
                            if st.button("🗑️", key=f"delete_project_btn_{i}", help="Delete this project"):
                                st.session_state.user_data['projects'].pop(i-1)
                                st.success(f"🗑️ Project deleted successfully!")
                                st.rerun()
            
            st.markdown("---")
            if st.button("➕ Add New Project", type="secondary", use_container_width=True):
                st.session_state.adding_new_project = True
                st.rerun()
            
            if st.session_state.get('adding_new_project', False):
                with st.form("add_new_project_form"):
                    st.markdown("**➕ Add New Project:**")
                    new_project_title = st.text_input("Project Title:", placeholder="e.g., E-commerce Website")
                    new_project_description = st.text_area("Description:", height=100, 
                                                            placeholder="Describe your project, technologies used, and achievements...")
                    new_project_technologies = st.text_input("Technologies:", placeholder="e.g., Python, React, AWS")
                    new_project_duration = st.text_input("Duration:", placeholder="e.g., 3 months, Jan-Mar 2024")
                    
                    col_add, col_cancel_add = st.columns(2)
                    with col_add:
                        add_project = st.form_submit_button("➕ Add Project", type="primary")
                    with col_cancel_add:
                        cancel_add = st.form_submit_button("❌ Cancel")
                    
                    if add_project and new_project_title and new_project_description:
                        new_project = {
                            'title': new_project_title,
                            'description': new_project_description,
                            'technologies': new_project_technologies or 'Not specified',
                            'duration': new_project_duration or 'Not specified'
                        }
                        if 'projects' not in st.session_state.user_data:
                            st.session_state.user_data['projects'] = []
                        st.session_state.user_data['projects'].append(new_project)
                        st.session_state.adding_new_project = False
                        st.success(f"✅ Project '{new_project_title}' added successfully!")
                        st.rerun()
                    
                    if cancel_add:
                        st.session_state.adding_new_project = False
                        st.rerun()
    
    elif not uploaded_file:
        st.subheader("✏️ Manual Information Entry")
        st.info("💡 Upload a resume above for automatic extraction, or fill in manually below:")
        
        with st.form("manual_form"):
            name = st.text_input("Full Name:")
            email = st.text_input("Email:")
            phone = st.text_input("Phone:")
            title = st.text_input("Current/Desired Job Title:")
            experience = st.text_area("Work Experience (brief):", key="manual_experience_input")
            skills = st.text_input("Key Skills (comma-separated):")
            education = st.text_input("Education:")
            
            submitted = st.form_submit_button("Save Information")
            
            if submitted:
                if name and email and title:
                    qa_data = {
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'title': title,
                        'experience': experience,
                        'skills': skills.split(',') if skills else [],
                        'education': education,
                        'source': 'manual'
                    }
                    st.session_state.user_data.update(qa_data)
                    st.session_state.verification_completed = True
                    st.success("✅ Information saved!")
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in at least Name, Email, and Job Title")
    
    elif st.session_state.qa_completed and not st.session_state.verification_completed:
        st.subheader("Step 2: Verification (Mandatory)")
        st.warning("⚠️ You must verify your information to proceed to other features.")
        
        verification_method = st.radio("Choose verification method:", [
            "Upload CV/Resume",
            "LinkedIn Profile URL"
        ])
        
        if verification_method == "Upload CV/Resume":
            uploaded_file = st.file_uploader(
                "Upload your CV/Resume", 
                type=["pdf", "docx", "jpg", "jpeg", "png"]
            )
            if uploaded_file:
                try:
                    with st.spinner("Extracting and verifying data..."):
                        extracted_text = data_extractor.extract_from_file(uploaded_file)
                        if extracted_text:
                            st.success("✅ Resume uploaded and verified successfully!")
                            st.text_area("Extracted Content", extracted_text, height=200, key="extracted_content_display")
                        
                        st.session_state.user_data['cv_text'] = extracted_text
                        st.session_state.user_data['verification_source'] = 'cv_upload'
                        st.session_state.verification_completed = True
                        
                        if st.button("Complete Profile"):
                            st.success("🎉 Profile completed! You can now use all features.")
                            st.rerun()
                except Exception as e:
                    st.error("Failed to extract text from file")
        
        elif verification_method == "LinkedIn Profile URL":
            linkedin_url = st.text_input("Enter your LinkedIn profile URL:")
            
            if st.button("Verify LinkedIn Profile"):
                if linkedin_url:
                    with st.spinner("Extracting and verifying LinkedIn data..."):
                        linkedin_data = data_extractor.extract_from_linkedin(linkedin_url)
                        
                    if linkedin_data:
                        st.success("✅ LinkedIn profile verified successfully!")
                        st.json(linkedin_data)
                        st.session_state.user_data.update(linkedin_data)
                        st.session_state.user_data['verification_source'] = 'linkedin'
                        st.session_state.verification_completed = True
                        
                        if st.button("Complete Profile"):
                            st.success("🎉 Profile completed! You can now use all features.")
                            st.rerun()
                    else:
                        st.error("Failed to extract LinkedIn data")
    
    elif st.session_state.qa_completed and st.session_state.verification_completed:
        st.success("✅ Profile completed successfully!")
        st.markdown("**Your Information:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** {st.session_state.user_data.get('name', 'N/A')}")
            st.write(f"**Email:** {st.session_state.user_data.get('email', 'N/A')}")
            st.write(f"**Phone:** {st.session_state.user_data.get('phone', 'N/A')}")
        
        with col2:
            st.write(f"**Title:** {st.session_state.user_data.get('title', 'N/A')}")
            st.write(f"**Verification:** {st.session_state.user_data.get('verification_source', 'N/A')}")
        
        if st.button("Reset Profile"):
            st.session_state.qa_completed = False
            st.session_state.verification_completed = False
            st.session_state.user_data = {}
            st.rerun()

def portfolio_page(groq_service, portfolio_gen):
    st.header("🌐 Portfolio Generator")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("Please complete your profile verification in the Data Input page first.")
        return
    
    if 'generated_portfolio' not in st.session_state:
        st.session_state.generated_portfolio = None
        st.session_state.portfolio_html = None
        st.session_state.portfolio_template_data = None
    
    st.markdown("### AI-Powered Portfolio Generation")
    st.info("🤖 Your portfolio will be intelligently generated using AI based on your profile data, skills, and experience.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        portfolio_style = st.selectbox("Choose Portfolio Style:", [
            "Modern Professional",
            "Creative Designer", 
            "Tech Developer",
            "Business Executive",
            "Minimalist Clean"        ])
        
        include_projects = st.checkbox("Generate AI project examples", value=False, 
                                    help="AI will create realistic project examples based on your skills (only if you don't have actual projects)")
        
        color_scheme = st.selectbox("Color Scheme:", ["Blue Gradient (Professional)",
            "Purple Gradient (Creative)", 
            "Green Gradient (Tech)",            "Orange Gradient (Energy)",
            "Dark Theme (Modern)"
        ])
    
    with col2:
        st.markdown("**Your Profile:**")
        st.write(f"✅ **Name:** {st.session_state.user_data.get('name', 'N/A')}")
        st.write(f"✅ **Title:** {st.session_state.user_data.get('title', 'N/A')}")
        st.write(f"✅ **Skills:** {len(st.session_state.user_data.get('skills', []))} skills")
        
        resume_extracted_projects = len(st.session_state.user_data.get('projects', []))
        manual_resume_projects = len(st.session_state.get('resume_projects', []))
        total_projects = resume_extracted_projects + manual_resume_projects
        
        if total_projects > 0:
            st.write(f"🚀 **Projects Available:** {total_projects}")
            if resume_extracted_projects > 0:
                st.write(f"  └─ From resume: {resume_extracted_projects}")
            if manual_resume_projects > 0:
                st.write(f"  └─ Manual entry: {manual_resume_projects}")
        else:
            st.write("🚀 **Projects:** None (AI will generate if enabled)")
    
    if st.button("🚀 Generate AI Portfolio", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is crafting your professional portfolio..."):
            enhanced_user_data = st.session_state.user_data.copy()
            enhanced_user_data['portfolio_style'] = portfolio_style
            enhanced_user_data['color_scheme'] = color_scheme
            enhanced_user_data['include_projects'] = include_projects
            
            portfolio_content = groq_service.generate_enhanced_portfolio(enhanced_user_data)
            
            st.session_state.generated_portfolio = portfolio_content
            st.session_state.portfolio_settings = {
                'portfolio_style': portfolio_style,
                'color_scheme': color_scheme,
                'include_projects': include_projects
            }
    
    if st.session_state.generated_portfolio:
        portfolio_content = st.session_state.generated_portfolio
        settings = st.session_state.portfolio_settings
        
        st.success("✅ AI Portfolio generated successfully!")
        
        with st.expander("📋 View Generated Content", expanded=False):
            st.json(portfolio_content)
        
        try:
            template_data = {
                'name': st.session_state.user_data.get('name'),
                'headline': portfolio_content.get('headline', st.session_state.user_data.get('title', 'Professional')),
                'about': portfolio_content.get('about', st.session_state.user_data.get('summary', 'Experienced professional')),
                'skills': [],
                'experience': [],
                'education': [],
                'projects': [],
                'email': st.session_state.user_data.get('email'),
                'phone': st.session_state.user_data.get('phone'),
                'linkedin': st.session_state.user_data.get('linkedin'),
                'portfolio_style': settings.get('portfolio_style'),
                'color_scheme': settings.get('color_scheme')
            }
            user_skills = st.session_state.user_data.get('skills', [])
            if user_skills:
                template_data['skills'] = user_skills
            elif 'skills_categories' in portfolio_content:
                all_skills = []
                for category, skills in portfolio_content['skills_categories'].items():
                    if isinstance(skills, list):
                        all_skills.extend(skills)
                template_data['skills'] = all_skills
            elif portfolio_content.get('skills'):
                template_data['skills'] = portfolio_content['skills']
            else:
                template_data['skills'] = ['Communication', 'Problem Solving', 'Leadership']
            user_work_experience = st.session_state.user_data.get('work_experience', [])
            user_experience = st.session_state.user_data.get('experience', '')
            ai_experience = portfolio_content.get('experience', [])
            
            if user_work_experience:
                template_data['experience'] = user_work_experience
            elif user_experience:
                template_data['experience'] = [{
                    'title': st.session_state.user_data.get('title', 'Professional'),
                    'company': 'Professional Experience',
                    'duration': 'Current',
                    'description': user_experience
                }]
            elif ai_experience:
                template_data['experience'] = ai_experience
            else:
                template_data['experience'] = []
            user_education = st.session_state.user_data.get('education', '')
            ai_education = portfolio_content.get('education', '')
            
            if user_education:
                template_data['education'] = user_education
            elif ai_education:
                template_data['education'] = ai_education
            else:
                template_data['education'] = 'Educational background'           
            user_projects = st.session_state.user_data.get('projects', [])
            resume_projects = st.session_state.get('resume_projects', [])
            ai_projects = portfolio_content.get('projects', [])
            
            all_projects = []
            
            if user_projects:
                all_projects.extend(user_projects)
            
            if resume_projects:
                all_projects.extend(resume_projects)
            
            if settings.get('include_projects') and ai_projects:
                all_projects.extend(ai_projects)
            
            template_data['projects'] = all_projects
            st.session_state.portfolio_template_data = template_data
            html_content = portfolio_gen.generate_html(template_data)
            st.session_state.portfolio_html = html_content;
            
            st.subheader("🌟 Portfolio Preview")
            st.components.v1.html(html_content, height=900, scrolling=True)
            
            st.download_button(
                label="📥 Download HTML",
                data=html_content,
                file_name=f"portfolio_{template_data.get('name', 'portfolio').replace(' ', '_').lower()}.html",
                mime="text/html",
                use_container_width=True
            )
            st.markdown("### 🚀 Deploy Your Portfolio")
            deployment_option = st.selectbox(
                "Choose deployment platform:",
                ["Select Platform", "Vercel", "Netlify", "GitHub Pages"],
                key="portfolio_deployment_select"
            )
                
            if deployment_option != "Select Platform":
                deployment_urls = {
                    "Vercel": "https://vercel.com/new",
                    "Netlify": "https://app.netlify.com/drop", 
                    "GitHub Pages": "https://pages.github.com/"
                }
                    
                if deployment_option in deployment_urls:
                    st.link_button(
                        f"🌐 Deploy to {deployment_option}",
                        deployment_urls[deployment_option],
                        use_container_width=True
                    )
                    st.success(f"🎉 Click the button above to open {deployment_option} deployment page!")
                    st.info(f"💡 Upload your downloaded HTML file to {deployment_option} to deploy your portfolio.")
                else:
                    st.info("💡 Select a deployment platform to get started!")
        except Exception as e:
            st.error(f"❌ Error generating portfolio: {str(e)}")
            st.info("💡 Try regenerating or contact support if the issue persists.")
    else:
        st.info("🚀 Click 'Generate AI Portfolio' above to create your professional portfolio!")

def resume_page(groq_service, resume_gen):
    st.header("📄 AI Resume Generator")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        return
    
    st.markdown("### 📋 Basic Information from Resume")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Name", value=st.session_state.user_data.get('name', 'N/A'), disabled=True)
        st.text_input("Email", value=st.session_state.user_data.get('email', 'N/A'), disabled=True)
    with col2:
        st.text_input("Phone", value=st.session_state.user_data.get('phone', 'N/A'), disabled=True)
        st.text_area("Education", value=st.session_state.user_data.get('education', 'N/A'), disabled=True, height=100, key="resume_education_display")
    
    st.markdown("### 💼 Enter Your Skills and Experience")
    st.info("Please provide your skills and experience manually for the best resume generation.")
    
    user_skills = st.text_area(
        "💼 Enter Your Skills and Experience:",
        height=150,
        placeholder="Enter your technical skills, soft skills, certifications, and key experiences here. Separate with commas or line breaks.\n\nExample:\nPython, JavaScript, React, Node.js\nProject Management, Team Leadership\nAWS, Docker, Kubernetes\n5 years software development experience",
        help="List all your relevant skills, technologies, certifications, and experience. The AI will use this to generate your resume.",        key="resume_skills_input"
    )
    
    st.markdown("### 🚀 Project Management")
    st.info("Add your projects to enhance your resume. AI will format them using the STAR method (Situation, Task, Action, Result).")
    if 'resume_projects' not in st.session_state:
        st.session_state.resume_projects = []
    
    extracted_projects = st.session_state.user_data.get('projects', [])
    if extracted_projects:
        import_resume_projects = st.checkbox(
            f"📥 Import projects from resume ({len(extracted_projects)} projects available)",
            value=False,
            help="Automatically add projects that were extracted from your uploaded resume"
        )
        if import_resume_projects:
            existing_titles = {p.get('title') for p in st.session_state.resume_projects}
            new_projects = [p for p in extracted_projects if p.get('title') not in existing_titles]
            if new_projects:
                st.session_state.resume_projects.extend(new_projects)
                st.success(f"✅ Imported {len(new_projects)} project(s) from resume.")
                st.rerun()
    
    with st.expander("➕ Add New Project", expanded=False):
        with st.form("project_form"):
            project_title = st.text_input("🏗️ Project Title:", placeholder="e.g., E-commerce Website")
            project_description = st.text_area(
                "📝 Project Description:", 
                height=100,
                placeholder="Describe your project, your role, challenges faced, and outcomes achieved...\n\nExample:\nDeveloped a full-stack e-commerce website for a local business. Led a team of 3 developers, implemented secure payment processing, and deployed using AWS. Resulted in 40% increase in online sales.",
                key="resume_project_description"
            )
            col_tech, col_duration, col_progress = st.columns(3)
            with col_tech:
                technologies = st.text_input("🛠️ Technologies Used:", placeholder="React, Node.js, MongoDB, AWS")
            with col_duration:
                duration = st.text_input("⏱️ Duration:", placeholder="3 months, Jan-Mar 2024")
            with col_progress:
                still_working = st.checkbox("Still Work in Progress?", key="project_progress")
            
            submit_project = st.form_submit_button("➕ Add Project", type="primary")
            if submit_project and project_title and project_description:
                new_project = {
                    'title': project_title,
                    'description': project_description,
                    'technologies': technologies,
                    'duration': duration if not still_working else "Ongoing",
                    'still_working': still_working                }
                st.session_state.resume_projects.append(new_project)
                st.success(f"✅ Project '{project_title}' added successfully!")
                st.rerun()
        
    if st.session_state.resume_projects:
        st.markdown("**📋 Your Projects:**")
        for i, project in enumerate(st.session_state.resume_projects):
            with st.container():
                col_project, col_remove = st.columns([4, 1])
                with col_project:
                    st.markdown(f"**{project['title']}**")
                    if project.get('still_working'):
                        st.write("🚧 Work in Progress")
                    st.write(f"📝 {project['description'][:100]}...")
                    if project['technologies']:
                        st.write(f"🛠️ Technologies: {project['technologies']}")
                    if project['duration']:
                        st.write(f"⏱️ Duration: {project['duration']}")
                with col_remove:
                    if st.button("🗑️", key=f"remove_project_{i}", help="Remove project"):
                        st.session_state.resume_projects.pop(i)
                        st.rerun()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        job_description = st.text_area(
            "🎯 Target Job Description (Optional - for AI tailoring):",
            height=120,
            key="resume_job_description_input",
            placeholder="Paste the job description here for AI to tailor your resume specifically for this role...",
            help="AI will analyze the job requirements and optimize your resume accordingly"
        )
        
        resume_style = st.selectbox("Resume Format:", [
            "Professional ATS-Optimized",
            "Creative Professional",
            "Executive Leadership",
            "Technical Specialist",
            "Entry Level Focus"
        ])
    
    with col2:
        st.markdown("**Profile Summary:**")
        st.write(f"👤 **Name:** {st.session_state.user_data.get('name', 'N/A')}")
        st.write(f"💼 **Title:** {st.session_state.user_data.get('title', 'N/A')}")
        st.write(f"📧 **Email:** {st.session_state.user_data.get('email', 'N/A')}")
        
        if user_skills:
            skills_count = len([skill.strip() for skill in user_skills.replace('\n', ',').split(',') if skill.strip()])
            st.write(f"🛠️ **Skills Entered:** {skills_count}")

        if hasattr(st.session_state, 'resume_projects') and st.session_state.resume_projects:
            project_count = len(st.session_state.resume_projects)
            st.write(f"🚀 **Projects Added:** {project_count}")
        
        if job_description:
            st.markdown("**🎯 AI Analysis:**")
            with st.spinner("Analyzing job requirements..."):
                temp_data = st.session_state.user_data.copy()
                temp_data['skills_input'] = user_skills
                analysis = groq_service.analyze_job_requirements(job_description, temp_data)
                st.success(f"✅ AI found {analysis.get('keyword_matches', 0)} matching keywords")
    
    if st.button("🚀 Generate AI Resume", type="primary", use_container_width=True, key="generate_resume_btn_2"):
        if not user_skills.strip():
            st.error("⚠️ Please enter your skills and experience to generate a resume.")
            return
        
        with st.spinner("🤖 AI is crafting your professional resume..."):
            enhanced_data = st.session_state.user_data.copy()
            enhanced_data['resume_style'] = resume_style
            enhanced_data['skills_input'] = user_skills
            enhanced_data['projects'] = st.session_state.resume_projects
            
            skills_list = []
            for line in user_skills.split('\n'):
                for skill in line.split(','):
                    skill = skill.strip()
                    if skill:
                        skills_list.append(skill)
            enhanced_data['skills'] = skills_list
            
            if job_description:
                enhanced_data['target_job'] = job_description
                resume_content = groq_service.generate_tailored_resume(enhanced_data, job_description)
            else:
                resume_content = groq_service.generate_enhanced_resume(enhanced_data)
            
            if resume_content:
                st.session_state.resume_content = resume_content
                st.session_state.resume_generated_data = {
                    'user_skills': user_skills,
                    'job_description': job_description,
                    'resume_style': resume_style,
                    'enhanced_data': enhanced_data,                    'projects': st.session_state.resume_projects
                }
                st.success("✅ AI Resume generated successfully!")
    if st.session_state.resume_content:
        resume_content = st.session_state.resume_content
        generated_data = st.session_state.resume_generated_data
        
        st.subheader("📋 Resume Content")
        st.markdown(resume_content)
        
        formatted_resume = resume_gen.format_resume_text(resume_content, st.session_state.user_data)
        st.download_button(
            label="📥 Save Text",
            data=formatted_resume,
            file_name=f"resume_{st.session_state.user_data.get('name', 'resume').replace(' ', '_').lower()}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        if st.button("🗑️ Clear Generated Resume"):
            st.session_state.resume_content = None
            st.session_state.resume_generated_data = {}
            st.rerun()
        
        if generated_data.get('job_description'):
            st.subheader("🎯 AI Job Match Analysis")
            match_analysis = groq_service.analyze_resume_job_match(resume_content, generated_data['job_description'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Match Score", f"{match_analysis.get('match_percentage', 75)}%")
            with col2:
                st.metric("Keywords Found", match_analysis.get('keyword_matches', 8))
            with col3:
                st.metric("ATS Score", f"{match_analysis.get('ats_score', 82)}%")
            
            if match_analysis.get('suggestions'):
                st.markdown("**🔧 AI Improvement Suggestions:**")
                for suggestion in match_analysis.get('suggestions', []):
                    st.write(f"• {suggestion}")
    else:
        st.info("🚀 Click 'Generate AI Resume' above to create your professional resume!")

def render_detailed_job_view(job, index):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"📍 **Location:** {job.get('location', 'N/A')}")
        salary_display = format_salary_in_inr(job.get('salary_range', 'Not specified'))
        st.write(f"💰 **Salary:** {salary_display}")
        st.write(f"📅 **Posted:** {job.get('posted_date', 'Recently')}")
        st.write(f"🏢 **Company Size:** {job.get('company_size', 'Not specified')}")
        st.write(f"⏰ **Type:** {job.get('employment_type', 'Full-time')}")
        
        if job.get('remote_type'):
            st.write("🏠 **Remote-friendly**")
        
        st.write(f"📋 **Description:** {job.get('description', 'No description available')[:300]}...")
        
        if job.get('skills'):
            st.write(f"🛠️ **Key Skills:** {', '.join(job.get('skills', [])[:5])}")
        
        if job.get('benefits'):
            st.write(f"💎 **Benefits:** {', '.join(job.get('benefits', [])[:3])}...")
        
        if job.get('ai_analysis'):
            analysis = job.get('ai_analysis')
            st.markdown("**🤖 AI Analysis:**")
            
            tab1, tab2, tab3 = st.tabs(["📊 Match Analysis", "💡 Market Insights", "🎯 Application Tips"])
            
            with tab1:
                st.info(f"**Match Level:** {analysis.get('match_level', 'N/A')}")
                if analysis.get('matched_keywords'):
                    st.success(f"**Matched Keywords:** {', '.join(analysis.get('matched_keywords', [])[:5])}")
                if analysis.get('missing_skills'):
                    st.warning(f"**Skills to Develop:** {', '.join(analysis.get('missing_skills', [])[:3])}")
            
            with tab2:
                market_insights = job.get('market_insights', {})
                col_market1, col_market2 = st.columns(2)
                with col_market1:
                    st.metric("📈 Demand Level", market_insights.get('demand_level', 'Medium'))
                    st.metric("💰 Salary Competitiveness", market_insights.get('salary_competitiveness', 'Competitive'))
                with col_market2:
                    st.metric("🚀 Growth Potential", market_insights.get('growth_potential', 'Good'))
                    st.metric("🎯 Industry Trend", market_insights.get('industry_trend', 'Stable'))
            
            with tab3:
                if job.get('application_tips'):
                    for tip in job.get('application_tips', [])[:3]:
                        st.info(f"💡 {tip}")
                else:
                    st.info("💡 Tailor your resume to highlight relevant experience")
                    st.info("🎯 Research the company culture and values")
                    st.info("📝 Write a compelling cover letter")
    
    with col2:
        source = job.get('source', 'web_scraper')
        source_names = {
            'indeed': 'Indeed',
            'linkedin': 'LinkedIn',
            'glassdoor': 'Glassdoor',
            'google_jobs_api': 'Google Jobs',
            'web_scraper': 'Multi-Platform'
        }
        st.info(f"🌐 **Source:** {source_names.get(source, 'Unknown')}")
        
        platform_name = job.get('application_platform', 'LinkedIn')
        platform_icon = job.get('platform_icon', '💼')
        
        if job.get('linkedin_url'):
            st.link_button("💼 View on LinkedIn", job['linkedin_url'], use_container_width=True)
        
        if job.get('application_url'):
            st.link_button(f"{platform_icon} Apply on {platform_name}", job['application_url'], use_container_width=True)
        
        col_action1, col_action2 = st.columns(2)
        
        with col_action1:
            if st.button(f"💾 Save Job", key=f"save_{index}", use_container_width=True):
                if 'saved_jobs' not in st.session_state:
                    st.session_state.saved_jobs = []
                st.session_state.saved_jobs.append(job)
                st.success("Job saved!")
        
        with col_action2:
            if st.button(f"📝 Generate Cover Letter", key=f"cover_{index}", use_container_width=True):
                st.session_state.cover_letter_job = job
                st.success("Job selected for cover letter!")
        
        try:
            match_score = int(str(job.get('ai_analysis', {}).get('match_score', job.get('ai_match_score', '0'))).replace('%', ''))
            st.progress(match_score / 100, f"AI Match: {match_score}%")
        except:
            st.progress(0.7, "AI Match: Good")

def cover_letter_page(groq_service, cover_letter_gen):
    st.header("✉️ AI Cover Letter Generator")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    st.markdown("### 📋 Basic Information from Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Name", value=st.session_state.user_data.get('name', 'N/A'), disabled=True)
        st.text_input("Email", value=st.session_state.user_data.get('email', 'N/A'), disabled=True)
    with col2:
        st.text_input("Phone", value=st.session_state.user_data.get('phone', 'N/A'), disabled=True)
        st.text_input("Title", value=st.session_state.user_data.get('title', 'N/A'), disabled=True)
    
    st.markdown("### 🎯 Job & Company Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("🏢 Company Name:", placeholder="e.g., Google, Microsoft, Tesla")
        job_title = st.text_input("💼 Job Title:", placeholder="e.g., Software Engineer, Data Scientist")
    with col2:
        tone = st.selectbox("✍️ Writing Tone:", [
            "Professional", "Enthusiastic", "Confident", "Formal", "Creative"
        ])
        
    job_description = st.text_area(
        "📄 Job Description:",
        height=150,
        placeholder="Paste the complete job description here for AI to analyze requirements and tailor your cover letter accordingly...",
        help="The more detailed the job description, the better AI can customize your cover letter"
    )
    
    if st.session_state.get('cover_letter_job'):
        selected_job = st.session_state.cover_letter_job
        st.info(f"✅ Using job: **{selected_job.get('title', 'N/A')}** at **{selected_job.get('company', 'N/A')}**")
        if st.button("🗑️ Clear Selected Job"):
            del st.session_state.cover_letter_job
            st.rerun()
        
        if not company_name and selected_job.get('company'):
            company_name = selected_job.get('company')
        if not job_title and selected_job.get('title'):
            job_title = selected_job.get('title')
        if not job_description and selected_job.get('description'):
            job_description = selected_job.get('description')
    
    if st.button("🚀 Generate AI Cover Letter", type="primary", use_container_width=True):
        if not all([company_name, job_title, job_description]):
            st.error("⚠️ Please fill in Company Name, Job Title, and Job Description to generate a cover letter.")
            return
        
        with st.spinner("🤖 AI is crafting your personalized cover letter..."):
            try:
                cover_letter_content = groq_service.generate_enhanced_cover_letter(
                    user_data=st.session_state.user_data,
                    job_description=job_description,
                    company_name=company_name,
                    tone=tone
                )
                
                if cover_letter_content:
                    st.session_state.cover_letter_content = cover_letter_content
                    st.session_state.cover_letter_data = {
                        'company_name': company_name,
                        'job_title': job_title,
                        'job_description': job_description,
                        'tone': tone
                    }
                    st.success("✅ AI Cover Letter generated successfully!")
                else:
                    st.error("❌ Failed to generate cover letter. Please try again.")
            except Exception as e:
                st.error(f"❌ Error generating cover letter: {str(e)}")
    
    if st.session_state.get('cover_letter_content'):
        cover_letter_content = st.session_state.cover_letter_content
        cover_letter_data = st.session_state.get('cover_letter_data', {})
        
        st.subheader("📝 Generated Cover Letter")
        st.markdown(cover_letter_content)
        col1, col2 = st.columns(2)
        with col1:
            clean_content = cover_letter_gen._clean_cover_letter_content(cover_letter_content)
            try:
                formatted_cover_letter = cover_letter_gen.format_cover_letter_text(clean_content, st.session_state.user_data, cover_letter_data)
                st.download_button(
                    label="📥 Save Text",
                    data=formatted_cover_letter,
                    file_name=f"cover_letter_{cover_letter_data.get('company_name', 'company').replace(' ', '_').lower()}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Error generating text file: {str(e)}")
                st.button("📥 Text (Error)", disabled=True, use_container_width=True)
        
        with col2:
            if st.button("🗑️ Clear Cover Letter"):
                if 'cover_letter_content' in st.session_state:
                    del st.session_state.cover_letter_content
                if 'cover_letter_data' in st.session_state:
                    del st.session_state.cover_letter_data
                st.rerun()
    else:
        st.info("🚀 Fill in the job details above and click 'Generate AI Cover Letter' to create your personalized cover letter!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def job_search_page(job_searcher, groq_service):
    st.header("🔍 AI-Powered Job Search")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    st.markdown("### 🎯 Job Search Filters")
    col1, col2, col3 = st.columns(3)
    user_skills = st.session_state.user_data.get('skills', [])
    auto_skills = ", ".join(user_skills[:5]) if user_skills else ""
    
    with col1:
        job_title = st.text_input("💼 Job Title:", placeholder="e.g. Software Engineer, Data Scientist, Product Manager")
        location = st.text_input("📍 Location:", placeholder="e.g. New York, Remote")
    
    with col2:
        experience_level = st.selectbox("📈 Experience Level:", [
            "", "Entry Level", "Mid Level", "Senior Level", "Executive"
        ])
        job_type = st.selectbox("💼 Job Type:", [
            "Full-time", "Part-time", "Contract", "Internship", "Remote"
        ])
    
    with col3:
        limit = st.slider("📊 Results Limit:", 5, 50, 20)
    
    col_search1, col_search2, col_search3 = st.columns(3)
    
    with col_search1:
        if st.button("🔍 Search Jobs", type="primary", use_container_width=True):
            if not job_title.strip():
                st.error("⚠️ Please enter a job title to search for jobs.")
            else:
                with st.spinner("🤖 AI is searching for relevant jobs..."):
                    try:
                        jobs = job_searcher.search_jobs(
                            keywords=job_title,
                            location=location,
                            experience_level=experience_level,
                            job_type=job_type,
                            limit=limit
                        )
                        st.session_state.search_results = jobs
                        st.session_state.search_params = {
                            'job_title': job_title,
                            'location': location,
                            'experience_level': experience_level,
                            'job_type': job_type
                        }
                        st.success(f"✅ Found {len(jobs)} job opportunities!")
                    except Exception as e:
                        st.error(f"❌ Search failed: {str(e)}")
    
    with col_search2:
        if st.button("🔥 Trending Jobs", use_container_width=True):
            with st.spinner("🤖 Finding trending opportunities..."):
                try:
                    trending_jobs = job_searcher.get_trending_jobs(location or "Remote")
                    st.session_state.search_results = trending_jobs
                    st.session_state.search_params = {'type': 'trending', 'location': location}
                    st.success(f"✅ Found {len(trending_jobs)} trending opportunities!")
                except Exception as e:
                    st.error(f"❌ Failed to get trending jobs: {str(e)}")
    
    with col_search3:
        if st.button("🎯 AI Recommendations", use_container_width=True):
            with st.spinner("🤖 Getting personalized recommendations..."):
                try:
                    user_skills = st.session_state.user_data.get('skills', [])
                    recommended_jobs = job_searcher.get_job_recommendations(user_skills, location or "Remote")
                    st.session_state.search_results = recommended_jobs
                    st.session_state.search_params = {'type': 'recommendations', 'skills': user_skills}
                    st.success(f"✅ Found {len(recommended_jobs)} personalized recommendations!")
                except Exception as e:
                    st.error(f"❌ Failed to get recommendations: {str(e)}")
    
    if st.session_state.get('search_results'):
        jobs = st.session_state.search_results
        search_params = st.session_state.get('search_params', {})
        
        st.markdown("---")
        st.subheader(f"📋 Search Results ({len(jobs)} jobs found)")
        
        if search_params.get('type') == 'trending':
            st.info(f"🔥 Showing trending jobs for **{search_params.get('location', 'All locations')}**")
        elif search_params.get('type') == 'recommendations':
            skills_text = ", ".join(search_params.get('skills', [])[:3])
            st.info(f"🎯 Personalized recommendations based on your skills: **{skills_text}**")
        else:
            st.info(f"🔍 Results for **{search_params.get('job_title', 'N/A')}** in **{search_params.get('location', 'All locations')}**")
        
        jobs_per_page = 5
        total_pages = (len(jobs) - 1) // jobs_per_page + 1
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        if total_pages > 1:
            col_prev, col_info, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("⬅️ Previous", disabled=st.session_state.current_page == 1):
                    st.session_state.current_page -= 1
                    st.rerun()
            with col_info:
                st.write(f"Page {st.session_state.current_page} of {total_pages}")
            with col_next:
                if st.button("➡️ Next", disabled=st.session_state.current_page == total_pages):
                    st.session_state.current_page += 1
                    st.rerun()
        
        start_idx = (st.session_state.current_page - 1) * jobs_per_page
        end_idx = start_idx + jobs_per_page
        current_jobs = jobs[start_idx:end_idx]
        
        for i, job in enumerate(current_jobs):
            with st.container():
                col_title, col_company, col_match = st.columns([3, 2, 1])
                
                with col_title:
                    st.markdown(f"### 💼 {job.get('title', 'Job Title')}")
                    if job.get('location'):
                        st.write(f"📍 {job.get('location')}")
                
                with col_company:
                    st.markdown(f"**🏢 {job.get('company', 'Company')}**")
                    if job.get('posted_date'):
                        st.write(f"📅 {job.get('posted_date')}")
                
                with col_match:
                    try:
                        match_score = job.get('ai_match_score', job.get('match_score', 75))
                        if isinstance(match_score, str):
                            match_score = int(match_score.replace('%', ''))
                        st.metric("🎯 AI Match", f"{match_score}%")
                    except:
                        st.metric("🎯 AI Match", "Good")
                
                col_details, col_actions = st.columns([2, 1])
                
                with col_details:
                    salary_display = format_salary_in_inr(job.get('salary_range', job.get('salary', 'Competitive')))
                    st.write(f"💰 **Salary:** {salary_display}")
                    
                    emp_type = job.get('employment_type', 'Full-time')
                    remote_info = " (Remote)" if job.get('remote_type') else ""
                    st.write(f"⏰ **Type:** {emp_type}{remote_info}")
                    
                    if job.get('skills'):
                        skills_text = ", ".join(job.get('skills', [])[:5])
                        st.write(f"🛠️ **Skills:** {skills_text}")
                    
                    description = job.get('description', '')
                    if description:
                        preview = description[:200] + "..." if len(description) > 200 else description
                        st.write(f"📝 {preview}")
                
                with col_actions:
                    if job.get('application_url'):
                        st.link_button(
                            "🚀 Apply Now",
                            job['application_url'],
                            use_container_width=True
                        )
                    elif job.get('linkedin_url'):
                        st.link_button(
                            "💼 View on LinkedIn",
                            job['linkedin_url'],
                            use_container_width=True
                        )
                with st.expander(f"📊 View Full Details"):
                    render_detailed_job_view(job, start_idx + i)
                
                st.divider()
        
        if st.button("🔄 Reset Search"):
            if 'search_results' in st.session_state:
                del st.session_state.search_results
            if 'search_params' in st.session_state:
                del st.session_state.search_params
            if 'current_page' in st.session_state:
                del st.session_state.current_page
            st.rerun()
    
    if st.session_state.get('saved_jobs'):
        st.markdown("---")
        st.subheader(f"💾 Saved Jobs ({len(st.session_state.saved_jobs)})")
        
        with st.expander("View Saved Jobs"):
            for i, saved_job in enumerate(st.session_state.saved_jobs):
                col_job, col_remove = st.columns([4, 1])
                with col_job:
                    st.write(f"💼 **{saved_job.get('title')}** at **{saved_job.get('company')}**")
                    st.write(f"📍 {saved_job.get('location', 'N/A')}")
                with col_remove:
                    if st.button("🗑️", key=f"remove_saved_{i}", help="Remove saved job"):
                        st.session_state.saved_jobs.pop(i)
                        st.rerun()
    
    else:
        st.info("🔍 Use the search filters above to find relevant job opportunities!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def interview_page(interview_sim):
    st.header("🎤 AI Interview Simulator")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    if not hasattr(st.session_state, 'interview_ui'):
        st.session_state.interview_ui = InterviewUI(interview_sim)
    
    interview_ui = st.session_state.interview_ui
    
    if not st.session_state.get('interview_active', False):
        interview_ui.render_interview_setup()
    
    elif st.session_state.get('interview_active') and not st.session_state.get('interview_completed', False):
        interview_ui.render_active_interview()
    
    elif st.session_state.get('interview_completed', False):
        interview_ui.render_interview_results()
    
    st.markdown('</div>', unsafe_allow_html=True)

def resume_chat_page(groq_service):
    st.header("💬 Chat with Resume AI")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    st.markdown("### 🤖 Your Personal Resume Assistant")
    st.info("Ask me anything about your resume, career advice, job market trends, or get personalized recommendations!")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'resume_context' not in st.session_state:
        user_data = st.session_state.user_data
        context = f"""
        User Profile:
        Name: {user_data.get('name', 'N/A')}
        Title: {user_data.get('title', 'N/A')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'N/A')}
        Education: {user_data.get('education', 'N/A')}
        
        Resume Projects: {len(user_data.get('projects', []))} projects available
        """
        st.session_state.resume_context = context
    
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
    
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Analyze My Resume", use_container_width=True):
            question = "Please analyze my resume and provide feedback on strengths and areas for improvement."
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("🤖 Analyzing your resume..."):
                response = groq_service.chat_with_resume(question, st.session_state.resume_context)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("💡 Career Advice", use_container_width=True):
            question = "Based on my background, what career advice and next steps would you recommend?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("🤖 Generating career advice..."):
                response = groq_service.chat_with_resume(question, st.session_state.resume_context)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("🎯 Job Matching", use_container_width=True):
            question = "What types of jobs and roles would be the best fit for my skills and experience?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("🤖 Finding job matches..."):
                response = groq_service.chat_with_resume(question, st.session_state.resume_context)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col4:
        if st.button("📈 Skill Gaps", use_container_width=True):
            question = "What skills should I learn or improve to advance in my career and become more competitive?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("🤖 Analyzing skill gaps..."):
                response = groq_service.chat_with_resume(question, st.session_state.resume_context)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    st.markdown("### 💬 Ask Me Anything")
    user_question = st.text_area(
        "Type your question about your resume, career, or job search:",
        placeholder="Example questions:\n- How can I improve my resume?\n- What salary should I expect for my experience?\n- How do I transition to a new field?\n- What are the latest trends in my industry?",
        height=100,
        key="chat_input"
    )
    
    col_send, col_clear = st.columns([3, 1])
    
    with col_send:
        if st.button("💬 Send Message", type="primary", use_container_width=True):
            if user_question.strip():
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                
                with st.spinner("🤖 AI is thinking..."):
                    try:
                        response = groq_service.chat_with_resume(user_question, st.session_state.resume_context)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error getting response: {str(e)}")
            else:
                st.error("⚠️ Please enter a question.")
    
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 📥 Export Chat")
        
        chat_text = "Resume Chat Session\n" + "="*50 + "\n\n"
        for message in st.session_state.chat_history:
            role = "You" if message['role'] == 'user' else "AI Assistant"
            chat_text += f"{role}: {message['content']}\n\n"
        
        chat_text += f"\nGenerated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        
        st.download_button(
            label="📥 Download Chat History",
            data=chat_text,
            file_name=f"resume_chat_{int(time.time())}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

if page == "📤 Data Input":
    data_input_page(data_extractor)
elif page == "🌐 Portfolio Generator":
    portfolio_page(groq_service, portfolio_gen)
elif page == "📄 Resume Generator":
    resume_page(groq_service, resume_gen)
elif page == "✉️ Cover Letter Generator":
    cover_letter_page(groq_service, cover_letter_gen)
elif page == "🔍 Job Search":
    job_search_page(job_searcher, groq_service)
elif page == "🎤 Interview Simulator":
    interview_page(interview_sim)
elif page == "💬 Chat with Resume":
    resume_chat_page(groq_service)
