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

# Try to set Tesseract path, but don't fail if it doesn't exist
try:
    if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    else:
        print("Warning: Tesseract not found at default location. OCR functionality may be limited.")
except Exception as e:
    print(f"Warning: Could not set Tesseract path: {e}")

st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def clear_session_data():
    if hasattr(st.session_state, 'user_data'):
        st.session_state.user_data = {}
    if hasattr(st.session_state, 'qa_completed'):
        st.session_state.qa_completed = False
    if hasattr(st.session_state, 'verification_completed'):
        st.session_state.verification_completed = False
    if hasattr(st.session_state, 'interview_active'):
        st.session_state.interview_active = False
    if hasattr(st.session_state, 'interview_messages'):
        st.session_state.interview_messages = []

def initialize_services():
    try:
        if not GROQ_API_KEY:
            st.error("Please set GROQ_API_KEY in your .env file")
            return None, None, None, None, None, None, None
        
        groq_service = GroqLLM(GROQ_API_KEY)
        data_extractor = DataExtractor()
        portfolio_gen = PortfolioGenerator()
        resume_gen = ResumeGenerator()
        cover_letter_gen = CoverLetterGenerator()
        job_searcher = JobSearcher()
        interview_sim = InterviewSimulator(groq_service)
        
        return groq_service, data_extractor, portfolio_gen, resume_gen, cover_letter_gen, job_searcher, interview_sim
    except Exception as e:
        st.error(f"Error initializing services: {str(e)}")
        return None, None, None, None, None, None, None

def convert_usd_to_inr(usd_amount: float, exchange_rate: float = 83.0) -> float:
    return usd_amount * exchange_rate

def format_salary_with_inr(salary_str: str) -> str:
    if not salary_str or salary_str == "Not specified":
        return salary_str
    
    import re
    numbers = re.findall(r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', salary_str)
    
    if numbers:
        try:
            usd_amount = float(numbers[0].replace(',', ''))
            inr_amount = convert_usd_to_inr(usd_amount)
            
            if len(numbers) > 1:
                usd_amount2 = float(numbers[1].replace(',', ''))
                inr_amount2 = convert_usd_to_inr(usd_amount2)
                return f"${usd_amount:,.0f} - ${usd_amount2:,.0f} (₹{inr_amount:,.0f} - ₹{inr_amount2:,.0f})"
            else:
                return f"${usd_amount:,.0f} (₹{inr_amount:,.0f})"
        except (ValueError, IndexError):
            return salary_str
    
    return salary_str

def main():
    if "session_id" not in st.session_state:
        st.session_state.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        atexit.register(clear_session_data)
    
    if "resume_content" not in st.session_state:
        st.session_state.resume_content = None
    if "resume_generated_data" not in st.session_state:
        st.session_state.resume_generated_data = {}
    if "cover_letter_content" not in st.session_state:
        st.session_state.cover_letter_content = None
    if "cover_letter_generated_data" not in st.session_state:
        st.session_state.cover_letter_generated_data = {}
    if "portfolio_content" not in st.session_state:
        st.session_state.portfolio_content = None
    if "portfolio_generated_data" not in st.session_state:
        st.session_state.portfolio_generated_data = {}
    
    st.markdown("""
    <script>
    window.addEventListener('beforeunload', function (e) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to leave? All your generated content and profile data will be lost.';
        return 'Are you sure you want to leave? All your generated content and profile data will be lost.';    });    </script>
    """, unsafe_allow_html=True)
    
    st.title("🚀 AI Career Assistant")
    st.markdown("Transform your career with AI-powered tools for portfolios, resumes, and interview prep!")
    
    # Debug: Show that we're initializing services
    with st.spinner("Initializing AI services..."):
        services = initialize_services()
    
    if services[0] is None: 
        st.error("Failed to initialize services. Please check your configuration.")
        return
    
    groq_service, data_extractor, portfolio_gen, resume_gen, cover_letter_gen, job_searcher, interview_sim = services
    st.success("✅ Services initialized successfully!")
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a feature:", [
        "📤 Data Input",
        "🌐 Portfolio Generator", 
        "📄 Resume Generator",
        "✉️ Cover Letter Generator",
        "🔍 Job Search",
        "🎤 Interview Simulator"
    ])
    
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    
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

