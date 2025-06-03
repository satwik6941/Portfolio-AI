# 🚀 ResuMate - AI Career Assistant

> **Transform your career journey with cutting-edge AI tools for portfolios, resumes, and interview preparation**

ResuMate is a comprehensive AI-powered career assistant that helps job seekers create professional portfolios, optimize resumes, practice interviews, and search for jobs - all powered by advanced LLM technology.

## 🌐 Try It Online
You can interact with the application directly in your browser at [resuMate](https://rezumate.streamlit.app/) 🚀

### Key Features Preview
- 🤖 **AI-Powered Data Extraction** - Automatically parse resumes and LinkedIn profiles
- 🌐 **Professional Portfolio Generation** - Create stunning portfolios in minutes
- 📄 **Smart Resume Builder** - ATS-optimized resumes tailored to job descriptions
- ✉️ **Dynamic Cover Letters** - Personalized cover letters for any job
- 🔍 **Intelligent Job Search** - Multi-platform job discovery with AI matching
- 🎤 **Interview Simulator** - Practice with AI-generated questions and feedback
- 💬 **Resume Chat Assistant** - Get career advice and resume feedback

## ✨ Features

### 📤 **Data Input & Analysis**
- **AI Resume Parsing**: Upload PDF/DOCX/Images and get intelligent data extraction
- **Profile Management**: Edit and manage your career information with AI assistance
- **Project Import**: Automatically extract projects from your existing resume

### 🌐 **Portfolio Generator**
- **AI-Powered Creation**: Generate stunning portfolios with customizable themes
- **Multiple Styles**: Professional, Creative, Technical, Executive, and Minimalist designs
- **Smart Content**: AI creates project examples and enhances your profile
- **One-Click Deployment**: Deploy to Vercel, Netlify, or GitHub Pages instantly

### 📄 **Resume Generator**
- **ATS-Optimized**: Generate resumes that pass Applicant Tracking Systems
- **Job-Tailored**: AI customizes your resume for specific job descriptions
- **STAR Method**: Automatically formats projects using proven methodologies
- **Multiple Formats**: Professional, Creative, Executive, Technical, and Entry-level styles

### ✉️ **Cover Letter Creator**
- **Personalized Letters**: AI researches companies and tailors content
- **Professional Tones**: Choose from Professional, Enthusiastic, or Formal styles
- **Smart Matching**: Analyzes job requirements and highlights relevant skills

### 🔍 **Job Search Engine**
- **Multi-Platform Search**: Scrapes Indeed, LinkedIn, Glassdoor simultaneously
- **AI Match Analysis**: Intelligent job-skill matching with percentage scores
- **Market Insights**: Get salary ranges, demand levels, and growth potential
- **Smart Filtering**: Filter by experience level, location, job type, and more

### 🎤 **Interview Simulator**
- **AI Interview Practice**: Role-specific questions powered by LLama 70B
- **Real-time Scoring**: Get instant feedback on your answers (1-10 scale)
- **Detailed Analytics**: Comprehensive performance reports with improvement suggestions
- **Customizable Length**: Choose 5, 10, or 15 questions per session

### 💬 **Resume Chat Assistant**
- **Interactive AI**: Chat with an AI that knows your resume inside-out
- **Career Guidance**: Get personalized advice and recommendations
- **Skill Gap Analysis**: Identify areas for professional development
- **Market Trends**: Stay updated with industry insights

## 🎯 Usage Guide

### Getting Started
1. **Upload Resume**: Start by uploading your resume in the "Data Input" section
2. **Verify Profile**: Review and edit the AI-extracted information
3. **Generate Content**: Use any of the AI-powered tools to create professional materials

### Local Development
```bash
streamlit run main.py
```

### Cloud Deployment

#### **Streamlit Community Cloud** (Recommended)
1. Fork this repository
2. Connect to [share.streamlit.io](https://share.streamlit.io)
3. Add your `GROQ_API_KEY` in secrets
4. Deploy with one click

## 🔧 Technical Architecture

### Core Technologies
- **Frontend**: Streamlit with custom CSS styling
- **Backend**: Python with service-oriented architecture
- **AI Engine**: Groq's LLama 70B model for content generation
- **Data Processing**: PyMuPDF, python-docx, pytesseract for file parsing
- **Web Scraping**: BeautifulSoup4, Selenium for job search
- **Deployment**: Supports cloud deployment on major platforms

### Project Structure
```
Portfolio AI/
├── main.py                 # Main Streamlit application
├── groq_service.py         # AI service integration and LLM logic
├── data_extractor.py       # Resume parsing and data extraction
├── generators_combined.py  # Portfolio, resume, cover letter generators
├── interview_simulator.py  # AI interview simulation engine
├── job_scraper.py         # Multi-platform job search
├── ai_data_service.py     # Additional AI utilities
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── templates/             # HTML templates for portfolio generation
└── README.md             # Project documentation
```

## 🔧 Configuration

### Environment Variables
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Python Dependencies
- `streamlit` - Web framework
- `python-dotenv` - Environment management
- `requests` - HTTP client
- `PyMuPDF` - PDF processing
- `python-docx` - Word document parsing
- `pytesseract` - OCR capabilities
- `Pillow` - Image processing
- `beautifulsoup4` - Web scraping
- `selenium` - Browser automation

See [requirements.txt](requirements.txt) for complete list.


<div align="center">

**Built with ❤️ using Python and AI**

</div>

