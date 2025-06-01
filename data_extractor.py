import fitz  
import docx
import pytesseract
from PIL import Image
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from typing import Dict, List, Optional
from ai_data_service import AIDataService

class DataExtractor:
    def __init__(self):
        pass
    
    def extract_from_file(self, file) -> str:
        if file.name.endswith(".pdf"):
            return self._extract_from_pdf(file)
        elif file.name.endswith(".docx"):
            return self._extract_from_docx(file)
        elif file.name.lower().endswith((".jpg", ".jpeg", ".png")):
            return self._extract_from_image(file)
        else:
            return ""
    
    def _extract_from_pdf(self, file) -> str:
        text = ""
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            page_text = page.get_text()
            if page_text.strip():
                text += page_text
            else:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text += pytesseract.image_to_string(img)
        return text

    def _extract_from_docx(self, file) -> str:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def _extract_from_image(self, file) -> str:
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    
    def extract_from_linkedin(self, linkedin_url: str) -> Dict:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(linkedin_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            name = soup.find('h1', class_='text-heading-xlarge')
            headline = soup.find('div', class_='text-body-medium')
            
            return {
                'name': name.text.strip() if name else "",
                'headline': headline.text.strip() if headline else "",
                'url': linkedin_url,
                'note': 'Limited data due to LinkedIn restrictions. Consider manual input.'
            }
        except Exception as e:
            return {'error': f'Could not extract LinkedIn data: {e}'}

def parse_resume_data(text: str) -> Dict:
        """Enhanced resume parsing with improved education and project extraction"""
        data = {
            'name': '',
            'email': '',
            'phone': '',
            'skills': [],
            'experience': [],
            'education': [],
            'projects': []
        }
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            data['email'] = emails[0]
        
        # Phone extraction
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            data['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]

        # Name extraction
        lines = text.split('\n')
        for line in lines[:5]:  
            line = line.strip()
            if line and not any(char.isdigit() for char in line) and '@' not in line:
                if len(line.split()) <= 4:  
                    data['name'] = line
                    break
        
        # Enhanced skill extraction
        skill_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'SQL',
            'Machine Learning', 'Data Analysis', 'Project Management', 'Leadership',
            'Communication', 'Problem Solving', 'Teamwork', 'HTML', 'CSS', 'PHP',
            'Ruby', 'Swift', 'Kotlin', 'Go', 'Rust', 'Docker', 'Kubernetes', 'AWS',
            'Azure', 'GCP', 'MongoDB', 'PostgreSQL', 'Redis', 'Git', 'Linux'
        ]
        
        for skill in skill_keywords:
            if skill.lower() in text.lower():
                data['skills'].append(skill)
        
        # Enhanced education extraction with section detection
        data['education'] = _extract_education_section(text)
        
        # Enhanced project extraction with section detection
        data['projects'] = _extract_projects_enhanced(text)
        
        return data

def _extract_education_section(text: str) -> str:
    """Extract education information by looking for education headings and content"""
    education_headings = [
        'education', 'academic background', 'qualifications', 'degrees',
        'university', 'college', 'school', 'certification', 'training'
    ]
    
    lines = text.split('\n')
    education_content = []
    in_education_section = False
    section_started = False
    
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        
        # Check if this line is an education heading
        if any(heading in line_lower for heading in education_headings):
            if len(line.strip()) < 50:  # Likely a heading, not content
                in_education_section = True
                section_started = True
                continue
        
        # Check if we've moved to a different section
        other_sections = ['experience', 'work', 'employment', 'skills', 'projects', 'summary']
        if in_education_section and any(section in line_lower for section in other_sections):
            if len(line.strip()) < 50:  # Likely a new section heading
                break
        
        # If we're in education section, collect content
        if in_education_section and line.strip():
            # Look for degree indicators
            degree_indicators = ['bachelor', 'master', 'phd', 'diploma', 'certificate', 'degree', 'university', 'college']
            if any(indicator in line_lower for indicator in degree_indicators):
                education_content.append(line.strip())
            elif section_started and len(line.strip()) > 10:
                education_content.append(line.strip())
    
    if education_content:
        return ' | '.join(education_content[:3])  # Limit to 3 most relevant entries
    
    # Fallback: look for degree patterns anywhere in text
    degree_patterns = [
        r'(Bachelor|Master|PhD|B\.?[AS]|M\.?[AS]|Ph\.?D\.?).*?(?:in|of).*?(?:\d{4}|\n)',
        r'(University|College).*?(?:\d{4}|\n)',
        r'(GPA|CGPA).*?(?:\d\.\d|\n)'
    ]
    
    for pattern in degree_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return ' | '.join(matches[:2])
    
    return "Not found"

def _extract_projects_enhanced(text: str) -> List[Dict]:
    """Enhanced project extraction with better format recognition"""
    import re
    
    project_headings = [
        'projects', 'personal projects', 'key projects', 'major projects',
        'professional projects', 'academic projects', 'side projects',
        'portfolio', 'work samples', 'capstone', 'thesis', 'research',
        'open source', 'github', 'repositories'
    ]
    
    lines = text.split('\n')
    projects = []
    in_project_section = False
    current_project = None
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        # Skip empty lines
        if not line_stripped:
            continue
        
        # Check if this line is a project section heading
        if any(heading in line_lower for heading in project_headings):
            if len(line_stripped) < 50 and not any(char.isdigit() for char in line_stripped):
                in_project_section = True
                # Save any pending project
                if current_project and current_project.get('title'):
                    projects.append(current_project)
                    current_project = None
                continue
        
        # Check if we've moved to a different section
        other_sections = ['experience', 'work history', 'employment', 'skills', 'education', 'summary', 'contact']
        if in_project_section and any(section in line_lower for section in other_sections):
            if len(line_stripped) < 50 and ':' not in line_stripped:
                if current_project and current_project.get('title'):
                    projects.append(current_project)
                in_project_section = False
                break
        
        # If we're in project section, parse projects
        if in_project_section and line_stripped:
            
            # Format 1: Pipe-delimited format (Title | Tech | Duration)
            if '|' in line_stripped and not line_stripped.startswith(('•', '-', '*')):
                if current_project and current_project.get('title'):
                    projects.append(current_project)
                
                parts = [part.strip() for part in line_stripped.split('|')]
                if len(parts) >= 2:
                    current_project = {
                        "title": parts[0],
                        "technologies": parts[1] if len(parts) > 1 else "Not specified",
                        "duration": parts[2] if len(parts) > 2 else "Not specified",
                        "description": ""
                    }
                continue
            
            # Format 2: Numbered list format (1. Project Name)
            numbered_match = re.match(r'^(\d+)\.?\s+(.+)', line_stripped)
            if numbered_match and len(numbered_match.group(2)) > 5:
                if current_project and current_project.get('title'):
                    projects.append(current_project)
                
                current_project = {
                    "title": numbered_match.group(2),
                    "technologies": "Not specified",
                    "duration": "Not specified", 
                    "description": ""
                }
                continue
            
            # Format 3: Project Name: followed by details
            if line_stripped.startswith(('Project Name:', 'Project:')):
                if current_project and current_project.get('title'):
                    projects.append(current_project)
                
                title = line_stripped.replace('Project Name:', '').replace('Project:', '').strip()
                current_project = {
                    "title": title,
                    "technologies": "Not specified",
                    "duration": "Not specified",
                    "description": ""
                }
                continue
            
            # Format 4: All caps or emphasized title lines
            if (line_stripped.isupper() or 
                (15 < len(line_stripped) < 80 and 
                 line_stripped[0].isupper() and 
                 not line_stripped.startswith(('•', '-', '*')) and
                 not any(word in line_lower for word in ['technologies', 'duration', 'tech', 'stack', 'using', 'built', 'description']))):
                
                if current_project and current_project.get('title'):
                    projects.append(current_project)
                
                current_project = {
                    "title": line_stripped,
                    "technologies": "Not specified",
                    "duration": "Not specified",
                    "description": ""
                }
                continue
            
            # Extract additional details for current project
            if current_project:
                # Extract technologies
                tech_patterns = [
                    r'(?:technologies?|tech stack|tech|stack|tools|languages|frameworks?):\s*(.+)',
                    r'(?:using|built with|made with):\s*(.+)',
                    r'(?:technologies used|tech used):\s*(.+)'
                ]
                
                for pattern in tech_patterns:
                    tech_match = re.search(pattern, line_stripped, re.IGNORECASE)
                    if tech_match and current_project['technologies'] == "Not specified":
                        current_project['technologies'] = tech_match.group(1).strip()
                        continue
                
                # Extract duration/timeline
                duration_patterns = [
                    r'(?:duration|timeline|time|period):\s*(.+)',
                    r'(\d+\s*(?:months?|weeks?|years?))',
                    r'(\d{4}\s*-\s*\d{4})',
                    r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*-\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
                    r'(\d{1,2}/\d{4}\s*-\s*\d{1,2}/\d{4})',
                    r'\(([^)]+(?:months?|years?)[^)]*)\)'
                ]
                
                for pattern in duration_patterns:
                    duration_match = re.search(pattern, line_stripped, re.IGNORECASE)
                    if duration_match and current_project['duration'] == "Not specified":
                        current_project['duration'] = duration_match.group(1).strip()
                        break
                
                # Extract description from bullet points or descriptive text
                if (line_stripped.startswith(('•', '-', '*', '◦')) or 
                    any(word in line_lower for word in ['developed', 'built', 'created', 'implemented', 'designed', 'achieved', 'features'])):
                    
                    desc_text = line_stripped.lstrip('•-*◦ ').strip()
                    if current_project['description']:
                        current_project['description'] += " " + desc_text
                    else:
                        current_project['description'] = desc_text
    
    # Add the last project if it exists
    if current_project and current_project.get('title'):
        projects.append(current_project)
    
    # Clean and validate projects
    cleaned_projects = []
    seen_titles = set()
    
    for project in projects:
        if not project.get('title') or len(project['title']) < 3:
            continue
        
        title_lower = project['title'].lower().strip()
        
        # Skip duplicates and generic titles
        if title_lower in seen_titles or title_lower in ['project', 'projects', 'work']:
            continue
        
        seen_titles.add(title_lower)
        
        # Ensure minimum description
        if not project.get('description') or len(project['description'].strip()) < 10:
            project['description'] = "Project details available upon request"
        
        cleaned_projects.append(project)
    
    return cleaned_projects[:5]

class JobSearcher:
    def __init__(self):
        self.job_scraper = None
        self.scraper_available = False
        self.job_cache = {}  # Cache for performance
        
        # Initialize AI data service
        self.ai_data_service = None
        try:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                self.ai_data_service = AIDataService(api_key)
            else:
                print("⚠️ No GROQ_API_KEY found for AI data service")
        except Exception as e:
            print(f"⚠️ Could not initialize AI data service: {e}")
            self.ai_data_service = None
        
        # Initialize the new Beautiful Soup job scraper
        self._initialize_job_scraper()
    
    def _initialize_job_scraper(self):
        """Initialize Beautiful Soup job scraper"""
        try:
            from job_scraper import JobScraper
            self.job_scraper = JobScraper()
            self.scraper_available = True
            print("✅ Job scraper initialized successfully - now using latest job postings!")
        except Exception as e:
            print(f"⚠️ Job scraper initialization failed: {str(e)}")
            print("Job search will use AI-powered fallback methods")
            self.job_scraper = None
            self.scraper_available = False
    
    def search_jobs(self, keywords: str, location: str = "", experience_level: str = "", 
                    company_size: str = "", remote: bool = False, job_type: str = "Full-time Jobs", limit: int = 20) -> List[Dict]:
        try:
            if self.scraper_available and self.job_scraper:
                # Use Beautiful Soup job scraper for latest postings
                print(f"🔍 Searching for latest {keywords} jobs...")
                
                jobs = self.job_scraper.aggregate_job_search(
                    keywords=keywords,
                    location=location,
                    limit=limit
                )
                
                if jobs:
                    # Filter by experience level and company size if specified
                    filtered_jobs = self._filter_jobs_by_criteria(jobs, experience_level, company_size, remote)
                    
                    # Enhance jobs with AI insights
                    for job in filtered_jobs:
                        job = self._enhance_job_with_insights(job, keywords)
                    
                    cache_key = f"{keywords}_{location}_{experience_level}"
                    self.job_cache[cache_key] = filtered_jobs
                    print(f"✅ Found {len(filtered_jobs)} latest job postings!")
                    return filtered_jobs
                    
        except Exception as e:
            print(f"Job scraper error, using fallback: {str(e)}")
        
        return self._fallback_search(keywords, location, experience_level, job_type, limit)
    
    def _filter_jobs_by_criteria(self, jobs: List[Dict], experience_level: str, 
                                company_size: str, remote: bool) -> List[Dict]:
        """Filter jobs based on additional criteria"""
        filtered_jobs = []
        
        for job in jobs:
            # Filter by remote preference
            if remote and not job.get('remote_type'):
                continue
            
            # Filter by company size (basic matching)
            if company_size and company_size != job.get('company_size', ''):
                # Allow some flexibility in company size matching
                pass
            
            # Filter by experience level (basic keyword matching in description)
            if experience_level:
                exp_keywords = self._get_experience_keywords(experience_level)
                job_text = f"{job.get('description', '')} {job.get('title', '')}".lower()
                
                if exp_keywords and not any(keyword in job_text for keyword in exp_keywords):
                    # Still include job but lower its relevance
                    job['experience_match'] = False
                else:
                    job['experience_match'] = True
            
            filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _get_experience_keywords(self, experience_level: str) -> List[str]:
        """Get keywords associated with experience levels"""
        level_keywords = {
            "Entry Level (0-2 years)": ["entry", "junior", "associate", "new grad", "0-2 years"],
            "Mid Level (3-5 years)": ["mid", "intermediate", "3-5 years", "experienced"],
            "Senior Level (6-10 years)": ["senior", "lead", "principal", "6+ years", "expert"],
            "Executive (10+ years)": ["director", "manager", "executive", "head of", "vp", "chief"]
        }
        
        return level_keywords.get(experience_level, [])
    
    def get_job_recommendations(self, user_skills: List[str], location: str = "") -> List[Dict]:
        """Get personalized job recommendations"""
        try:
            if self.api_available and self.google_jobs_api:
                return self.google_jobs_api.get_job_recommendations(user_skills, location)
        except Exception as e:
            print(f"Error getting job recommendations: {str(e)}")
          # Fallback to regular search
        skills_query = " ".join(user_skills[:3]) if user_skills else "software developer"
        return self.search_jobs(skills_query, location, limit=10)
    
    def get_trending_jobs(self, location: str = "") -> List[Dict]:
        """Get trending job opportunities"""
        try:
            if self.api_available and self.google_jobs_api:
                return self.google_jobs_api.get_trending_jobs(location)
        except Exception as e:
            print(f"Error getting trending jobs: {str(e)}")
          # Fallback trending searches
        return self._fallback_trending_search(location)
    
    def _fallback_trending_search(self, location: str) -> List[Dict]:
        """AI-powered dynamic trending jobs generation"""
        try:
            # Use AI data service for trending jobs
            trending_jobs = self.ai_data_service.generate_dynamic_jobs(
                keywords="trending technology roles",
                location=location,
                experience_level="",
                job_type="Full-time",
                limit=12
            )
            
            if trending_jobs and len(trending_jobs) > 0:
                # Mark these as trending jobs
                for job in trending_jobs:
                    job['source'] = 'ai_trending'
                    job['trending'] = True
                    job['posted_date'] = 'Today' if len(trending_jobs) > 6 else '1 day ago'
                
                print(f"✅ Generated {len(trending_jobs)} AI-powered trending jobs")
                return trending_jobs
            else:
                return self._minimal_trending_fallback(location)
                
        except Exception as e:
            print(f"⚠️ AI trending jobs generation failed: {e}")
            return self._minimal_trending_fallback(location)
    
    def _minimal_trending_fallback(self, location: str) -> List[Dict]:
        """Minimal trending jobs fallback"""
        return [
            {
                'title': 'AI/ML Engineer - High Demand',
                'company': 'Tech Innovators Inc',
                'location': location or 'Remote',
                'description': 'Join the AI revolution! Work on cutting-edge machine learning solutions.',
                'employment_type': 'FULL_TIME',
                'posted_date': 'Today',
                'url': '#',
                'salary': 'Competitive - Above Market Rate',
                'requirements': ['Machine Learning experience', 'Python proficiency'],
                'skills': ['Python', 'TensorFlow', 'PyTorch', 'AI/ML'],                'source': 'minimal_trending',
                'trending': True
            }
        ]
    
    def get_salary_insights(self, job_title: str, location: str = "") -> Dict:
        """Get salary insights for a job title and location"""
        try:
            if self.api_available and self.google_jobs_api:
                return self.google_jobs_api.get_salary_insights(job_title, location)
        except Exception as e:
            print(f"Error getting salary insights: {str(e)}")
        
        return self._fallback_salary_insights(job_title, location)
    
    def _fallback_salary_insights(self, job_title: str, location: str) -> Dict:
        """Fallback salary insights"""
        base_salaries = {
            'software engineer': 110000,
            'data scientist': 120000,
            'product manager': 135000,
            'devops engineer': 115000,
            'frontend developer': 95000,
            'backend developer': 105000
        }
        
        base_salary = 95000  # default
        for title, salary in base_salaries.items():
            if title in job_title.lower():
                base_salary = salary
                break
        
        # Location adjustments
        location_multipliers = {
            'san francisco': 1.4, 'new york': 1.3, 'seattle': 1.2,
            'boston': 1.15, 'austin': 1.1, 'remote': 1.0
        }
        
        multiplier = 1.0
        for loc, mult in location_multipliers.items():
            if loc in location.lower():
                multiplier = mult
                break
        
        adjusted_salary = int(base_salary * multiplier)
        
        return {
            'median_salary': adjusted_salary,
            'min_salary': int(adjusted_salary * 0.7),
            'max_salary': int(adjusted_salary * 1.4),
            'sample_size': 50,            'job_title': job_title,
            'location': location or 'All locations'
        }
    
    def _fallback_search(self, keywords: str, location: str, experience_level: str, job_type: str, limit: int) -> List[Dict]:
        """Enhanced AI-powered fallback job search"""
        try:
            # Use AI data service for dynamic job generation
            ai_jobs = self.ai_data_service.generate_dynamic_jobs(
                keywords=keywords,
                location=location,
                experience_level=experience_level,
                job_type=job_type,
                limit=limit
            )
            
            if ai_jobs and len(ai_jobs) > 0:
                print(f"✅ Generated {len(ai_jobs)} AI-powered job listings")
                return ai_jobs
            else:
                print("⚠️ AI job generation returned empty, using minimal fallback")
                return self._minimal_hardcoded_fallback(keywords, location, limit)
                
        except Exception as e:
            print(f"⚠️ AI job generation failed: {e}, using minimal fallback")
            return self._minimal_hardcoded_fallback(keywords, location, limit)
    
    def _minimal_hardcoded_fallback(self, keywords: str, location: str, limit: int) -> List[Dict]:
        """Minimal hardcoded fallback when all AI systems fail"""
        companies = ["TechFlow Solutions", "DataDrive Inc", "CloudNext Corp", "InnovateLabs"]
        locations = ["Remote", "San Francisco, CA", "New York, NY", "Seattle, WA"]
        
        jobs = []
        for i in range(min(limit, 8)):
            jobs.append({
                'id': f'minimal_fallback_{i}',
                'title': f"{keywords} Developer" if keywords else "Software Developer",
                'company': companies[i % len(companies)],
                'company_industry': 'Technology',
                'company_size': 'Medium',
                'location': location or locations[i % len(locations)],
                'description': f'Work on innovative {keywords} solutions in a collaborative environment.',
                'employment_type': 'Full-time',
                'experience_level': 'Mid Level',
                'posted_date': f'{(i % 7) + 1} days ago',
                'url': '#',
                'application_url': '#',
                'salary_range': '$90,000 - $130,000',
                'requirements': [f'{keywords} experience', 'Problem-solving skills', 'Team collaboration'],
                'skills': [keywords or 'Programming', 'Git', 'Agile'],
                'benefits': ['Health insurance', 'Remote work', 'Professional development'],
                'remote_type': 'Remote' if i % 2 == 0 else 'On-site',                'source': 'minimal_fallback',
                'ai_match_score': 80
            })
        return jobs
    
    def _get_recent_date(self, days_ago: int) -> str:
        from datetime import datetime, timedelta
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime('%Y-%m-%d')
    
    def _generate_relevant_skills(self, keywords: str) -> List[str]:
        skill_mapping = {
            'python': ['Python', 'Django', 'Flask', 'FastAPI', 'NumPy', 'Pandas'],
            'javascript': ['JavaScript', 'React', 'Node.js', 'TypeScript', 'Vue.js', 'Angular'],
            'data': ['Python', 'SQL', 'Machine Learning', 'Tableau', 'Power BI', 'Statistics'],
            'machine learning': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Statistics', 'Deep Learning'],
            'frontend': ['React', 'JavaScript', 'CSS', 'HTML', 'TypeScript', 'Responsive Design'],
            'backend': ['Python', 'Java', 'Node.js', 'PostgreSQL', 'MongoDB', 'API Development'],
            'devops': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Terraform', 'Linux'],
            'product': ['Product Strategy', 'User Research', 'Analytics', 'A/B Testing', 'Roadmapping', 'Agile']
        }
        
        keywords_lower = keywords.lower()
        for key, skills in skill_mapping.items():
            if key in keywords_lower:
                return skills[:4]  
        
        return ['Problem Solving', 'Team Collaboration', 'Communication', 'Leadership']
    
    def _generate_benefits(self) -> List[str]:
        """Generate realistic job benefits"""
        all_benefits = [
            'Health, dental, and vision insurance',
            'Unlimited PTO',
            '401(k) with company matching',
            'Remote work flexibility',
            'Professional development budget',
            'Stock options/equity',
            'Flexible working hours',
            'Home office stipend',
            'Gym membership reimbursement',
            'Mental health support',
            'Parental leave',
            'Learning and development opportunities'
        ]
        
        import random
        return random.sample(all_benefits, 6)
    
    def _generate_requirements(self, keywords: str, experience_level: str) -> List[str]:
        base_requirements = [
            f'Experience with {keywords}',
            'Strong problem-solving skills',
            'Excellent communication abilities',
            'Team collaboration experience'
        ]
        
        experience_requirements = {
            'Entry Level (0-2 years)': ['Bachelor\'s degree or equivalent', 'Willingness to learn'],
            'Mid Level (3-5 years)': ['3-5 years of relevant experience', 'Proven track record'],            'Senior Level (6-10 years)': ['6+ years of experience', 'Leadership experience', 'Mentoring capabilities'],
            'Executive (10+ years)': ['10+ years of experience', 'Strategic thinking', 'Team management', 'P&L responsibility']
        }
        
        requirements = base_requirements + experience_requirements.get(experience_level, [])
        return requirements
    
    def get_job_details(self, job_id: str) -> Optional[Dict]:
        """Get detailed information about a specific job"""
        try:
            if self.api_available and self.google_jobs_api:
                return self.google_jobs_api.get_job_details(job_id)
        except Exception as e:
            print(f"Error fetching job details: {str(e)}")
        
        return None
    
    def get_company_insights(self, company_name: str) -> Dict:
        """Get insights about a company"""
        try:
            # Search for jobs at the company to gather insights
            if self.api_available and self.google_jobs_api:
                company_jobs = self.google_jobs_api.search_jobs_by_company([company_name])
                
                if company_jobs:
                    # Aggregate insights from job postings
                    total_jobs = len(company_jobs)
                    common_skills = self._extract_common_skills(company_jobs)
                    salary_range = self._estimate_company_salary_range(company_jobs)
                    
                    return {
                        'name': company_name,
                        'open_positions': total_jobs,
                        'common_skills': common_skills,
                        'salary_range': salary_range,
                        'locations': list(set([job.get('location', '') for job in company_jobs])),
                        'remote_friendly': any(job.get('remote_type') for job in company_jobs),
                        'data_source': 'google_talent_api'
                    }
        except Exception as e:
            print(f"Error fetching company insights: {str(e)}")
        
        # Fallback company insights
        return {
            'name': company_name,
            'industry': 'Technology',
            'size': 'Medium',
            'description': f'{company_name} is an innovative company focused on growth and excellence.',
            'linkedin_url': f'https://www.linkedin.com/company/{company_name.lower().replace(" ", "-")}',
            'founded_year': 2010,
            'headquarters': 'San Francisco, CA',
            'data_source': 'estimated'
        }
    
    def _extract_common_skills(self, jobs: List[Dict]) -> List[str]:
        """Extract most common skills from job listings"""
        skill_counts = {}
        
        for job in jobs:
            skills = job.get('skills', [])
            for skill in skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Return top 10 most common skills
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return [skill for skill, count in sorted_skills[:10]]
    
    def _estimate_company_salary_range(self, jobs: List[Dict]) -> Dict:
        """Estimate salary range for a company based on job postings"""
        salaries = []
        
        for job in jobs:
            salary_str = job.get('salary', '')
            if salary_str and 'competitive' not in salary_str.lower():
                # Extract salary numbers
                salary_numbers = self._extract_salary_numbers_basic(salary_str)
                salaries.extend(salary_numbers)
        
        if salaries:
            return {
                'min': min(salaries),
                'max': max(salaries),
                'average': sum(salaries) // len(salaries)
            }
        
        return {'min': 70000, 'max': 150000, 'average': 110000}
    
    def _extract_salary_numbers_basic(self, salary_str: str) -> List[int]:
        """Basic salary number extraction"""
        import re
        numbers = re.findall(r'\d{4,6}', salary_str)
        
        salary_values = []
        for num_str in numbers:
            try:
                num = int(num_str)
                if 30000 <= num <= 500000:
                    salary_values.append(num)
            except ValueError:
                continue
        
        return salary_values
    
    def validate_google_jobs_access(self) -> bool:
        """Validate Google Cloud Talent Solution API access"""
        return self.api_available
    
    def get_salary_insights(self, job_title: str, location: str = "") -> Dict:
        try:
            # Google Jobs API doesn't provide direct salary insights
            # Return enhanced fallback data based on market research
            pass
        except Exception as e:
            print(f"Error fetching salary insights: {str(e)}")
            
        # Enhanced salary data based on current market trends
        base_salaries = {
            'software engineer': {'min': 85000, 'max': 150000, 'median': 115000},
            'data scientist': {'min': 95000, 'max': 170000, 'median': 130000},
            'product manager': {'min': 100000, 'max': 180000, 'median': 140000},
            'marketing manager': {'min': 70000, 'max': 130000, 'median': 95000},
            'sales manager': {'min': 65000, 'max': 140000, 'median': 100000},
            'devops engineer': {'min': 90000, 'max': 160000, 'median': 125000},
            'frontend developer': {'min': 75000, 'max': 140000, 'median': 105000},
            'backend developer': {'min': 80000, 'max': 150000, 'median': 115000}
        }
        
        # Location multipliers for salary adjustment
        location_multipliers = {
            'san francisco': 1.4, 'new york': 1.3, 'seattle': 1.2,
            'boston': 1.15, 'austin': 1.05, 'remote': 1.0
        }
        
        job_key = job_title.lower()
        location_key = location.lower() if location else 'remote'
        
        base_data = base_salaries.get(job_key, base_salaries['software engineer'])
        multiplier = location_multipliers.get(location_key, 1.0)
        
        return {
            'job_title': job_title,
            'location': location,
            'min_salary': int(base_data['min'] * multiplier),
            'max_salary': int(base_data['max'] * multiplier),
            'median_salary': int(base_data['median'] * multiplier),
            'currency': 'USD'
        }
    
    def get_trending_skills(self, industry: str = "") -> List[str]:
        try:
            # Enhanced trending skills based on current market demands
            skill_trends = {
                'technology': [
                    'Artificial Intelligence', 'Machine Learning', 'Cloud Computing',
                    'Cybersecurity', 'Data Science', 'DevOps', 'Kubernetes', 'React',
                    'Python', 'Blockchain', 'IoT', 'Microservices'
                ],
                'data': [
                    'Python', 'SQL', 'Machine Learning', 'Tableau', 'Power BI',
                    'Statistics', 'Deep Learning', 'Apache Spark', 'TensorFlow', 'PyTorch'
                ],
                'marketing': [
                    'Digital Marketing', 'Content Strategy', 'Social Media Marketing',                    'SEO/SEM', 'Marketing Analytics', 'Growth Hacking', 'Email Marketing'
                ],
                'finance': [
                    'Financial Analysis', 'Risk Management', 'Fintech', 'Cryptocurrency',
                    'ESG Investing', 'Robo-Advisory', 'Regulatory Compliance'
                ]
            }
            
            industry_key = industry.lower() if industry else 'technology'
            return skill_trends.get(industry_key, skill_trends['technology'])
        except Exception as e:
            print(f"Error fetching trending skills: {str(e)}")
            return ['AI/Machine Learning', 'Cloud Computing', 'Data Analysis', 'Leadership']
    
    def get_job_alerts(self, user_profile: Dict, preferences: Dict) -> List[Dict]:
        skills = user_profile.get('skills', [])
        location = preferences.get('location', '')
        experience_level = preferences.get('experience_level', '')
        
        alerts = []
        
        for skill in skills[:3]:
            try:
                jobs = self.search_jobs(
                    keywords=skill, 
                    location=location,
                    experience_level=experience_level,
                    limit=5
                )
                alerts.extend(jobs)
            except Exception as e:
                print(f"Error getting alerts for skill {skill}: {str(e)}")
        
        seen_jobs = set()
        unique_alerts = []
        for job in alerts:
            job_key = f"{job['title']}_{job['company']}"
            if job_key not in seen_jobs:
                seen_jobs.add(job_key)
                unique_alerts.append(job)
        
        return unique_alerts[:10]
    
    def get_trending_skills(self, industry: str = "") -> List[str]:
        """Get trending skills in the industry"""
        try:
            if self.api_available and self.google_jobs_api:
                trending_jobs = self.google_jobs_api.get_trending_jobs()
                return self._extract_common_skills(trending_jobs)
        except Exception as e:
            print(f"Error getting trending skills: {str(e)}")
        
        # Fallback trending skills
        default_skills = [
            "Python", "JavaScript", "React", "AWS", "Docker", "Kubernetes",
            "Machine Learning", "Node.js", "TypeScript", "GraphQL",
            "Microservices", "CI/CD", "Agile", "SQL", "NoSQL"
        ]
        
        return default_skills[:10]
    
    def get_job_alerts(self, user_profile: Dict, preferences: Dict) -> List[Dict]:
        """Get personalized job alerts based on user profile and preferences"""
        try:
            skills = user_profile.get('skills', [])
            location = preferences.get('location', '')
            
            if self.api_available and self.google_jobs_api:
                recommended_jobs = self.google_jobs_api.get_job_recommendations(skills, location)
                
                # Filter based on preferences
                filtered_jobs = []
                for job in recommended_jobs:
                    if self._matches_preferences(job, preferences):
                        job['alert_type'] = 'recommendation'
                        job['match_reason'] = self._get_match_reason(job, user_profile)
                        filtered_jobs.append(job)
                
                return filtered_jobs[:5]  # Return top 5 alerts
        except Exception as e:
            print(f"Error getting job alerts: {str(e)}")
        
        return []
    
    def _matches_preferences(self, job: Dict, preferences: Dict) -> bool:
        """Check if job matches user preferences"""
        # Check salary expectations
        expected_salary = preferences.get('salary_min', 0)
        if expected_salary > 0:
            job_salary = self._estimate_job_salary(job.get('salary', ''))
            if job_salary > 0 and job_salary < expected_salary:
                return False
        
        # Check remote work preference
        if preferences.get('remote_only', False):
            if not job.get('remote_type'):
                return False
        
        # Check employment type
        preferred_types = preferences.get('employment_types', [])
        if preferred_types and job.get('employment_type') not in preferred_types:
            return False
        
        return True
    
    def _estimate_job_salary(self, salary_str: str) -> int:
        """Estimate numeric salary from salary string"""
        if not salary_str or 'competitive' in salary_str.lower():
            return 0
        
        numbers = self._extract_salary_numbers_basic(salary_str)
        return max(numbers) if numbers else 0
    
    def _get_match_reason(self, job: Dict, user_profile: Dict) -> str:
        """Get reason why job matches user profile"""
        user_skills = set(skill.lower() for skill in user_profile.get('skills', []))
        job_skills = set(skill.lower() for skill in job.get('skills', []))
        
        common_skills = user_skills.intersection(job_skills)
        
        if common_skills:
            return f"Matches your skills: {', '.join(list(common_skills)[:3])}"
        
        if user_profile.get('title', '').lower() in job.get('title', '').lower():
            return "Matches your job title"
        
        return "Recommended based on your profile"
    
    def validate_google_jobs_access(self) -> bool:
        """Validate Google Cloud Talent Solution API access"""
        return self.api_available
    
    def _enhance_job_with_insights(self, job: Dict, keywords: str) -> Dict:
        """Enhance job posting with AI insights and matching scores"""
        import random
        
        # Add AI match score based on keywords and job content
        title_match = len(set(keywords.lower().split()) & set(job.get('title', '').lower().split()))
        skills_match = len(set(keywords.lower().split()) & set(' '.join(job.get('skills', [])).lower().split()))
        
        base_score = 70 + (title_match * 5) + (skills_match * 3)
        job['ai_match_score'] = min(98, base_score + random.randint(-5, 10))
        
        # Add market insights
        job['market_insights'] = {
            'demand_level': random.choice(['High', 'Very High', 'Growing']),
            'salary_competitiveness': random.choice(['Above Average', 'Competitive', 'Excellent']),
            'growth_potential': random.choice(['Strong', 'Excellent', 'High'])
        }
        
        # Add application tips
        job['application_tips'] = [
            f"Highlight your {keywords} experience",
            "Showcase relevant project portfolio",
            "Demonstrate problem-solving skills"
        ]
        
        return job