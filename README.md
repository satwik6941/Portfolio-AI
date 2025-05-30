# 🚀 AI Career Assistant

## 📋 Overview

An AI-powered career assistant web application that transforms your career with intelligent tools for:

- **📤 Resume Upload & Analysis** - AI-powered resume parsing and profile extraction
- **🌐 Portfolio Generation** - Professional portfolios with AI-generated projects
- **📄 ATS-Optimized Resumes** - Smart resume generation tailored to job descriptions
- **✉️ Cover Letter Creation** - Personalized cover letters with company research
- **🔍 Job Search** - Real-time job scraping with AI match analysis
- **🎤 Interview Simulation** - Chat-based AI interview practice with detailed feedback
- **💬 Resume Chat** - Interactive AI assistant for resume improvement

---

## 🛠️ Recent Fixes Applied

### ✅ Syntax Error Resolution (COMPLETED)
- **Fixed Try-Except Blocks**: Added missing `except Exception as e:` clauses
- **Fixed Statement Separation**: Resolved multiple "Statements must be separated by newlines or semicolons" errors
- **Fixed Indentation Issues**: Corrected improper indentation throughout the codebase
- **Fixed File Ending**: Replaced corrupted Unicode characters with proper `if __name__ == "__main__": main()` block
- **Function Integrity**: Maintained all existing functionality while fixing syntax issues

### 🎯 Error Types Fixed
1. **Missing Exception Handlers**: Added proper try-except blocks
2. **Statement Separation**: Fixed missing newlines between statements
3. **Indentation Errors**: Corrected misaligned code blocks
4. **File Corruption**: Removed invalid Unicode characters from file ending
5. **Import Issues**: Verified all module imports are working correctly

---

## 🔧 Technical Details

### Fixed Architecture
- **Frontend**: Streamlit web interface
- **Backend**: Python with AI service integrations
- **AI Services**: Groq LLM for intelligent content generation
- **Job Search**: Multi-platform web scraping (Indeed, LinkedIn, Glassdoor)
- **File Processing**: Resume parsing with OCR support

### Project Structure
```
Portfolio AI/
├── main.py                 # ✅ Main application (FIXED)
├── groq_service.py         # AI service integration
├── data_extractor.py       # Resume parsing and data extraction
├── generators_combined.py  # Portfolio, resume, cover letter generators
├── interview_simulator.py  # AI interview simulation
├── job_scraper.py         # Job search and scraping
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (configured)
├── templates/             # HTML templates for portfolios
├── start_app.bat         # Windows launcher
├── start_app.ps1         # PowerShell launcher
└── validate_app.py       # Application validation script
```

---

## 🎉 Application Features

### 1. **📤 Data Input**
- Resume upload with AI parsing
- Manual profile creation
- Real-time editing interface
- Profile verification system

### 2. **🌐 Portfolio Generator**
- AI-generated professional portfolios
- Multiple design themes
- Project showcase generation
- Download as HTML

### 3. **📄 Resume Generator**
- ATS-optimized resume creation
- Job-specific tailoring
- STAR method project formatting
- PDF export functionality

### 4. **✉️ Cover Letter Generator**
- Personalized cover letter creation
- Company research integration
- Multiple tone options
- PDF export

### 5. **🔍 AI Job Search**
- Real-time job scraping
- AI-powered job matching
- Salary insights in INR
- Application tracking

### 6. **🎤 Interview Simulator**
- Chat-based interview practice
- AI-generated questions
- Real-time feedback
- Performance analytics

### 7. **💬 Resume Chat**
- Interactive AI assistant
- Resume improvement suggestions
- Career guidance
- Skills analysis

---

## 🔑 API Keys Configuration

The application uses the following APIs (already configured in `.env`):
