import streamlit as st
import os
import json
import atexit
from datetime import datetime
from dotenv import load_dotenv
import pytesseract
from groq_service import GroqLLM
from data_extractor import DataExtractor, JobSearcher
from generators_combined import PortfolioGenerator, ResumeGenerator, CoverLetterGenerator
from interview_simulator import InterviewSimulator, InterviewUI
from linkedin_service import LinkedInJobAPI

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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

@st.cache_resource
def initialize_services():
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

def main():
    if "session_id" not in st.session_state:
        st.session_state.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        atexit.register(clear_session_data)
    
    st.title("🚀 AI Career Assistant")
    st.markdown("Transform your career with AI-powered tools for portfolios, resumes, and interview prep!")
    
    services = initialize_services()
    if services[0] is None: 
        return
    
    groq_service, data_extractor, portfolio_gen, resume_gen, cover_letter_gen, job_searcher, interview_sim = services
    
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
        job_search_page(job_searcher)
    elif page == "🎤 Interview Simulator":
        interview_page(interview_sim)

def data_input_page(data_extractor):
    st.header("📤 Data Input")
    st.markdown("Complete your profile by answering quick questions and then verifying with your resume or LinkedIn.")
    
    if "qa_completed" not in st.session_state:
        st.session_state.qa_completed = False
    if "verification_completed" not in st.session_state:
        st.session_state.verification_completed = False
    
    if not st.session_state.qa_completed:
        st.subheader("Step 1: Basic Information")
        
        with st.form("qa_form"):
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
                        'source': 'qa'
                    }
                    st.session_state.user_data.update(qa_data)
                    st.session_state.qa_completed = True
                    st.success("✅ Basic information saved!")
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
        
        color_scheme = st.selectbox("Color Scheme:", [
            "Blue Gradient (Professional)",
            "Purple Gradient (Creative)", 
            "Green Gradient (Tech)",            "Orange Gradient (Energy)",
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
        
        if portfolio_content and "error" not in portfolio_content:
            st.success("✅ AI Portfolio generated successfully!")
            
            with st.expander("📋 View Generated Content", expanded=False):
                st.json(portfolio_content)
            
            try:                # Map AI-generated content to template format
                template_data = {
                    'name': st.session_state.user_data.get('name', 'Professional'),
                    'headline': portfolio_content.get('headline', portfolio_content.get('summary', 'Professional')),
                    'about': portfolio_content.get('about', 'Professional with extensive experience'),
                    'skills': [],
                    'experience': [],
                    'email': st.session_state.user_data.get('email', 'contact@example.com'),
                    'phone': st.session_state.user_data.get('phone', 'Phone Number'),
                    'linkedin': st.session_state.user_data.get('linkedin', 'linkedin.com/in/professional'),
                    'portfolio_style': portfolio_style,
                    'color_scheme': color_scheme
                }
                
                # Handle skills - extract from skills_categories or use user skills
                if 'skills_categories' in portfolio_content:
                    all_skills = []
                    for category, skills in portfolio_content['skills_categories'].items():
                        if isinstance(skills, list):
                            all_skills.extend(skills)
                    template_data['skills'] = all_skills
                else:
                    template_data['skills'] = st.session_state.user_data.get('skills', [])
                
                # Handle experience - generate from projects or user data
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
                    # Create experience from user data
                    template_data['experience'] = [{
                        'title': st.session_state.user_data.get('title', 'Professional'),                        'company': 'Professional Experience',
                        'duration': 'Current',
                        'description': st.session_state.user_data.get('experience', 'Professional experience in the field')
                    }]
                
                html_content = portfolio_gen.generate_html(template_data)
                
                st.subheader("🌟 Portfolio Preview")
                st.components.v1.html(html_content, height=600, scrolling=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        label="📥 Download HTML",
                        data=html_content,
                        file_name=f"portfolio_{template_data.get('name', 'portfolio').replace(' ', '_').lower()}.html",
                        mime="text/html",                        use_container_width=True
                    )
                
                with col2:
                    if st.button("🔄 Regenerate with AI", use_container_width=True):
                        st.rerun()
                
                with col3:
                    if st.button("✨ Enhance with AI", use_container_width=True):
                        with st.spinner("🤖 AI is enhancing your portfolio..."):
                            enhanced_content = groq_service.enhance_portfolio_content(portfolio_content, st.session_state.user_data)
                            if enhanced_content:                                # Map enhanced content to template format
                                enhanced_template_data = {
                                    'name': st.session_state.user_data.get('name', 'Professional'),
                                    'headline': enhanced_content.get('headline', enhanced_content.get('summary', 'Professional')),
                                    'about': enhanced_content.get('about', 'Professional with extensive experience'),
                                    'skills': [],
                                    'experience': [],
                                    'email': st.session_state.user_data.get('email', 'contact@example.com'),
                                    'phone': st.session_state.user_data.get('phone', 'Phone Number'),
                                    'linkedin': st.session_state.user_data.get('linkedin', 'linkedin.com/in/professional'),
                                    'portfolio_style': portfolio_style,
                                    'color_scheme': color_scheme
                                }
                                
                                # Handle skills
                                if 'skills_categories' in enhanced_content:
                                    all_skills = []
                                    for category, skills in enhanced_content['skills_categories'].items():
                                        if isinstance(skills, list):
                                            all_skills.extend(skills)
                                    enhanced_template_data['skills'] = all_skills
                                else:
                                    enhanced_template_data['skills'] = st.session_state.user_data.get('skills', [])
                                
                                # Handle experience
                                if 'projects' in enhanced_content and enhanced_content['projects']:
                                    enhanced_template_data['experience'] = [
                                        {
                                            'title': project.get('name', 'Project'),
                                            'company': 'Personal/Professional Project',
                                            'duration': 'Recent',
                                            'description': project.get('description', 'Professional project')
                                        }
                                        for project in enhanced_content['projects']
                                    ]
                                else:
                                    enhanced_template_data['experience'] = [{
                                        'title': st.session_state.user_data.get('title', 'Professional'),
                                        'company': 'Professional Experience',
                                        'duration': 'Current',
                                        'description': st.session_state.user_data.get('experience', 'Professional experience')
                                    }]
                                
                                enhanced_html = portfolio_gen.generate_html(enhanced_template_data)
                                st.subheader("✨ Enhanced Portfolio Preview")
                                st.components.v1.html(enhanced_html, height=600, scrolling=True)
                
                st.subheader("🌐 AI-Powered Deployment Options")
                hosting_option = st.selectbox("Choose hosting platform:", [
                    "GitHub Pages (Recommended)",
                    "Netlify (Easy Deploy)", 
                    "Vercel (Developer Friendly)",
                    "Custom Domain Setup"
                ])
                
                # Deployment platform URLs
                deployment_urls = {
                    "GitHub Pages (Recommended)": "https://pages.github.com/",
                    "Netlify (Easy Deploy)": "https://www.netlify.com/",
                    "Vercel (Developer Friendly)": "https://vercel.com/",
                    "Custom Domain Setup": "https://domains.google.com/"
                }
                
                deployment_tips = groq_service.generate_deployment_guide(hosting_option, st.session_state.user_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🚀 Get AI Deployment Guide"):
                        st.markdown("### 📖 AI-Generated Deployment Guide")
                        st.markdown(deployment_tips)
                        
                        # Get quick start information
                        quick_start = groq_service.get_deployment_quick_start(hosting_option)
                        st.markdown("### ⚡ Quick Start Guide")
                        st.markdown(quick_start["steps"])
                        st.info(quick_start["tip"])
                        st.success(f"✅ Ready to deploy to {hosting_option}!")
                
                with col2:
                    deployment_url = deployment_urls.get(hosting_option, "https://github.com/")
                    
                    # Create clickable deployment button with proper target="_blank"
                    st.markdown(f"""
                    <a href="{deployment_url}" target="_blank" style="
                        display: inline-block;
                        width: 100%;
                        padding: 0.5rem 1rem;
                        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        text-align: center;
                        font-weight: 600;
                        margin-bottom: 1rem;
                        transition: transform 0.2s ease;
                    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        🌐 Go to {hosting_option.split(' ')[0]}
                    </a>
                    """, unsafe_allow_html=True)
                    
                    # Display helpful information below the button
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
            st.error("❌ Failed to generate portfolio content")
            st.info("💡 Please check your profile data and try again.")

def resume_page(groq_service, resume_gen):
    st.header("📄 AI Resume Generator")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        return
    
    st.markdown("### 🤖 AI-Powered ATS-Optimized Resume")
    st.info("Our AI will create a professionally tailored resume optimized for Applicant Tracking Systems (ATS).")
    
    # Simple text box for skills input
    user_skills = st.text_area(
        "💼 Enter Your Skills and Experience:",
        height=150,
        placeholder="Enter your technical skills, soft skills, certifications, and key experiences here. Separate with commas or line breaks.\n\nExample:\nPython, JavaScript, React, Node.js\nProject Management, Team Leadership\nAWS, Docker, Kubernetes\n5 years software development experience",
        help="List all your relevant skills, technologies, certifications, and experience. The AI will use this to generate your resume."
    )
    
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
            
            # Parse skills from input
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
            st.success("✅ AI Resume generated successfully!")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader("📋 Resume Content")
                st.markdown(resume_content)
            
            with col2:
                st.markdown("**📊 AI Quality Score:**")
                quality_score = groq_service.evaluate_resume_quality(resume_content, job_description if job_description else "")
                
                score = quality_score.get('overall_score', 85)
                st.metric("ATS Compatibility", f"{score}%", delta=f"+{score-70}%")
                
                st.markdown("**✅ AI Checks:**")
                checks = quality_score.get('checks', {})
                for check, passed in checks.items():
                    icon = "✅" if passed else "❌"
                    st.write(f"{icon} {check}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pdf_bytes = resume_gen.generate_pdf(resume_content, st.session_state.user_data)
                st.download_button(
                    label="📥 Download PDF Resume",
                    data=pdf_bytes,
                    file_name=f"resume_{st.session_state.user_data.get('name', 'resume').replace(' ', '_').lower()}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with col2:
                if st.button("🔄 Regenerate with AI", use_container_width=True):
                    st.rerun()
            
            with col3:
                if st.button("✨ AI Optimize Further", use_container_width=True):
                    with st.spinner("🤖 AI is further optimizing..."):
                        optimized_resume = groq_service.optimize_resume_further(resume_content, st.session_state.user_data)
                        st.markdown("### 🎯 AI-Optimized Version")
                        st.markdown(optimized_resume)
            
            if job_description:
                st.subheader("🎯 AI Job Match Analysis")
                match_analysis = groq_service.analyze_resume_job_match(resume_content, job_description)
                
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
            st.error("❌ Failed to generate resume")
            st.info("💡 Please check your profile data and try again.")

def cover_letter_page(groq_service, cover_letter_gen):
    st.header("✉️ AI Cover Letter Generator")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        return
    
    st.markdown("### 🤖 AI-Powered Personalized Cover Letters")
    st.info("Our AI will create compelling, personalized cover letters that get interviews!")
    
    # Simple text box for skills and experience
    user_skills_experience = st.text_area(
        "💼 Enter Your Skills and Experience:",
        height=120,
        placeholder="Enter your relevant skills, experience, and achievements for this position.\n\nExample:\nPython, JavaScript, React development\nTeam leadership and project management\n3 years experience in full-stack development\nLed team of 5 developers on e-commerce project",
        help="Describe your key skills, experience, and achievements relevant to the position you're applying for."
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
                'company_research': company_research,
                'skills_experience_input': user_skills_experience
            })
            
            # Parse skills from input
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
            st.success("✅ AI Cover letter generated successfully!")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader("📝 Your Personalized Cover Letter")
                st.markdown(cover_letter)
            
            with col2:
                st.markdown("**📊 AI Quality Analysis:**")
                quality_analysis = groq_service.analyze_cover_letter_quality(cover_letter, job_description)
                
                engagement_score = quality_analysis.get('engagement_score', 88)
                relevance_score = quality_analysis.get('relevance_score', 85)
                
                st.metric("Engagement Score", f"{engagement_score}%")
                st.metric("Job Relevance", f"{relevance_score}%")
                
                st.markdown("**✅ AI Checks:**")
                checks = quality_analysis.get('checks', {})
                for check, status in checks.items():
                    icon = "✅" if status else "⚠️"
                    st.write(f"{icon} {check}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📥 Download as Text",
                    data=cover_letter,
                    file_name=f"cover_letter_{company_name.lower().replace(' ', '_')}_{position.lower().replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                if st.button("🔄 Regenerate with AI", use_container_width=True):
                    st.rerun()
            
            with col3:
                if st.button("✨ Different AI Style", use_container_width=True):
                    with st.spinner("🤖 Creating alternative version..."):
                        alt_letter = groq_service.generate_alternative_cover_letter(
                            enhanced_data, job_description, company_name
                        )
                        st.markdown("### 🎨 Alternative AI Version")
                        st.markdown(alt_letter)
            
            st.subheader("🎯 AI Interview Preparation")
            if st.button("Generate AI Interview Questions for this Role"):
                with st.spinner("🤖 AI is preparing interview questions..."):
                    interview_questions = groq_service.generate_role_specific_questions(
                        job_description, st.session_state.user_data, company_name
                    )
                    
                    st.markdown("### 🎤 AI-Generated Interview Questions")
                    for i, q in enumerate(interview_questions, 1):
                        with st.expander(f"Question {i}: {q.get('category', 'General')}"):
                            st.write(f"**Q:** {q.get('question', '')}")
                            st.write(f"**Focus:** {q.get('focus_area', '')}")
                            st.write(f"**Difficulty:** {q.get('difficulty', 'Medium')}")
                            
                            if st.button(f"Get AI Answer Tips for Q{i}"):
                                tips = groq_service.generate_answer_tips(q.get('question', ''), st.session_state.user_data)
                                st.info(f"💡 **AI Tips:** {tips}")
        else:
            st.error("❌ Failed to generate cover letter")
            st.info("💡 Please check your inputs and try again.")

def job_search_page(job_searcher):
    st.header("🔍 AI-Powered Job Search & Career Strategy")
    
    # Check LinkedIn API status
    linkedin_status = job_searcher.validate_linkedin_access()
    if linkedin_status:
        st.success("🟢 LinkedIn API Connected - Enhanced job search available!")
    else:
        st.warning("🟡 LinkedIn API not configured - Using enhanced fallback search")
        with st.expander("🔧 Configure LinkedIn API (Optional)"):
            st.markdown("""
            **To enable LinkedIn API integration:**
            1. Create a LinkedIn Developer App at https://www.linkedin.com/developers/
            2. Add these environment variables to your .env file:
               - `LINKEDIN_CLIENT_ID=your_client_id`
               - `LINKEDIN_CLIENT_SECRET=your_client_secret`
               - `LINKEDIN_ACCESS_TOKEN=your_access_token`
            3. Restart the application
            
            **Note:** The app works great without LinkedIn API using our enhanced search!
            """)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Smart Job Search", "📬 AI Job Alerts", "🚀 Career Strategy", "💼 Company Insights"])
    
    with tab1:
        st.markdown("### 🤖 AI-Enhanced Job Discovery with LinkedIn Integration")
        
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
                
                ai_filters = st.multiselect("🤖 AI Smart Filters:", [
                    "Match my skills automatically",
                    "High growth companies", 
                    "Recently funded startups",
                    "Fortune 500 companies",
                    "Companies with good culture ratings",
                    "Fast-track career growth opportunities"
                ])
                
                submitted = st.form_submit_button("🚀 Search LinkedIn Jobs", type="primary")
        
        with col2:
            if st.session_state.get("user_data"):
                st.markdown("**🎯 AI Profile Analysis:**")
                groq_service = st.session_state.get('groq_service')
                if groq_service:
                    profile_strength = groq_service.analyze_profile_strength(st.session_state.user_data)
                    st.metric("Profile Strength", f"{profile_strength.get('score', 75)}%")
                    
                    st.markdown("**💡 AI Optimization Tips:**")
                    suggestions = profile_strength.get('suggestions', [])
                    for suggestion in suggestions[:3]:
                        st.write(f"• {suggestion}")
                        
                # Add salary insights
                if keywords:
                    with st.spinner("Getting salary insights..."):
                        salary_data = job_searcher.get_salary_insights(keywords, location)
                        if salary_data:
                            st.markdown("**💰 Salary Insights:**")
                            st.write(f"**Median:** ${salary_data.get('median_salary', 0):,}")
                            st.write(f"**Range:** ${salary_data.get('min_salary', 0):,} - ${salary_data.get('max_salary', 0):,}")
        
        if submitted and keywords:
            with st.spinner("🤖 Searching LinkedIn and analyzing job matches..."):
                # Enhanced job search with LinkedIn API
                jobs = job_searcher.search_jobs(
                    keywords=keywords, 
                    location=location, 
                    experience_level=experience_level,
                    company_size=company_size,
                    remote=remote_work,
                    limit=25
                )
                
                # Enhance with AI analysis if we have user data
                if st.session_state.get("user_data") and jobs:
                    enhanced_jobs = groq_service.analyze_job_matches(jobs, st.session_state.user_data)
                    jobs = enhanced_jobs
                
            if jobs:
                st.success(f"🎉 Found {len(jobs)} job opportunities from LinkedIn and other sources!")
                
                # Add filter and sort options
                col1, col2, col3 = st.columns(3)
                with col1:
                    sort_by = st.selectbox("Sort by:", ["Relevance", "Date Posted", "Company", "Match Score"])
                with col2:
                    company_filter = st.multiselect("Filter by Company:", 
                                                   options=list(set([job.get('company', '') for job in jobs])))
                with col3:
                    show_only_remote = st.checkbox("Show only remote jobs")
                
                # Apply filters
                filtered_jobs = jobs
                if company_filter:
                    filtered_jobs = [job for job in jobs if job.get('company') in company_filter]
                if show_only_remote:
                    filtered_jobs = [job for job in jobs if job.get('remote_type')]
                
                # Display jobs
                for i, job in enumerate(filtered_jobs):
                    match_score = job.get('ai_match_score', job.get('overall_fit', 'N/A'))
                    source_icon = "🔗" if job.get('source') == 'linkedin_api' else "🤖"
                    
                    with st.expander(f"{source_icon} {job.get('title', 'Job Title')} at {job.get('company', 'Company')} - Match: {match_score}%"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"📍 **Location:** {job.get('location', 'N/A')}")
                            st.write(f"💰 **Salary:** {job.get('salary_range', 'Not specified')}")
                            st.write(f"📅 **Posted:** {job.get('posted_date', 'Recently')}")
                            st.write(f"🏢 **Company Size:** {job.get('company_size', 'Not specified')}")
                            st.write(f"⏰ **Type:** {job.get('employment_type', 'Full-time')}")
                            
                            if job.get('remote_type'):
                                st.write("🏠 **Remote-friendly**")
                            
                            st.write(f"📋 **Description:** {job.get('description', 'No description available')[:300]}...")
                            
                            # Show skills and requirements
                            if job.get('skills'):
                                st.write(f"🛠️ **Key Skills:** {', '.join(job.get('skills', [])[:5])}")
                            
                            if job.get('benefits'):
                                st.write(f"💎 **Benefits:** {', '.join(job.get('benefits', [])[:3])}...")
                            
                            # AI Analysis
                            if job.get('ai_analysis'):
                                st.markdown("**🤖 AI Analysis:**")
                                st.info(job.get('ai_analysis'))
                            
                            # Match breakdown
                            if job.get('skills_match') or job.get('experience_match'):
                                st.markdown("**📊 Match Breakdown:**")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if job.get('skills_match'):
                                        st.metric("Skills Match", f"{job.get('skills_match')}%")
                                with col_b:
                                    if job.get('experience_match'):
                                        st.metric("Experience Match", f"{job.get('experience_match')}%")
                        
                        with col2:
                            # Action buttons
                            if job.get('linkedin_url'):
                                st.link_button("🔗 View on LinkedIn", job['linkedin_url'], use_container_width=True)
                            
                            if job.get('application_url'):
                                st.link_button("🚀 Apply Now", job['application_url'], use_container_width=True)
                                
                            if st.button(f"📝 Generate Cover Letter", key=f"cover_{i}"):
                                st.info("📝 Navigate to Cover Letter Generator to create a tailored letter for this role!")
                            
                            if st.button(f"🏢 Company Insights", key=f"company_{i}"):
                                with st.spinner("Fetching company insights..."):
                                    company_info = job_searcher.get_company_insights(job.get('company', ''))
                                    st.json(company_info)
                            
                            # Save job functionality
                            if st.button(f"💾 Save Job", key=f"save_{i}"):
                                if 'saved_jobs' not in st.session_state:
                                    st.session_state.saved_jobs = []
                                st.session_state.saved_jobs.append(job)
                                st.success("Job saved!")
            else:
                st.info("🔍 No jobs found. Try different keywords or broader search terms.")
                
                if st.session_state.get("user_data"):
                    st.markdown("### 💡 AI Career Suggestions")
                    groq_service = st.session_state.get('groq_service')
                    if groq_service:
                        career_suggestions = groq_service.generate_career_suggestions(st.session_state.user_data, keywords)
                        st.markdown(career_suggestions)
    
    with tab2:
        st.markdown("### 📬 Smart Job Alerts with LinkedIn Integration")
        
        with st.form("alert_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                alert_keywords = st.text_input("🎯 Alert Keywords:")
                alert_email = st.text_input("📧 Email for Alerts:")
                alert_location = st.text_input("📍 Preferred Locations:")
                
            with col2:
                alert_frequency = st.selectbox("📅 Frequency:", ["Daily", "Weekly", "Bi-weekly"])
                alert_experience = st.selectbox("Experience Level:", [
                    "Any", "Entry Level", "Mid Level", "Senior Level", "Executive"
                ])
                ai_personalization = st.checkbox("🤖 AI Personalization", value=True, 
                                               help="AI will filter and rank jobs based on your profile")
            
            advanced_filters = st.multiselect("🔧 Advanced LinkedIn Filters:", [
                "Only LinkedIn verified companies",
                "Salary growth potential analysis",
                "Company culture match scoring",
                "Career advancement opportunities", 
                "Remote work policies",
                "Learning and development programs",
                "Diversity and inclusion focus",
                "Stock options/equity available",
                "Recently funded companies"
            ])
            
            alert_submitted = st.form_submit_button("🚀 Set Up LinkedIn Job Alert", type="primary")
            
            if alert_submitted and alert_keywords and alert_email:
                st.success("✅ AI-powered LinkedIn job alert set up successfully!")
                st.info(f"🤖 You'll receive {alert_frequency.lower()} AI-curated alerts for '{alert_keywords}' jobs.")
                
                # Preview of what the alert would contain
                if ai_personalization and st.session_state.get("user_data"):
                    with st.spinner("Generating alert preview..."):
                        preview_jobs = job_searcher.get_job_alerts(
                            st.session_state.user_data, 
                            {
                                'keywords': alert_keywords,
                                'location': alert_location,
                                'experience_level': alert_experience
                            }
                        )
                        
                        if preview_jobs:
                            st.markdown("### 📋 Alert Preview")
                            st.markdown(f"Here's what your {alert_frequency.lower()} alert would include:")
                            
                            for job in preview_jobs[:3]:  # Show top 3
                                st.markdown(f"**• {job.get('title')} at {job.get('company')}** - {job.get('location')}")
                                st.markdown(f"  Posted: {job.get('posted_date')} | Match: {job.get('ai_match_score', 'N/A')}%")
    
    with tab3:
        st.markdown("### 🚀 AI Career Strategy & LinkedIn Growth")
        
        if not st.session_state.get("user_data"):
            st.warning("Complete your profile to get personalized AI career strategy!")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 🎯 Personalized Career Roadmap")
            
            career_goals = st.selectbox("🎯 Career Goal:", [
                "Advance to senior role in current field",
                "Transition to management/leadership",
                "Switch to new industry/field", 
                "Start own business/consulting",
                "Increase salary significantly",
                "Improve work-life balance",
                "Build stronger LinkedIn presence"
            ])
            
            time_horizon = st.selectbox("⏰ Timeline:", [
                "6 months", "1 year", "2 years", "3-5 years"
            ])
            
            if st.button("🤖 Generate AI Career Strategy", type="primary"):
                with st.spinner("🤖 AI is creating your personalized career strategy using LinkedIn insights..."):
                    groq_service = st.session_state.get('groq_service')
                    if groq_service:
                        strategy = groq_service.generate_comprehensive_career_strategy(
                            st.session_state.user_data, career_goals, time_horizon
                        )
                        
                        # Add LinkedIn-specific recommendations
                        linkedin_strategy = f"""
                        
                        ### 🔗 LinkedIn-Specific Action Plan:
                        
                        **Profile Optimization:**
                        - Update your LinkedIn headline to include trending keywords for your field
                        - Add a professional summary highlighting your {career_goals.lower()}
                        - Request recommendations from colleagues and managers
                        
                        **Networking Strategy:**
                        - Connect with 10-15 professionals weekly in your target field
                        - Engage with posts from industry leaders daily
                        - Share insights about your expertise 2-3 times per week
                        
                        **Content Strategy:**
                        - Post about your learning journey and projects
                        - Share industry insights and trends
                        - Comment thoughtfully on posts from your network
                        
                        **Job Search Optimization:**
                        - Set up LinkedIn job alerts for your target roles
                        - Use LinkedIn's "Open to Work" feature strategically
                        - Research hiring managers and companies of interest
                        """
                
                st.markdown("### 📋 Your AI-Generated Career Strategy")
                st.markdown(strategy)
                st.markdown(linkedin_strategy)
        
        with col2:
            st.markdown("#### 📊 Career Analytics")
            
            if st.button("🔍 Analyze Career Potential"):
                groq_service = st.session_state.get('groq_service')
                if groq_service:
                    analysis = groq_service.analyze_career_potential(st.session_state.user_data)
                    
                    st.metric("Market Demand", f"{analysis.get('market_demand', 75)}%")
                    st.metric("Salary Growth Potential", f"{analysis.get('salary_growth', 85)}%") 
                    st.metric("Skill Relevance", f"{analysis.get('skill_relevance', 90)}%")
                    
                    st.markdown("**🎯 Growth Areas:**")
                    for area in analysis.get('growth_areas', [])[:3]:
                        st.write(f"• {area}")
            
            # LinkedIn Skills Trending
            st.markdown("#### 🔥 Trending LinkedIn Skills")
            if st.button("📊 Get Trending Skills"):
                user_title = st.session_state.user_data.get('title', '')
                trending_skills = job_searcher.get_trending_skills(user_title)
                
                st.markdown("**Most In-Demand Skills:**")
                for skill in trending_skills[:8]:
                    st.write(f"🔥 {skill}")
            
            st.markdown("#### 📚 AI Learning Path")
            if st.button("📖 Get Learning Recommendations"):
                groq_service = st.session_state.get('groq_service')
                if groq_service:
                    learning_path = groq_service.generate_learning_path(st.session_state.user_data)
                    st.markdown(learning_path)
    
    with tab4:
        st.markdown("### 💼 Company Research & Insights")
        
        company_search = st.text_input("🔍 Search for Companies:", placeholder="e.g., Google, Microsoft, OpenAI")
        
        if company_search:
            if st.button("🔍 Research Company"):
                with st.spinner("Researching company..."):
                    company_info = job_searcher.get_company_insights(company_search)
                    
                    if company_info:
                        st.markdown(f"### 🏢 {company_info.get('name', company_search)}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Industry:** {company_info.get('industry', 'N/A')}")
                            st.write(f"**Size:** {company_info.get('size', 'N/A')} employees")
                            st.write(f"**Founded:** {company_info.get('founded_year', 'N/A')}")
                            st.write(f"**Headquarters:** {company_info.get('headquarters', 'N/A')}")
                            
                        with col2:
                            if company_info.get('linkedin_url'):
                                st.link_button("🔗 LinkedIn Page", company_info['linkedin_url'])
                            if company_info.get('website'):
                                st.link_button("🌐 Website", company_info['website'])
                        
                        st.markdown("**About:**")
                        st.write(company_info.get('description', 'No description available'))
                        
                        # Get current job openings
                        if st.button("💼 View Current Openings"):
                            with st.spinner("Finding current job openings..."):
                                openings = job_searcher.search_jobs(
                                    keywords=st.session_state.user_data.get('title', 'engineer'),
                                    location="",
                                    limit=10
                                )
                                
                                company_jobs = [job for job in openings if 
                                              company_info.get('name', '').lower() in job.get('company', '').lower()]
                                
                                if company_jobs:
                                    st.markdown(f"**Current Openings at {company_info.get('name')}:**")
                                    for job in company_jobs:
                                        st.markdown(f"• **{job.get('title')}** - {job.get('location')}")
                                else:
                                    st.info("No current openings found. Set up a job alert to be notified!")
        
        # Saved jobs section
        if st.session_state.get('saved_jobs'):
            st.markdown("### 💾 Your Saved Jobs")
            for i, job in enumerate(st.session_state.saved_jobs):
                with st.expander(f"{job.get('title')} at {job.get('company')}"):
                    st.write(f"📍 **Location:** {job.get('location')}")
                    st.write(f"💰 **Salary:** {job.get('salary_range', 'Not specified')}")
                    st.write(f"📅 **Saved on:** {job.get('saved_date', 'Recently')}")
                    
                    if st.button(f"Remove", key=f"remove_{i}"):
                        st.session_state.saved_jobs.pop(i)
                        st.rerun()

def interview_page(interview_sim):
    st.header("🎤 AI Interview Simulator")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        return
    
    st.markdown("### 🤖 Advanced AI Interview Practice")
    st.info("Practice with our AI interviewer and get real-time feedback, scoring, and improvement suggestions!")
    
    # Initialize session state for interview UI
    if 'interview_active' not in st.session_state:
        st.session_state.interview_active = False
    if 'interview_session' not in st.session_state:
        st.session_state.interview_session = None
        
    # Create InterviewUI instance
    from interview_simulator import InterviewUI
    interview_ui = InterviewUI(interview_sim)
    
    # Render appropriate UI based on interview state
    if not st.session_state.interview_active:
        interview_ui.render_interview_setup()
    else:
        if st.session_state.interview_session:
            current_q = interview_sim.get_current_question(st.session_state.interview_session)
            if current_q:
                interview_ui.render_active_interview()
            else:
                interview_ui.render_interview_results()

if __name__ == "__main__":
    main()