def data_input_page(data_extractor):
    st.header("📤 Data Input")
    st.markdown("Upload your resume to automatically extract and edit your profile information.")
    
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = {}
    if "verification_completed" not in st.session_state:
        st.session_state.verification_completed = False
    
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
            'Verification': 'Resume Upload ✅'        }
        
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
        
        # Resume Chat Section
        st.subheader("💬 Chat About Your Resume")
        st.markdown("Get AI-powered insights, suggestions, and answers about your resume!")
        
        # Initialize chat history if not exists
        if "resume_chat_history" not in st.session_state:
            st.session_state.resume_chat_history = []
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for i, message in enumerate(st.session_state.resume_chat_history):
                if message["role"] == "user":
                    st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right;">
                        <strong>You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #f1f8e9; padding: 10px; border-radius: 10px; margin: 5px 0;">
                        <strong>AI Career Coach:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        col_chat, col_send = st.columns([4, 1])
        with col_chat:
            user_question = st.text_input(
                "Ask me anything about your resume:",
                placeholder="e.g., How can I improve my skills section? What keywords should I add?",
                key="resume_chat_input"
            )
        with col_send:
            send_message = st.button("Send 📤", key="send_resume_chat")
        
        # Quick question buttons
        st.markdown("**Quick Questions:**")
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            if st.button("💡 Improvement Tips", key="improve_tips"):
                user_question = "What are the top 3 ways I can improve my resume?"
                send_message = True
        with col_q2:
            if st.button("🎯 ATS Optimization", key="ats_tips"):
                user_question = "How can I optimize my resume for ATS systems?"
                send_message = True
        with col_q3:
            if st.button("📈 Career Advice", key="career_advice"):
                user_question = "What career opportunities align with my skills and experience?"
                send_message = True
        
        # Process chat message
        if (send_message or user_question) and user_question.strip():
            with st.spinner("🤖 AI is analyzing your resume and preparing a response..."):
                try:
                    # Get the groq service
                    groq_service = initialize_services()[0]
                    
                    if groq_service:
                        # Get resume content from extracted data
                        resume_content = ""
                        if 'cv_text' in st.session_state.user_data:
                            resume_content = st.session_state.user_data['cv_text']
                        else:
                            # Build resume content from extracted data
                            resume_content = f"""
                            Name: {st.session_state.user_data.get('name', '')}
                            Email: {st.session_state.user_data.get('email', '')}
                            Phone: {st.session_state.user_data.get('phone', '')}
                            Title: {st.session_state.user_data.get('title', '')}
                            
                            Education:
                            {st.session_state.user_data.get('education', '')}
                            
                            Skills:
                            {', '.join(st.session_state.user_data.get('skills', []))}
                            
                            Experience:
                            {st.session_state.user_data.get('experience', '')}
                            """
                        
                        # Get AI response
                        ai_response = groq_service.chat_about_resume(
                            resume_content=resume_content,
                            user_message=user_question,
                            chat_history=st.session_state.resume_chat_history
                        )
                        
                        # Add to chat history
                        st.session_state.resume_chat_history.append({
                            "role": "user",
                            "content": user_question
                        })
                        st.session_state.resume_chat_history.append({
                            "role": "assistant", 
                            "content": ai_response
                        })
                        
                        # Clear input and rerun to show new messages
                        st.rerun()
                        
                    else:
                        st.error("❌ Failed to initialize AI service")
                        
                except Exception as e:
                    st.error(f"❌ Error processing your question: {str(e)}")
        
        # Clear chat history button
        if st.session_state.resume_chat_history:
            if st.button("🗑️ Clear Chat History", key="clear_chat"):
                st.session_state.resume_chat_history = []
                st.rerun()
    
    elif not uploaded_file:
        st.subheader("✏️ Manual Information Entry")
        st.info("💡 Upload a resume above for automatic extraction, or fill in manually below:")
        
        with st.form("manual_form"):
            name = st.text_input("Full Name:")
            email = st.text_input("Email:")
            phone = st.text_input("Phone:")
            title = st.text_input("Current/Desired Job Title:")
            experience = st.text_area("Work Experience (brief):")
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
                    st.error("Please fill in at least Name, Email, and Job Title")
    
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
                with st.spinner("Extracting and verifying data..."):
                    extracted_text = data_extractor.extract_from_file(uploaded_file)
                    
                if extracted_text:
                    st.success("✅ Resume uploaded and verified successfully!")
                    st.text_area("Extracted Content", extracted_text, height=200)
                    
                    st.session_state.user_data['cv_text'] = extracted_text
                    st.session_state.user_data['verification_source'] = 'cv_upload'
                    st.session_state.verification_completed = True
                    
                    if st.button("Complete Profile"):
                        st.success("🎉 Profile completed! You can now use all features.")
                        st.rerun()
                else:
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
            "Minimalist Clean"
        ])
        
        include_projects = st.checkbox("Generate AI project examples", value=True, 
                                    help="AI will create realistic project examples based on your skills")
        
        color_scheme = st.selectbox("Color Scheme:", [            "Blue Gradient (Professional)",
            "Purple Gradient (Creative)", 
            "Green Gradient (Tech)",
            "Orange Gradient (Energy)",
            "Dark Theme (Modern)"
        ])
    
    with col2:
        st.markdown("**Your Profile:**")
        st.write(f"✅ **Name:** {st.session_state.user_data.get('name', 'N/A')}")
        st.write(f"✅ **Title:** {st.session_state.user_data.get('title', 'N/A')}")
        st.write(f"✅ **Skills:** {len(st.session_state.user_data.get('skills', []))} skills")
    
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
                'name': st.session_state.user_data.get('name', 'Professional'),
                'headline': portfolio_content.get('headline', portfolio_content.get('summary', 'Professional')),
                'about': portfolio_content.get('about', 'Professional with extensive experience'),
                'skills': [],
                'experience': [],
                'email': st.session_state.user_data.get('email', 'contact@example.com'),
                'phone': st.session_state.user_data.get('phone', 'Phone Number'),
                'linkedin': st.session_state.user_data.get('linkedin', 'linkedin.com/in/professional'),
                'portfolio_style': settings.get('portfolio_style', 'Modern Professional'),
                'color_scheme': settings.get('color_scheme', 'Blue Gradient (Professional)')
            }
            
            if 'skills_categories' in portfolio_content:
                all_skills = []
                for category, skills in portfolio_content['skills_categories'].items():
                    if isinstance(skills, list):
                        all_skills.extend(skills)
                template_data['skills'] = all_skills
            else:
                template_data['skills'] = st.session_state.user_data.get('skills', [])
            
            if 'projects' in portfolio_content and portfolio_content['projects']:
                template_data['experience'] = [
                    {
                        'title': project.get('name', 'Project'),
                        'company': 'Personal/Professional Project',
                        'duration': 'Recent',
                        'description': project.get('description', 'Professional project')
                    }
                    for project in portfolio_content['projects']
                ]
            else:
                template_data['experience'] = [{
                    'title': st.session_state.user_data.get('title', 'Professional'),
                    'company': 'Professional Experience',
                    'duration': 'Current',
                    'description': st.session_state.user_data.get('experience', 'Professional experience in the field')
                }]
            st.session_state.portfolio_template_data = template_data
            html_content = portfolio_gen.generate_html(template_data)
            st.session_state.portfolio_html = html_content
            
            st.subheader("🌟 Portfolio Preview")
            st.components.v1.html(html_content, height=600, scrolling=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download HTML",
                    data=html_content,
                    file_name=f"portfolio_{template_data.get('name', 'portfolio').replace(' ', '_').lower()}.html",
                    mime="text/html",
                    use_container_width=True
                )
            with col2:
                if st.button("🎨 Customize Style", use_container_width=True):
                    st.session_state.generated_portfolio = None
                    st.session_state.portfolio_html = None
                    st.session_state.portfolio_template_data = None
                    st.rerun()
            
            st.subheader("🌐 AI-Powered Deployment Options")
            hosting_option = st.selectbox("Choose hosting platform:", [
                "GitHub Pages (Recommended)",
                "Netlify (Easy Deploy)", 
                "Vercel (Developer Friendly)",
                "Custom Domain Setup"
            ])
            
            deployment_urls = {
                "GitHub Pages (Recommended)": "https://pages.github.com/",
                "Netlify (Easy Deploy)": "https://www.netlify.com/",
                "Vercel (Developer Friendly)": "https://vercel.com/",
                "Custom Domain Setup": "https://domains.google.com/"
            }
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🚀 Get AI Deployment Guide", use_container_width=True):
                    deployment_tips = groq_service.generate_deployment_guide(hosting_option, st.session_state.user_data)
                    st.markdown("### 📖 AI-Generated Deployment Guide")
                    st.markdown(deployment_tips)
                    
                    quick_start = groq_service.get_deployment_quick_start(hosting_option)
                    st.markdown("### ⚡ Quick Start Guide")
                    st.markdown(quick_start["steps"])
                    st.info(quick_start["tip"])
                    st.success(f"✅ Ready to deploy to {hosting_option}!")
            
            with col2:
                deployment_url = deployment_urls.get(hosting_option, "https://github.com/")
                
                if st.button(f"🌐 Go to {hosting_option.split(' ')[0]} & Download HTML", use_container_width=True, type="primary"):
                    if 'portfolio_html' in st.session_state:
                        st.download_button(
                            label="💾 Your Portfolio HTML",
                            data=st.session_state.portfolio_html,
                            file_name=f"{st.session_state.user_data.get('name', 'portfolio').lower().replace(' ', '_')}_portfolio.html",
                            mime="text/html",
                            use_container_width=True
                        )
                        st.markdown(f"""
                        <script>
                            window.open('{deployment_url}', '_blank');
                        </script>
                        """, unsafe_allow_html=True)
                        st.success(f"🚀 HTML downloaded! Opening {hosting_option.split(' ')[0]}...")
                    else:
                        st.error("⚠️ Please generate your portfolio first!")
                
                if "GitHub" in hosting_option:
                    st.info("💡 **Tip:** Create a new repository and upload your HTML file to get started!")
                elif "Netlify" in hosting_option:
                    st.info("💡 **Tip:** Drag and drop your HTML file directly to deploy instantly!")
                elif "Vercel" in hosting_option:
                    st.info("💡 **Tip:** Connect your GitHub repository for automatic deployments!")
                else:
                    st.info("💡 **Tip:** Purchase a custom domain and point it to your hosting service!")
            
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
    
    st.markdown("### 🤖 AI-Powered ATS-Optimized Resume")
    st.info("Our AI will create a professionally tailored resume optimized for Applicant Tracking Systems (ATS).")
    
    user_skills = st.text_area(
        "💼 Enter Your Skills and Experience:",
        height=150,
        placeholder="Enter your technical skills, soft skills, certifications, and key experiences here. Separate with commas or line breaks.\n\nExample:\nPython, JavaScript, React, Node.js\nProject Management, Team Leadership\nAWS, Docker, Kubernetes\n5 years software development experience",
        help="List all your relevant skills, technologies, certifications, and experience. The AI will use this to generate your resume."
    )
    
    # Projects Management Section
    st.markdown("### 🚀 Project Management")
    st.info("Add your projects to enhance your resume. AI will format them using the STAR method (Situation, Task, Action, Result).")
    
    # Initialize projects in session state
    if 'resume_projects' not in st.session_state:
        st.session_state.resume_projects = []
    
    # Project input form
    with st.expander("➕ Add New Project", expanded=False):
        with st.form("project_form"):
            project_title = st.text_input("🏗️ Project Title:", placeholder="e.g., E-commerce Website Development")
            project_description = st.text_area(
                "📝 Project Description:", 
                height=100,
                placeholder="Describe your project, your role, challenges faced, and outcomes achieved...\n\nExample:\nDeveloped a full-stack e-commerce website for a local business. Led a team of 3 developers, implemented secure payment processing, and deployed using AWS. Resulted in 40% increase in online sales."
            )
            
            col_tech, col_duration = st.columns(2)
            with col_tech:
                technologies = st.text_input("🛠️ Technologies Used:", placeholder="React, Node.js, MongoDB, AWS")
            with col_duration:
                duration = st.text_input("⏱️ Duration:", placeholder="3 months, Jan-Mar 2024")
            
            submit_project = st.form_submit_button("➕ Add Project", type="primary")
            
            if submit_project and project_title and project_description:
                new_project = {
                    'title': project_title,
                    'description': project_description,
                    'technologies': technologies,
                    'duration': duration
                }
                st.session_state.resume_projects.append(new_project)
                st.success(f"✅ Project '{project_title}' added successfully!")
                st.rerun()
    
    # Display existing projects
    if st.session_state.resume_projects:
        st.markdown("**📋 Your Projects:**")
        for i, project in enumerate(st.session_state.resume_projects):
            with st.container():
                col_project, col_remove = st.columns([4, 1])
                with col_project:
                    st.markdown(f"**{project['title']}**")
                    st.write(f"📝 {project['description'][:100]}...")
                    if project['technologies']:
                        st.write(f"🛠️ Technologies: {project['technologies']}")
                    if project['duration']:
                        st.write(f"⏱️ Duration: {project['duration']}")
                with col_remove:
                    if st.button("🗑️", key=f"remove_project_{i}", help="Remove project"):
                        st.session_state.resume_projects.pop(i)
                        st.rerun()
                st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        job_description = st.text_area(
            "🎯 Target Job Description (Optional - for AI tailoring):",
            height=120,
            placeholder="Paste the job description here for AI to tailor your resume specifically for this role...",
            help="AI will analyze the job requirements and optimize your resume accordingly"
        )
        
        resume_style = st.selectbox("Resume Format:", [
            "Professional ATS-Optimized",
            "Creative Professional",
            "Executive Leadership",
            "Technical Specialist",
            "Entry Level Focus"        ])
    
    with col2:
        st.markdown("**Profile Summary:**")
        st.write(f"👤 **Name:** {st.session_state.user_data.get('name', 'N/A')}")
        st.write(f"💼 **Title:** {st.session_state.user_data.get('title', 'N/A')}")
        st.write(f"📧 **Email:** {st.session_state.user_data.get('email', 'N/A')}")
        
        if user_skills:
            skills_count = len([skill.strip() for skill in user_skills.replace('\n', ',').split(',') if skill.strip()])
            st.write(f"🛠️ **Skills Entered:** {skills_count}")
          # Display project count
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
    
    if st.button("🚀 Generate AI Resume", type="primary", use_container_width=True):
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
                    'enhanced_data': enhanced_data,
                    'projects': st.session_state.resume_projects
                }
                st.success("✅ AI Resume generated successfully!")
    
    if st.session_state.resume_content:
        resume_content = st.session_state.resume_content
        generated_data = st.session_state.resume_generated_data
        
        st.subheader("📋 Resume Content")
        st.markdown(resume_content)
        
        pdf_bytes = resume_gen.generate_pdf(resume_content, st.session_state.user_data)
        st.download_button(
            label="📥 Save PDF",
            data=pdf_bytes,
            file_name=f"resume_{st.session_state.user_data.get('name', 'resume').replace(' ', '_').lower()}.pdf",
            mime="application/pdf",
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

def cover_letter_page(groq_service, cover_letter_gen):
    st.header("✉️ AI Cover Letter Generator")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        return
    
    st.markdown("### 🤖 AI-Powered Personalized Cover Letters")
    st.info("Our AI will create compelling, personalized cover letters that get interviews!")
    
    user_skills_experience = st.text_area(
        "💼 Enter Your Skills and Experience:",
        height=120,
        placeholder="Enter your relevant skills, experience, and achievements for this position.\n\nExample:\nPython, JavaScript, React development\nTeam leadership and project management\n3 years experience in full-stack development\nLed team of 5 developers on e-commerce project",        help="Describe your key skills, experience, and achievements relevant to the position you're applying for."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("🏢 Company Name:", placeholder="e.g., Google, Microsoft, Apple")
        position = st.text_input("💼 Position Title:", placeholder="e.g., Software Engineer, Marketing Manager")
        
    with col2:
        tone = st.selectbox("Writing Tone:", [
            "Professional & Confident",
            "Enthusiastic & Energetic", 
            "Formal & Conservative",
            "Creative & Personal",
            "Technical & Precise"
        ])
        
        length = st.selectbox("Letter Length:", [
            "Concise (200-250 words)",
            "Standard (300-400 words)",
            "Detailed (450-500 words)"
        ])
        
    job_description = st.text_area(
        "📋 Job Description:", 
        height=120,
        placeholder="Paste the complete job description here for AI to analyze requirements and tailor your letter..."
    )
    
    company_research = st.text_area(
        "🔍 Company Research (Optional):",
        height=80,
        placeholder="Share what you know about the company, recent news, values, etc. AI will incorporate this for personalization."
    )
    
    if st.button("🚀 Generate AI Cover Letter", type="primary", use_container_width=True):
        if not company_name or not position or not user_skills_experience:
            st.error("⚠️ Please fill in Company Name, Position Title, and your Skills/Experience to generate a cover letter.")
            return
            
        with st.spinner("🤖 AI is crafting your personalized cover letter..."):
            enhanced_data = st.session_state.user_data.copy()
            enhanced_data.update({
                'company_name': company_name,
                'position': position,
                'tone': tone,
                'length': length,
                'company_research': company_research,                'skills_experience_input': user_skills_experience
            })
            
            skills_list = []
            for line in user_skills_experience.split('\n'):
                for skill in line.split(','):
                    skill = skill.strip()
                    if skill:
                        skills_list.append(skill)
            enhanced_data['skills'] = skills_list
            
            cover_letter = groq_service.generate_enhanced_cover_letter(
                enhanced_data, 
                job_description,
                company_name,
                position
            )
            
            if cover_letter:
                st.session_state.cover_letter_content = cover_letter
                st.session_state.cover_letter_generated_data = {
                    'company_name': company_name,
                    'position': position,
                    'user_skills_experience': user_skills_experience,
                    'job_description': job_description,
                    'company_research': company_research,
                    'tone': tone,
                    'length': length,
                    'enhanced_data': enhanced_data
                }
                st.success("✅ AI Cover letter generated successfully!")
    
    if st.session_state.cover_letter_content:
        cover_letter = st.session_state.cover_letter_content
        generated_data = st.session_state.cover_letter_generated_data
        
        st.subheader("📝 Your Personalized Cover Letter")
        st.markdown(cover_letter)
        
        pdf_bytes = cover_letter_gen.generate_pdf(cover_letter, generated_data['enhanced_data'], generated_data['company_name'])
        st.download_button(
            label="📥 Save as PDF",
            data=pdf_bytes,
            file_name=f"cover_letter_{generated_data['company_name'].lower().replace(' ', '_')}_{generated_data['position'].lower().replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        # Add clear content button
        if st.button("🗑️ Clear Generated Cover Letter"):
            st.session_state.cover_letter_content = None
            st.session_state.cover_letter_generated_data = {}
            st.rerun()
    else:
        if not st.session_state.cover_letter_content:
            st.info("🚀 Fill in the fields above and click 'Generate AI Cover Letter' to create your personalized cover letter!")

def job_search_page(job_searcher, groq_service):
    st.header("🔍 Job Search")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        return
    
    google_jobs_status = job_searcher.validate_google_jobs_access()
    if google_jobs_status:
        st.success("🟢 Google Cloud Talent Solution API Connected - Enhanced job search available!")
    else:
        st.warning("🟡 Google Jobs API not configured - Using enhanced fallback search")
        with st.expander("🔧 Configure Google Cloud Talent Solution API (Optional)"):
            st.markdown("""
            **To enable Google Cloud Talent Solution API integration:**
            1. Create a Google Cloud Project and enable the Cloud Talent Solution API
            2. Create a service account and download the JSON key file
            3. Add this environment variable to your .env file:
                - `JOBS_API_KEY=your_google_cloud_api_key`
            4. Restart the application
            
            **Note:** The app works great without the API using our enhanced search with realistic job data!
            """)
    
    st.markdown("### 🔍 Job Search")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("job_search_form"):
            keywords = st.text_input("🔍 Job Keywords/Title:", placeholder="e.g., Software Engineer, Data Scientist")
            location = st.text_input("📍 Location:", placeholder="e.g., New York, Remote, San Francisco")
            
            col_a, col_b = st.columns(2)
            with col_a:
                experience_level = st.selectbox("Experience Level:", [
                    "", 
                    "Entry Level (0-2 years)", 
                    "Mid Level (3-5 years)", 
                    "Senior Level (6-10 years)", 
                    "Executive (10+ years)"
                ])
                
                company_size = st.selectbox("Company Size:", [
                    "",
                    "Startup (1-50)",
                    "Small (51-200)", 
                    "Medium (201-1000)",
                    "Large (1001-5000)",
                    "Enterprise (5000+)"
                ])
            
            with col_b:
                salary_range = st.selectbox("Expected Salary Range:", [
                    "Not specified",
                    "$40k - $60k",
                    "$60k - $80k", 
                    "$80k - $120k",
                    "$120k - $180k",
                    "$180k - $250k",
                    "$250k+"
                ])
                
                remote_work = st.checkbox("Include Remote Jobs", value=True)
            
            submitted = st.form_submit_button("🚀 Search Jobs", type="primary")
    
    with col2:
        if st.session_state.get("user_data"):
            st.markdown("**👤 Profile Summary:**")
            st.write(f"**Name:** {st.session_state.user_data.get('name', 'N/A')}")
            st.write(f"**Title:** {st.session_state.user_data.get('title', 'N/A')}")
            st.write(f"**Skills:** {len(st.session_state.user_data.get('skills', []))}")
            
            if keywords:
                with st.spinner("Getting salary insights..."):
                    salary_data = job_searcher.get_salary_insights(keywords, location)
                    if salary_data:
                        st.markdown("**💰 Salary Insights:**")
                        median_usd = salary_data.get('median_salary', 0)
                        min_usd = salary_data.get('min_salary', 0)
                        max_usd = salary_data.get('max_salary', 0)
                        
                        if median_usd > 0:
                            median_inr = convert_usd_to_inr(median_usd)
                            st.write(f"**Median:** ${median_usd:,} (₹{median_inr:,.0f})")
                        
                        if min_usd > 0 and max_usd > 0:
                            min_inr = convert_usd_to_inr(min_usd)
                            max_inr = convert_usd_to_inr(max_usd)
                            st.write(f"**Range:** ${min_usd:,} - ${max_usd:,} (₹{min_inr:,.0f} - ₹{max_inr:,.0f})")
    
    if submitted and keywords:
        with st.spinner("🔍 Searching for jobs..."):
            jobs = job_searcher.search_jobs(
                keywords=keywords, 
                location=location, 
                experience_level=experience_level,
                company_size=company_size,
                remote=remote_work,
                limit=25
            )
            
            if st.session_state.get("user_data") and jobs:
                enhanced_jobs = groq_service.analyze_job_matches(jobs, st.session_state.user_data)
                jobs = enhanced_jobs
            
        if jobs:
            st.success(f"🎉 Found {len(jobs)} job opportunities!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                sort_by = st.selectbox("Sort by:", ["Relevance", "Date Posted", "Company", "Match Score"])
            with col2:
                company_filter = st.multiselect("Filter by Company:", 
                                                options=list(set([job.get('company', '') for job in jobs])))
            with col3:
                show_only_remote = st.checkbox("Show only remote jobs")
            
            filtered_jobs = jobs
            if company_filter:
                filtered_jobs = [job for job in jobs if job.get('company') in company_filter]
            if show_only_remote:
                filtered_jobs = [job for job in jobs if job.get('remote_type')]
            
            for i, job in enumerate(filtered_jobs):
                match_score = job.get('ai_analysis', {}).get('match_score', job.get('ai_match_score', 'N/A'))
                source_icon = "🔗" if job.get('source') == 'google_jobs_api' else "🤖"
                
                with st.expander(f"{source_icon} {job.get('title', 'Job Title')} at {job.get('company', 'Company')} - Match: {match_score}%"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"📍 **Location:** {job.get('location', 'N/A')}")
                        salary_display = format_salary_with_inr(job.get('salary_range', 'Not specified'))
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
                            st.info(f"Match Level: {analysis.get('match_level', 'N/A')} | Keywords: {', '.join(analysis.get('matched_keywords', [])[:3])}")
                    
                    with col2:
                        # Action buttons
                        if job.get('linkedin_url'):
                            st.link_button("🔗 View on LinkedIn", job['linkedin_url'], use_container_width=True)
                        
                        if job.get('application_url'):
                            st.link_button("🚀 Apply Now", job['application_url'], use_container_width=True)
                            
                        if st.button(f"📝 Generate Cover Letter", key=f"cover_{i}"):
                            st.info("📝 Navigate to Cover Letter Generator to create a tailored letter for this role!")
                        
                        if st.button(f"💾 Save Job", key=f"save_{i}"):
                            if 'saved_jobs' not in st.session_state:
                                st.session_state.saved_jobs = []
                            st.session_state.saved_jobs.append(job)
                            st.success("Job saved!")
        else:
            st.info("🔍 No jobs found. Try different keywords or broader search terms.")
    
    if st.session_state.get('saved_jobs'):
        st.markdown("### 💾 Your Saved Jobs")
        for i, job in enumerate(st.session_state.saved_jobs):
            with st.expander(f"{job.get('title')} at {job.get('company')}"):
                st.write(f"📍 **Location:** {job.get('location')}")
                saved_salary_display = format_salary_with_inr(job.get('salary_range', 'Not specified'))
                st.write(f"💰 **Salary:** {saved_salary_display}")
                st.write(f"📅 **Saved on:** {job.get('saved_date', 'Recently')}")
                
                if st.button(f"Remove", key=f"remove_{i}"):
                    st.session_state.saved_jobs.pop(i)
                    st.rerun()

def interview_page(interview_sim):
    st.header("🎤 AI Interview Simulator")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        return
    
    st.markdown("### 🤖 Chat-Based Interview Practice")
    st.info("Practice with our AI interviewer in a conversational format. Answer 5 questions and get detailed analysis!")
    
    if 'chat_interview_active' not in st.session_state:
        st.session_state.chat_interview_active = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'interview_question_count' not in st.session_state:
        st.session_state.interview_question_count = 0
    if 'interview_job_info' not in st.session_state:
        st.session_state.interview_job_info = {}
    if 'interview_complete' not in st.session_state:
        st.session_state.interview_complete = False
    
    if not st.session_state.chat_interview_active and not st.session_state.interview_complete:
        render_chat_interview_setup(interview_sim)
    elif st.session_state.chat_interview_active and not st.session_state.interview_complete:
        render_chat_interview(interview_sim)
    elif st.session_state.interview_complete:
        render_chat_interview_results(interview_sim)

def render_interview_setup(interview_sim):
    st.subheader("🎯 Interview Setup")
    st.markdown("Configure your AI interview session:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        job_title = st.text_input("🎯 Job Title", 
                                placeholder="e.g., Software Engineer, Data Scientist", 
                                help="The position you're interviewing for")
        company = st.text_input("🏢 Company Name", 
                                placeholder="e.g., Google, Microsoft, Amazon",
                                help="Target company (optional)")
        
    with col2:
        experience_level = st.selectbox("📊 Experience Level", [
            "Entry Level (0-2 years)",
            "Mid Level (3-5 years)", 
            "Senior Level (6-10 years)",
            "Executive (10+ years)"
        ])
        
        interview_type = st.selectbox("🎭 Interview Type", [
            "General/Behavioral",
            "Technical/Skills-based",
            "Case Study/Problem Solving",
            "Leadership/Management",
            "Mixed (All types)"
        ])
    
    job_description = st.text_area(
        "📋 Job Description (Optional but Recommended)",
        height=120,
        placeholder="Paste the job description here for more targeted interview questions...",
        help="AI will generate questions specifically tailored to this role"
    )
    
    st.subheader("⚙️ Interview Settings")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_questions = st.selectbox("Number of Questions", [3, 5, 8, 10], index=1)
    with col2:
        difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard", "Mixed"])
    with col3:
        time_limit = st.selectbox("Time per Question", ["No Limit", "2 minutes", "3 minutes", "5 minutes"])
    
    with st.expander("📖 What to Expect in This Interview"):
        st.markdown(f"""
        **Interview Type:** {interview_type}
        **Number of Questions:** {num_questions}
        **Difficulty:** {difficulty}
        **Time per Question:** {time_limit}
        
        **You'll receive:**
        - Real-time AI feedback on each answer
        - Scoring based on relevance, clarity, and depth
        - Suggestions for improvement
        - Final performance report with detailed analysis
        
        **Tips for Success:**
        - Speak clearly and provide specific examples
        - Use the STAR method (Situation, Task, Action, Result)
        - Take your time to think before answering
        - Be authentic and honest in your responses
        """)
    
    if st.button("🚀 Start AI Interview", type="primary", use_container_width=True):
        if not job_title.strip():
            st.error("⚠️ Please provide a job title to start the interview.")
            return
        
        if not job_description.strip():
            job_description = f"""
            {interview_type} interview for {job_title} position at {company if company else 'a leading company'}.
            Experience level: {experience_level}
            
            Key areas to assess:
            - Relevant technical and soft skills
            - Problem-solving abilities
            - Communication and teamwork
            - Cultural fit and motivation
            - Experience and achievements
            """
        
        user_background = st.session_state.get('user_data', {})
        user_background.update({
            'target_job_title': job_title,
            'target_company': company,
            'experience_level': experience_level,
            'interview_type': interview_type,
            'difficulty': difficulty,
            'num_questions': num_questions
        })
        
        with st.spinner("🤖 AI is preparing your personalized interview questions..."):
            session = interview_sim.start_interview_session(job_description, user_background)
            
            if session and session.get('questions'):
                st.session_state.interview_session = session
                st.session_state.interview_active = True
                st.session_state.interview_messages = []
                st.success("✅ Interview session created! Starting now...")
                st.rerun()
            else:
                st.error("❌ Failed to create interview session. Please try again.")

def render_active_interview(interview_sim):
    session = st.session_state.interview_session
    current_q_index = session['current_question']
    total_questions = len(session['questions'])
    current_q = interview_sim.get_current_question(session)
    
    if not current_q:
        render_interview_results(interview_sim)
        return
    
    progress = current_q_index / total_questions
    st.progress(progress, text=f"Question {current_q_index + 1} of {total_questions}")
    
    st.subheader(f"Question {current_q_index + 1}")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.write(f"**Type:** {current_q.get('type', 'General')}")
    with col2:
        st.write(f"**Difficulty:** {current_q.get('difficulty', 'Medium')}")
    with col3:
        st.write(f"**Focus:** {current_q.get('category', 'General Skills')}")
    
    st.markdown(f"### 💬 {current_q['question']}")
    
    if current_q.get('context'):
        st.info(f"💡 **Context:** {current_q['context']}")
    
    st.markdown("### ✍️ Your Answer")
    answer = st.text_area(
        "Type your response here:",
        height=200,
        placeholder="Take your time to provide a thoughtful, detailed answer. Use specific examples when possible...",
        key=f"answer_{current_q_index}",
        help="Tip: Use the STAR method (Situation, Task, Action, Result) for behavioral questions"
    )
    
    if answer:
        char_count = len(answer)
        if char_count < 50:
            st.warning(f"📝 {char_count} characters - Consider providing more detail")
        elif char_count < 200:
            st.info(f"📝 {char_count} characters - Good length, add more specifics if possible")
        else:
            st.success(f"📝 {char_count} characters - Great detailed response!")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        submit_disabled = not answer.strip() or len(answer.strip()) < 10
        if st.button("✅ Submit Answer", type="primary", disabled=submit_disabled, use_container_width=True):
            with st.spinner("🤖 AI is evaluating your answer..."):
                evaluation = interview_sim.submit_answer(session, answer)
                if evaluation:
                    st.session_state.last_evaluation = evaluation
                    st.rerun()
    
    with col2:
        if st.button("⏭️ Skip", use_container_width=True):
            interview_sim.submit_answer(session, "Question skipped by candidate")
            st.rerun()
    
    with col3:
        if st.button("🔄 Regenerate Q", use_container_width=True, help="Get a different question"):
            user_data = st.session_state.get('user_data', {})
            job_desc = session.get('job_description', '')
            groq_service = initialize_services()[0]
            if groq_service:
                new_question = groq_service.generate_interview_question(user_data, job_desc)
                if new_question:
                    session['questions'][current_q_index] = {
                        'question': new_question,
                        'type': current_q.get('type', 'General'),
                        'difficulty': current_q.get('difficulty', 'Medium'),
                        'category': current_q.get('category', 'General')
                    }
                    st.rerun()
    
    with col4:
        if st.button("🛑 End Interview", use_container_width=True):
            st.session_state.interview_active = False
            st.rerun()
    
    if hasattr(st.session_state, 'last_evaluation') and st.session_state.last_evaluation:
        render_question_feedback(st.session_state.last_evaluation)

def render_question_feedback(evaluation):
    st.divider()
    st.subheader("📊 Feedback on Previous Answer")
    
    score = evaluation.get('score', 5)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Score:** {score}/10")
    
    with col2:
        if evaluation.get('strengths'):
            st.markdown("**✅ What You Did Well:**")
            for strength in evaluation['strengths']:
                st.write(f"• {strength}")
    
    if score >= 8:
        st.success("🎉 Excellent Response!")
    elif score >= 6:
        st.info("👍 Good Answer")
    elif score >= 4:
        st.warning("⚠️ Fair Response")
    else:
        st.error("❌ Needs Improvement")
    
    if evaluation.get('feedback'):
        st.markdown("**💭 AI Interviewer Feedback:**")
        st.info(evaluation['feedback'])
    
    if evaluation.get('suggestions'):
        st.markdown("**💡 Suggestions for Next Time:**")
        st.write(evaluation['suggestions'])

def render_interview_results(interview_sim):
    session = st.session_state.interview_session
    report = interview_sim.get_final_report(session)
    
    st.balloons()
    st.subheader("🎉 Interview Complete!")
    
    score = report['overall_score']
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if score >= 8:
            st.success(f"🌟 Overall Score: {score}/10")
            st.success(f"Performance: {report['performance_level']}")
        elif score >= 6:
            st.info(f"👍 Overall Score: {score}/10")
            st.info(f"Performance: {report['performance_level']}")
        elif score >= 4:
            st.warning(f"⚠️ Overall Score: {score}/10")
            st.warning(f"Performance: {report['performance_level']}")
        else:
            st.error(f"❌ Overall Score: {score}/10")
            st.error(f"Performance: {report['performance_level']}")
    
    st.markdown(f"### 💬 {report['message']}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Questions Answered", report['questions_answered'])
    with col2:
        st.metric("Duration", f"{report['duration_minutes']} min")
    with col3:
        st.metric("Average Score", f"{score}/10")
    with col4:
        completion_rate = (report['questions_answered'] / len(session['questions'])) * 100
        st.metric("Completion Rate", f"{completion_rate:.0f}%")
    
    if st.checkbox("📊 Show Detailed Question Breakdown", value=True):
        for i, feedback in enumerate(report['detailed_feedback']):
            if i < len(session['answers']): 
                with st.expander(f"Question {i + 1} - Score: {feedback.get('score', 'N/A')}/10"):
                    question = session['questions'][i]['question']
                    answer = session['answers'][i]
                    
                    st.markdown(f"**❓ Question:** {question}")
                    st.markdown(f"**💬 Your Answer:** {answer}")
                    
                    if feedback.get('feedback'):
                        st.markdown(f"**🤖 AI Feedback:** {feedback['feedback']}")
                    
                    if feedback.get('strengths'):
                        st.markdown("**✅ Strengths:**")
                        for strength in feedback['strengths']:
                            st.write(f"• {strength}")
                    
                    if feedback.get('weaknesses'):
                        st.markdown("**📈 Improvement Areas:**")
                        for weakness in feedback['weaknesses']:
                            st.write(f"• {weakness}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Practice Again", type="primary", use_container_width=True):
            for key in ['interview_session', 'interview_active', 'last_evaluation']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("📊 Download Report", use_container_width=True):
            report_text = generate_report_text(report, session)
            st.download_button(
                label="📄 Download Detailed Report",
                data=report_text,
                file_name=f"interview_report_{int(time.time())}.txt",
                mime="text/plain"
            )
    
    with col3:
        if st.button("🎯 Practice Specific Areas", use_container_width=True):
            st.info("💡 Navigate back to the setup to practice specific interview types or difficulties!")

def generate_report_text(report, session):
    import time
    
    lines = [
        "AI INTERVIEW PERFORMANCE REPORT",
        "=" * 50,
        f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "OVERALL PERFORMANCE:",
        f"• Overall Score: {report['overall_score']}/10",
        f"• Performance Level: {report['performance_level']}", 
        f"• Questions Answered: {report['questions_answered']}",
        f"• Interview Duration: {report['duration_minutes']} minutes",
        "",
        "EXECUTIVE SUMMARY:",
        report['message'],
        "",
        "DETAILED QUESTION BREAKDOWN:",
        "-" * 40
    ]
    
    for i, feedback in enumerate(report['detailed_feedback']):
        if i < len(session['answers']):
            lines.extend([
                f"",
                f"QUESTION {i + 1}:",
                f"Q: {session['questions'][i]['question']}",
                f"A: {session['answers'][i]}",
                f"Score: {feedback.get('score', 'N/A')}/10",
                f"Feedback: {feedback.get('feedback', 'No feedback available')}",
                "-" * 40
            ])
    
    if report.get('improvement_areas'):
        lines.extend([
            "",
            "KEY IMPROVEMENT AREAS:",
            *[f"• {area}" for area in report['improvement_areas']]
        ])
    
    if report.get('strengths'):
        lines.extend([
            "",
            "DEMONSTRATED STRENGTHS:",
            *[f"• {strength}" for strength in report['strengths']]
        ])
    
    lines.extend([
        "",
        "RECOMMENDATIONS:",
        "• Continue practicing with different interview types",
        "• Focus on providing specific examples using the STAR method",
        "• Practice articulating achievements with quantifiable results",
        "• Research target companies and roles thoroughly",
        "",
        "Good luck with your interviews!"
    ])
    
    return "\n".join(lines)

def render_chat_interview_setup(interview_sim):
    """Setup for chat-based interview mode"""
    st.subheader("💬 Chat Interview Setup")
    st.markdown("Configure your conversational AI interview session:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        job_title = st.text_input("🎯 Job Title", 
                                placeholder="e.g., Software Engineer, Data Scientist", 
                                help="The position you're interviewing for",
                                key="chat_job_title")
        company = st.text_input("🏢 Company Name", 
                                placeholder="e.g., Google, Microsoft, Amazon",
                                help="Target company (optional)",
                                key="chat_company")
        
    with col2:
        experience_level = st.selectbox("📊 Experience Level", [
            "Entry Level (0-2 years)",
            "Mid Level (3-5 years)", 
            "Senior Level (6-10 years)",
            "Executive (10+ years)"
        ], key="chat_experience")
        
        interview_type = st.selectbox("🎭 Interview Type", [
            "General/Behavioral",
            "Technical",
            "System Design",
            "Case Study"
        ], key="chat_interview_type")
    
    job_description = st.text_area("📝 Job Description (Optional)", 
                                    placeholder="Paste the job description here for more targeted questions...",
                                    height=100,
                                    key="chat_job_desc")
    
    st.markdown("---")
    st.subheader("🎯 Interview Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.slider("Number of Questions", 3, 10, 5, key="chat_num_questions")
    with col2:
        difficulty = st.selectbox("Difficulty Level", 
                                ["Easy", "Medium", "Hard", "Mixed"], 
                                index=2, key="chat_difficulty")
    
    if st.button("🚀 Start Chat Interview", type="primary", use_container_width=True):
        if job_title:
            # Store interview configuration
            st.session_state.interview_job_info = {
                'job_title': job_title,
                'company': company,
                'experience_level': experience_level,
                'interview_type': interview_type,
                'job_description': job_description or f"{job_title} position at {company}. {experience_level} role.",
                'num_questions': num_questions,
                'difficulty': difficulty
            }
            
            # Initialize chat interview session
            st.session_state.chat_interview_messages = []
            st.session_state.chat_interview_active = True
            st.session_state.current_question_num = 0
            st.session_state.interview_answers = []
            st.session_state.interview_scores = []
            
            # Generate first question
            user_background = st.session_state.get('user_data', {})
            first_question = interview_sim.groq_service.generate_interview_questions(
                st.session_state.interview_job_info['job_description'], 
                user_background
            )[0]
            
            # Add welcome message and first question
            welcome_msg = f"Welcome to your {interview_type} interview for {job_title}"
            if company:
                welcome_msg += f" at {company}"
            welcome_msg += "! I'm your AI interviewer. Let's begin with your first question:"
            
            st.session_state.chat_interview_messages = [
                {"role": "assistant", "content": welcome_msg},
                {"role": "assistant", "content": first_question['question']}
            ]
            st.session_state.current_question = first_question
            
            st.rerun()
        else:
            st.error("Please provide at least a job title to start the interview.")

def render_chat_interview(interview_sim):
    """Active chat-based interview interface"""
    st.subheader("💬 Live Interview Chat")
    
    job_info = st.session_state.interview_job_info
    progress = st.session_state.current_question_num / job_info['num_questions']
    st.progress(progress, text=f"Question {st.session_state.current_question_num + 1} of {job_info['num_questions']}")
    
    # Display chat messages
    for message in st.session_state.chat_interview_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # User input for answers
    if prompt := st.chat_input("Type your answer here..."):
        # Add user message to chat
        st.session_state.chat_interview_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process the answer
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your answer..."):
                # Evaluate the answer
                evaluation = interview_sim.groq_service.evaluate_interview_answer(
                    st.session_state.current_question['question'],
                    prompt,
                    job_info['job_description']
                )
                
                # Store answer and score
                st.session_state.interview_answers.append(prompt)
                st.session_state.interview_scores.append(evaluation.get('score', 5))
                
                # Generate feedback message
                score = evaluation.get('score', 5)
                feedback_msg = f"**Score: {score}/10**\n\n"
                
                if evaluation.get('feedback'):
                    feedback_msg += f"**Feedback:** {evaluation['feedback']}\n\n"
                
                if evaluation.get('strengths'):
                    feedback_msg += "**Strengths:**\n"
                    for strength in evaluation['strengths']:
                        feedback_msg += f"• {strength}\n"
                    feedback_msg += "\n"
                
                if evaluation.get('suggestions'):
                    feedback_msg += f"**Suggestions:** {evaluation['suggestions']}\n\n"
                
                st.write(feedback_msg)
                st.session_state.chat_interview_messages.append({"role": "assistant", "content": feedback_msg})
                
                # Move to next question or end interview
                st.session_state.current_question_num += 1
                
                if st.session_state.current_question_num < job_info['num_questions']:
                    # Generate next question
                    user_background = st.session_state.get('user_data', {})
                    questions = interview_sim.groq_service.generate_interview_questions(
                        job_info['job_description'], 
                        user_background
                    )
                    
                    if st.session_state.current_question_num < len(questions):
                        next_question = questions[st.session_state.current_question_num]
                        st.session_state.current_question = next_question
                        
                        next_q_msg = f"**Question {st.session_state.current_question_num + 1}:** {next_question['question']}"
                        st.write(next_q_msg)
                        st.session_state.chat_interview_messages.append({"role": "assistant", "content": next_q_msg})
                else:
                    # Interview complete
                    completion_msg = "🎉 **Interview Complete!** Thank you for your responses. Let me prepare your results..."
                    st.write(completion_msg)
                    st.session_state.chat_interview_messages.append({"role": "assistant", "content": completion_msg})
                    st.session_state.chat_interview_active = False
                    st.session_state.interview_complete = True
                    
                    # Generate final report
                    avg_score = sum(st.session_state.interview_scores) / len(st.session_state.interview_scores)
                    st.session_state.final_interview_report = {
                        'overall_score': round(avg_score, 1),
                        'questions_answered': len(st.session_state.interview_answers),
                        'job_info': job_info,
                        'answers': st.session_state.interview_answers,
                        'scores': st.session_state.interview_scores
                    }
        
        st.rerun()
    
    # Option to end interview early
    if st.button("🛑 End Interview Early", type="secondary"):
        st.session_state.chat_interview_active = False
        st.session_state.interview_complete = True
        
        # Generate final report with current answers
        if st.session_state.interview_scores:
            avg_score = sum(st.session_state.interview_scores) / len(st.session_state.interview_scores)
            st.session_state.final_interview_report = {
                'overall_score': round(avg_score, 1),
                'questions_answered': len(st.session_state.interview_answers),
                'job_info': job_info,
                'answers': st.session_state.interview_answers,
                'scores': st.session_state.interview_scores
            }
        st.rerun()

def render_chat_interview_results(interview_sim):
    """Display chat interview results and feedback"""
    st.subheader("🎉 Interview Results")
    
    if 'final_interview_report' not in st.session_state:
        st.error("No interview results found. Please complete an interview first.")
        return
    
    report = st.session_state.final_interview_report
    job_info = report['job_info']
    
    # Display overall results
    st.balloons()
    
    score = report['overall_score']
    if score >= 8:
        st.success(f"🌟 Excellent Performance! Overall Score: {score}/10")
        performance_level = "Excellent"
    elif score >= 6:
        st.info(f"👍 Good Performance! Overall Score: {score}/10")
        performance_level = "Good"
    elif score >= 4:
        st.warning(f"📈 Fair Performance! Overall Score: {score}/10")
        performance_level = "Fair"
    else:
        st.error(f"💪 Keep Practicing! Overall Score: {score}/10")
        performance_level = "Needs Improvement"
    
    # Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Overall Score", f"{score}/10")
    
    with col2:
        st.metric("Questions Answered", report['questions_answered'])
    
    # Interview summary
    st.markdown("---")
    st.subheader("📊 Interview Summary")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Position:** {job_info['job_title']}")
        if job_info['company']:
            st.write(f"**Company:** {job_info['company']}")
        st.write(f"**Experience Level:** {job_info['experience_level']}")
    
    with col2:
        st.write(f"**Interview Type:** {job_info['interview_type']}")
        st.write(f"**Difficulty:** {job_info['difficulty']}")
        st.write(f"**Total Questions:** {job_info['num_questions']}")
    
    # Detailed feedback
    if st.checkbox("📝 Show Detailed Question-by-Question Feedback"):
        st.markdown("---")
        for i, (answer, score) in enumerate(zip(report['answers'], report['scores'])):
            with st.expander(f"Question {i + 1} - Score: {score}/10"):
                question = session['questions'][i]['question']
                answer = session['answers'][i]
                
                st.markdown(f"**❓ Question:** {question}")
                st.markdown(f"**💬 Your Answer:** {answer}")
                
                if feedback.get('feedback'):
                    st.markdown(f"**🤖 AI Feedback:** {feedback['feedback']}")
                
                if feedback.get('strengths'):
                    st.markdown("**✅ Strengths:**")
                    for strength in feedback['strengths']:
                        st.write(f"• {strength}")
                
                if feedback.get('weaknesses'):
                    st.markdown("**📈 Improvement Areas:**")
                    for weakness in feedback['weaknesses']:
                        st.write(f"• {weakness}")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Practice Again", type="primary", use_container_width=True):
            # Reset interview state
            keys_to_clear = [
                'chat_interview_active', 'interview_complete', 'chat_interview_messages',
                'current_question_num', 'interview_answers', 'interview_scores',
                'current_question', 'final_interview_report', 'interview_job_info'
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("💬 View Chat History", use_container_width=True):
            if 'chat_interview_messages' in st.session_state:
                with st.expander("Complete Interview Chat", expanded=True):
                    for msg in st.session_state.chat_interview_messages:
                        role_icon = "🤖" if msg["role"] == "assistant" else "👤"
                        st.write(f"{role_icon} **{msg['role'].title()}:** {msg['content']}")
    
    with col3:
        # Generate downloadable report
        report_text = f"""INTERVIEW PERFORMANCE REPORT
========================================
Position: {job_info['job_title']}
Company: {job_info.get('company', 'Not specified')}
Interview Type: {job_info['interview_type']}
Experience Level: {job_info['experience_level']}
Difficulty: {job_info['difficulty']}

RESULTS:
Overall Score: {score}/10
Performance Level: {performance_level}
Questions Answered: {report['questions_answered']}/{job_info['num_questions']}
Completion Rate: {completion_rate:.0f}%

DETAILED ANSWERS:
"""
        for i, (answer, score) in enumerate(zip(report['answers'], report['scores'])):
            report_text += f"\nQuestion {i + 1} (Score: {score}/10):\n{answer}\n{'-' * 40}"
        
        st.download_button(
            label="📄 Download Report",
            data=report_text,
            file_name=f"interview_report_{job_info['job_title'].replace(' ', '_').lower()}.txt",
            mime="text/plain",
            use_container_width=True
        )

if __name__ == "__main__":
    main()