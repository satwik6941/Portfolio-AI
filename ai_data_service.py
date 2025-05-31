import json
import random
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from groq_service import GroqLLM

class AIDataService:
    """AI-powered dynamic data generation service to replace hardcoded fallbacks"""
    
    def __init__(self, api_key: str = None):
        load_dotenv()
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY is required for AIDataService")
        
        self.groq_service = GroqLLM(api_key)
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
        
    def generate_dynamic_jobs(self, keywords: str, location: str = "", 
                            experience_level: str = "", job_type: str = "Full-time", 
                            limit: int = 20) -> List[Dict]:
        """Generate dynamic, AI-powered job listings"""
        cache_key = f"jobs_{keywords}_{location}_{experience_level}_{job_type}_{limit}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            prompt = f"""
            Generate {limit} realistic, current job opportunities in JSON format based on these criteria:
            - Keywords: {keywords}
            - Location: {location or 'various locations including remote'}
            - Experience Level: {experience_level or 'various levels'}
            - Job Type: {job_type}
            
            Create diverse, realistic job postings that reflect current market trends. Each job should include:
            
            1. Job title that incorporates the keywords naturally
            2. Realistic company name (mix of well-known and emerging companies)
            3. Location (use provided location or distribute across major tech hubs + remote options)
            4. Compelling job description (2-3 sentences highlighting growth and impact)
            5. Employment type matching the request
            6. Recent posting date (Today to 2 weeks ago)
            7. Competitive salary reflecting current market rates
            8. 3-5 realistic requirements based on experience level
            9. 4-8 relevant technical skills
            10. Benefits package (3-6 realistic benefits)
            11. Company size and industry
            12. Remote work options when applicable
            
            Focus on in-demand roles and current technology trends. Vary the companies, locations, and requirements.
            
            Return ONLY a JSON array with this exact structure:
            [
                {{
                    "id": "unique_job_id",
                    "title": "Job Title",
                    "company": "Company Name",
                    "company_industry": "Industry",
                    "company_size": "Startup/Small/Medium/Large",
                    "location": "City, State or Remote",
                    "description": "Compelling job description...",
                    "employment_type": "Full-time/Part-time/Contract/Internship",
                    "experience_level": "Entry/Mid/Senior/Executive",
                    "posted_date": "Time ago",
                    "url": "#",
                    "application_url": "https://example.com/apply",
                    "salary_range": "$XXX,XXX - $XXX,XXX",
                    "requirements": ["requirement1", "requirement2", "requirement3"],
                    "skills": ["skill1", "skill2", "skill3", "skill4"],
                    "benefits": ["benefit1", "benefit2", "benefit3"],
                    "remote_type": "Remote/Hybrid/On-site",
                    "source": "ai_generated",
                    "ai_match_score": 85
                }}
            ]
            """
            
            response = self.groq_service.chat_completion(prompt)
            jobs = self._parse_ai_response(response)
            
            if jobs:
                # Cache the result
                self.cache[cache_key] = {
                    'data': jobs,
                    'timestamp': datetime.now().timestamp()
                }
                return jobs
            else:
                return self._generate_minimal_fallback_jobs(keywords, location, limit)
                
        except Exception as e:
            print(f"Error generating AI jobs: {e}")
            return self._generate_minimal_fallback_jobs(keywords, location, limit)
    
    def generate_dynamic_salary_insights(self, job_title: str, location: str = "") -> Dict:
        """Generate AI-powered salary insights"""
        cache_key = f"salary_{job_title}_{location}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            prompt = f"""
            Provide realistic salary insights for "{job_title}" in "{location or 'United States'}" in JSON format.
            
            Consider current market trends, experience levels, and location factors.
            Research current industry standards and provide competitive ranges.
            
            Return ONLY a JSON object with this structure:
            {{
                "job_title": "{job_title}",
                "location": "{location or 'All locations'}",
                "entry_level": {{
                    "min_salary": 65000,
                    "max_salary": 85000,
                    "median_salary": 75000
                }},
                "mid_level": {{
                    "min_salary": 85000,
                    "max_salary": 120000,
                    "median_salary": 100000
                }},
                "senior_level": {{
                    "min_salary": 120000,
                    "max_salary": 180000,
                    "median_salary": 150000
                }},
                "factors": [
                    "Location premium/discount",
                    "Industry demand",
                    "Skill requirements"
                ],
                "trending_skills": ["skill1", "skill2", "skill3"],
                "market_outlook": "Growing/Stable/Declining",
                "note": "Current market estimate based on industry data"
            }}
            """
            
            response = self.groq_service.chat_completion(prompt)
            salary_data = self._parse_ai_response(response, expect_list=False)
            
            if salary_data:
                self.cache[cache_key] = {
                    'data': salary_data,
                    'timestamp': datetime.now().timestamp()
                }
                return salary_data
            else:
                return self._generate_fallback_salary_data(job_title, location)
                
        except Exception as e:
            print(f"Error generating AI salary insights: {e}")
            return self._generate_fallback_salary_data(job_title, location)
    
    def generate_trending_skills(self, industry: str = "", keywords: str = "") -> List[str]:
        """Generate AI-powered trending skills"""
        cache_key = f"skills_{industry}_{keywords}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            prompt = f"""
            List the top 15 trending and in-demand technical skills for {industry or 'technology'} industry in 2024.
            {f"Focus on skills related to: {keywords}" if keywords else ""}
            
            Include a mix of:
            - Programming languages
            - Frameworks and libraries
            - Cloud and DevOps tools
            - Emerging technologies
            - Industry-specific skills
            
            Return ONLY a JSON array of skill names:
            ["skill1", "skill2", "skill3", ...]
            """
            
            response = self.groq_service.chat_completion(prompt)
            skills = self._parse_ai_response(response)
            
            if skills and isinstance(skills, list):
                self.cache[cache_key] = {
                    'data': skills,
                    'timestamp': datetime.now().timestamp()
                }
                return skills[:15]
            else:
                return self._get_fallback_skills(keywords)
                
        except Exception as e:
            print(f"Error generating trending skills: {e}")
            return self._get_fallback_skills(keywords)
    
    def generate_company_insights(self, company_name: str) -> Dict:
        """Generate AI-powered company insights"""
        cache_key = f"company_{company_name}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            prompt = f"""
            Generate realistic company insights for "{company_name}" in JSON format.
            
            If this is a real company, provide accurate information. If fictional, create realistic details.
            
            Return ONLY a JSON object:
            {{
                "company_name": "{company_name}",
                "industry": "Primary industry",
                "size": "Startup/Small/Medium/Large/Enterprise",
                "founded_year": 2010,
                "location": "Primary location",
                "culture": ["value1", "value2", "value3"],
                "benefits": ["benefit1", "benefit2", "benefit3"],
                "tech_stack": ["tech1", "tech2", "tech3"],
                "growth_stage": "Growing/Mature/Scaling",
                "rating": 4.2,
                "notable_for": "What the company is known for"
            }}
            """
            
            response = self.groq_service.chat_completion(prompt)
            company_data = self._parse_ai_response(response, expect_list=False)
            
            if company_data:
                self.cache[cache_key] = {
                    'data': company_data,
                    'timestamp': datetime.now().timestamp()
                }
                return company_data
            else:
                return self._generate_fallback_company_data(company_name)
                
        except Exception as e:
            print(f"Error generating company insights: {e}")
            return self._generate_fallback_company_data(company_name)
    
    def generate_market_trends(self, industry: str = "technology") -> Dict:
        """Generate AI-powered market trends and insights"""
        cache_key = f"trends_{industry}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            prompt = f"""
            Generate current market trends and insights for the {industry} industry in JSON format.
            
            Return ONLY a JSON object:
            {{
                "industry": "{industry}",
                "hot_roles": ["role1", "role2", "role3"],
                "emerging_skills": ["skill1", "skill2", "skill3"],
                "salary_trends": "Increasing/Stable/Decreasing",
                "remote_work_trend": "High/Medium/Low adoption",
                "hiring_outlook": "Strong/Moderate/Cautious",
                "key_trends": [
                    "Trend description 1",
                    "Trend description 2",
                    "Trend description 3"
                ],
                "growth_areas": ["area1", "area2", "area3"],
                "competitive_factors": ["factor1", "factor2"]
            }}
            """
            
            response = self.groq_service.chat_completion(prompt)
            trends_data = self._parse_ai_response(response, expect_list=False)
            
            if trends_data:
                self.cache[cache_key] = {
                    'data': trends_data,
                    'timestamp': datetime.now().timestamp()
                }
                return trends_data
            else:
                return self._generate_fallback_trends()
                
        except Exception as e:
            print(f"Error generating market trends: {e}")
            return self._generate_fallback_trends()
    
    def _parse_ai_response(self, response: str, expect_list: bool = True) -> Any:
        """Parse AI response and extract JSON"""
        try:
            # Clean the response
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            elif clean_response.startswith('```'):
                clean_response = clean_response[3:]
            
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            
            clean_response = clean_response.strip()
            
            # Parse JSON
            data = json.loads(clean_response)
            
            # Validate structure
            if expect_list and not isinstance(data, list):
                return None
            elif not expect_list and not isinstance(data, dict):
                return None
                
            return data
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing AI response: {e}")
            return None
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return (datetime.now().timestamp() - cache_time) < self.cache_duration
    
    def _generate_minimal_fallback_jobs(self, keywords: str, location: str, limit: int) -> List[Dict]:
        """Minimal fallback when AI fails completely"""
        companies = [
            "TechFlow Solutions", "DataDrive Inc", "CloudNext Corp", 
            "InnovateLabs", "CodeCraft Systems", "Digital Dynamics",
            "FutureTech Inc", "AgileWorks", "SmartSolutions Co"
        ]
        
        jobs = []
        for i in range(min(limit, 10)):
            company = companies[i % len(companies)]
            jobs.append({
                'id': f'fallback_{i}',
                'title': f"{keywords} Developer" if keywords else "Software Developer",
                'company': company,
                'company_industry': 'Technology',
                'company_size': random.choice(['Small', 'Medium', 'Large']),
                'location': location or 'Remote',
                'description': f'Join {company} to work on innovative {keywords} solutions.',
                'employment_type': 'Full-time',
                'experience_level': random.choice(['Entry', 'Mid', 'Senior']),
                'posted_date': f'{random.randint(1, 7)} days ago',
                'url': '#',
                'application_url': f'https://careers.{company.lower().replace(" ", "")}.com',
                'salary_range': '$80,000 - $120,000',
                'requirements': [f'{keywords} experience', 'Problem-solving skills', 'Team collaboration'],
                'skills': [keywords, 'Git', 'Agile', 'Problem Solving'] if keywords else ['Python', 'JavaScript', 'Git', 'Agile'],
                'benefits': ['Health insurance', 'Remote work', 'Professional development'],
                'remote_type': 'Remote' if i % 3 == 0 else 'On-site',
                'source': 'ai_fallback',
                'ai_match_score': random.randint(75, 95)
            })
        
        return jobs
    
    def _generate_fallback_salary_data(self, job_title: str, location: str) -> Dict:
        """Fallback salary data when AI fails"""
        base_salary = 95000
        
        # Simple title-based adjustments
        if 'senior' in job_title.lower() or 'lead' in job_title.lower():
            base_salary = 130000
        elif 'junior' in job_title.lower() or 'entry' in job_title.lower():
            base_salary = 70000
        elif 'data scientist' in job_title.lower():
            base_salary = 115000
        elif 'manager' in job_title.lower():
            base_salary = 140000
        
        return {
            'job_title': job_title,
            'location': location or 'All locations',
            'entry_level': {
                'min_salary': int(base_salary * 0.6),
                'max_salary': int(base_salary * 0.8),
                'median_salary': int(base_salary * 0.7)
            },
            'mid_level': {
                'min_salary': int(base_salary * 0.8),
                'max_salary': int(base_salary * 1.2),
                'median_salary': base_salary
            },
            'senior_level': {
                'min_salary': int(base_salary * 1.2),
                'max_salary': int(base_salary * 1.8),
                'median_salary': int(base_salary * 1.5)
            },
            'factors': ['Experience level', 'Location', 'Company size'],
            'trending_skills': ['Python', 'Cloud', 'AI/ML', 'DevOps'],
            'market_outlook': 'Growing',
            'note': 'Fallback estimate'
        }
    
    def _get_fallback_skills(self, keywords: str) -> List[str]:
        """Fallback skills when AI fails"""
        base_skills = [
            'Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker',
            'Kubernetes', 'Git', 'SQL', 'MongoDB', 'TypeScript', 'Vue.js',
            'Machine Learning', 'Data Analysis', 'DevOps'
        ]
        
        if keywords:
            # Add keywords-related skills
            if 'data' in keywords.lower():
                base_skills.extend(['Pandas', 'NumPy', 'TensorFlow', 'Jupyter'])
            elif 'web' in keywords.lower():
                base_skills.extend(['HTML', 'CSS', 'Bootstrap', 'REST APIs'])
            elif 'mobile' in keywords.lower():
                base_skills.extend(['React Native', 'Flutter', 'Swift', 'Kotlin'])
        
        return base_skills[:15]
    
    def _generate_fallback_company_data(self, company_name: str) -> Dict:
        """Fallback company data when AI fails"""
        return {
            'company_name': company_name,
            'industry': 'Technology',
            'size': 'Medium',
            'founded_year': 2015,
            'location': 'San Francisco, CA',
            'culture': ['Innovation', 'Collaboration', 'Growth'],
            'benefits': ['Health insurance', 'Remote work', 'Learning budget'],
            'tech_stack': ['Python', 'React', 'AWS'],
            'growth_stage': 'Growing',
            'rating': 4.0,
            'notable_for': 'Innovative technology solutions'
        }
    
    def _generate_fallback_trends(self) -> Dict:
        """Fallback trends when AI fails"""
        return {
            'industry': 'technology',
            'hot_roles': ['AI Engineer', 'DevOps Engineer', 'Full Stack Developer'],
            'emerging_skills': ['AI/ML', 'Cloud Computing', 'Cybersecurity'],
            'salary_trends': 'Increasing',
            'remote_work_trend': 'High adoption',
            'hiring_outlook': 'Strong',
            'key_trends': [
                'AI and machine learning integration',
                'Remote-first work culture',
                'Cloud-native development'
            ],
            'growth_areas': ['AI/ML', 'Cloud', 'Cybersecurity'],
            'competitive_factors': ['Technical skills', 'Experience']
        }
    
    def clear_cache(self):
        """Clear the entire cache"""
        self.cache = {}
    
    def clear_expired_cache(self):
        """Clear only expired cache entries"""
        current_time = datetime.now().timestamp()
        expired_keys = [
            key for key, value in self.cache.items()
            if (current_time - value['timestamp']) > self.cache_duration
        ]
        
        for key in expired_keys:
            del self.cache[key]
