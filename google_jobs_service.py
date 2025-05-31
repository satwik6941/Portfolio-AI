import os
import requests
import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from google.cloud import talent
from google.oauth2 import service_account
import logging
import re
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleJobsService:
    def __init__(self, project_id: str = None, credentials_path: str = None):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CLOUD_CREDENTIALS_PATH')
        self.client = None
        self.parent = None
        
        # Initialize AI data service for fallback
        self.ai_data_service = None
        try:
            import os
            from dotenv import load_dotenv
            from ai_data_service import AIDataService
            load_dotenv()
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                self.ai_data_service = AIDataService(api_key)
                logger.info("✅ AI data service initialized for Google Jobs fallback")
            else:
                logger.warning("⚠️ No GROQ_API_KEY found for AI data service")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize AI data service: {e}")
            self.ai_data_service = None
        
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                self.client = talent.JobServiceClient(credentials=credentials)
                logger.info("Google Cloud Talent Solution API initialized with service account")
            elif self.project_id:
                self.client = talent.JobServiceClient()
                logger.info("Google Cloud Talent Solution API initialized with default credentials")
            
            if self.client and self.project_id:
                self.parent = f"projects/{self.project_id}"
                logger.info(f"Using project: {self.project_id}")
            else:
                logger.warning("Google Cloud Talent Solution API not properly configured")
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Talent Solution API: {str(e)}")
            self.client = None
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10, 
                    employment_types: List[str] = None, experience_levels: List[str] = None) -> List[Dict]:
        try:
            if not self.client or not self.parent:
                logger.warning("Google Cloud Talent Solution API not available, using fallback")
                return self._get_mock_jobs(query, location, limit)
            
            job_query = talent.JobQuery(query=query)
            
            if location and location.strip():
                location_filter = talent.LocationFilter(address=location)
                job_query.location_filters = [location_filter]
            
            if employment_types:
                job_query.employment_types = [
                    getattr(talent.EmploymentType, emp_type, talent.EmploymentType.FULL_TIME)
                    for emp_type in employment_types
                ]
            else:
                job_query.employment_types = [
                    talent.EmploymentType.FULL_TIME,
                    talent.EmploymentType.PART_TIME,
                    talent.EmploymentType.CONTRACT
                ]
            
            request_metadata = talent.RequestMetadata(
                user_id="portfolio_ai_user",
                session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                domain="portfolio-ai.com"
            )
            
            search_request = talent.SearchJobsRequest(
                parent=self.parent,
                request_metadata=request_metadata,
                job_query=job_query,
                page_size=limit,
                order_by="relevance desc",
                enable_broadening=True
            )
            
            response = self.client.search_jobs(request=search_request)
            
            jobs = []
            for result in response.matching_jobs:
                job_data = self._parse_job_result(result.job)
                jobs.append(job_data)
            
            logger.info(f"Found {len(jobs)} jobs from Google Cloud Talent Solution API")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching jobs with Google Cloud Talent Solution API: {str(e)}")
            return self._get_mock_jobs(query, location, limit)
    
    def _parse_job_result(self, job: talent.Job) -> Dict:
        try:
            job_data = {
                'title': job.title or 'Software Developer',
                'company': job.company_display_name or 'Tech Company',
                'location': self._extract_job_location(job.addresses),
                'description': job.description or 'Exciting opportunity in software development',
                'employment_type': self._convert_employment_type(job.employment_types[0] if job.employment_types else None),
                'posted_date': self._parse_posting_date(job.posting_create_time),
                'url': self._extract_application_url(job.application_info),
                'salary': self._extract_job_salary(job.compensation_info),
                'requirements': self._extract_job_requirements(job.qualifications),
                'skills': self._extract_job_skills(job.description or ''),
                'source': 'google_talent_api',
                'job_id': job.name.split('/')[-1] if job.name else '',
                'company_size': self._estimate_company_size(job.company_display_name),
                'remote_type': self._detect_remote_work(job.description or '', job.addresses)
            }
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error parsing job result: {str(e)}")
            return self._create_fallback_job_data()
    
    def _extract_job_location(self, addresses: List[str]) -> str:
        if addresses:
            return addresses[0]
        return "Remote"
    
    def _convert_employment_type(self, employment_type) -> str:
        type_mapping = {
            talent.EmploymentType.FULL_TIME: 'Full-time',
            talent.EmploymentType.PART_TIME: 'Part-time',
            talent.EmploymentType.CONTRACT: 'Contract',
            talent.EmploymentType.TEMPORARY: 'Temporary',
            talent.EmploymentType.INTERN: 'Internship'
        }
        return type_mapping.get(employment_type, 'Full-time')
    
    def _parse_posting_date(self, posting_time) -> str:
        if not posting_time:
            return "Recently"
        
        try:
            post_date = posting_time.ToDatetime() if hasattr(posting_time, 'ToDatetime') else datetime.now()
            days_ago = (datetime.now() - post_date).days
            
            if days_ago == 0:
                return "Today"
            elif days_ago == 1:
                return "Yesterday"
            elif days_ago < 7:
                return f"{days_ago} days ago"
            else:
                return post_date.strftime("%B %d, %Y")
        except:
            return "Recently"
    
    def _extract_application_url(self, application_info) -> str:
        if application_info and hasattr(application_info, 'uris') and application_info.uris:
            return application_info.uris[0]
        return '#'
    
    def _extract_job_salary(self, compensation_info) -> str:
        if not compensation_info:
            return "Competitive salary"
        
        try:
            if hasattr(compensation_info, 'entries') and compensation_info.entries:
                entry = compensation_info.entries[0]
                if hasattr(entry, 'amount') and entry.amount:
                    amount = entry.amount
                    currency = getattr(amount, 'currency_code', 'USD')
                    
                    if hasattr(amount, 'units'):
                        return f"{currency} {amount.units:,}"
                    elif hasattr(entry, 'range') and entry.range:
                        range_info = entry.range
                        min_amount = getattr(range_info.min, 'units', 0) if hasattr(range_info, 'min') else 0
                        max_amount = getattr(range_info.max, 'units', 0) if hasattr(range_info, 'max') else 0
                        return f"{currency} {min_amount:,} - {max_amount:,}"
            
            return "Competitive salary"
        except Exception as e:
            logger.error(f"Error extracting salary: {str(e)}")
            return "Competitive salary"
    
    def _extract_job_requirements(self, qualifications) -> List[str]:
        requirements = []
        
        try:
            if qualifications:
                if hasattr(qualifications, 'education_levels') and qualifications.education_levels:
                    education_level = qualifications.education_levels[0]
                    requirements.append(f"Education: {education_level}")
                
                if hasattr(qualifications, 'experience_in_months') and qualifications.experience_in_months:
                    years = qualifications.experience_in_months // 12
                    requirements.append(f"{years}+ years experience")
            
            if not requirements:
                requirements = [
                    "Bachelor's degree in relevant field",
                    "Strong problem-solving skills",
                    "Team collaboration experience"
                ]
            
            return requirements
        except Exception as e:
            logger.error(f"Error extracting requirements: {str(e)}")
            return ["Bachelor's degree in relevant field", "Strong problem-solving skills"]
    
    def _extract_job_skills(self, description: str) -> List[str]:
        common_skills = [
            'Python', 'JavaScript', 'Java', 'React', 'Node.js', 'SQL', 'AWS',
            'Docker', 'Kubernetes', 'Git', 'Agile', 'Scrum', 'REST API',
            'Machine Learning', 'Data Analysis', 'Cloud Computing', 'TypeScript',
            'Angular', 'Vue.js', 'MongoDB', 'PostgreSQL', 'Redis', 'GraphQL',
            'Microservices', 'DevOps', 'CI/CD', 'Jenkins', 'Terraform'
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:8]
    
    def _estimate_company_size(self, company_name: str) -> str:
        large_companies = ['google', 'microsoft', 'amazon', 'apple', 'facebook', 'meta', 'netflix', 'tesla']
        if any(large_comp in company_name.lower() for large_comp in large_companies):
            return "Enterprise (5000+)"
        return "Medium (201-1000)"
    
    def _detect_remote_work(self, description: str, addresses: List[str]) -> Optional[str]:
        remote_keywords = ['remote', 'work from home', 'telecommute', 'distributed']
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in remote_keywords):
            return "Remote-friendly"
        
        if not addresses or any('remote' in addr.lower() for addr in addresses):
            return "Remote-friendly"
        return None
    
    def _create_fallback_job_data(self) -> Dict:
        # Instead of hardcoded fallback, return None to indicate failure
        # This will prompt the system to use AI-generated opportunities instead
        return None
    
    def _get_mock_jobs(self, query: str, location: str, limit: int) -> List[Dict]:
        """Enhanced fallback method using AI-powered job generation"""
        try:
            # Try AI-powered job generation first
            if self.ai_data_service:
                logger.info("🤖 Using AI data service for dynamic job generation")
                ai_jobs = self.ai_data_service.generate_dynamic_jobs(
                    query=query or "software developer",
                    location=location or "Remote",
                    count=limit
                )
                if ai_jobs:
                    return ai_jobs
        except Exception as e:
            logger.warning(f"AI job generation failed: {e}")
        
        # Minimal static fallback for complete AI failure
        logger.info("⚡ Using minimal static fallback jobs")
        return self._get_minimal_fallback_jobs(query, location, limit)
    
    def _get_minimal_fallback_jobs(self, query: str, location: str, limit: int) -> List[Dict]:
        """Minimal static fallback for complete system failure"""
        basic_jobs = [
            {
                'title': 'Software Developer',
                'company': 'Tech Company',
                'location': location or 'Remote',
                'description': 'Exciting software development opportunity',
                'employment_type': 'FULL_TIME',
                'posted_date': 'Recently',
                'url': '#',
                'salary': 'Competitive',
                'requirements': ['Programming experience'],
                'skills': ['Programming', 'Problem Solving'],
                'source': 'google_jobs_api',
                'ai_generated': False
            }
        ]
        return basic_jobs[:limit]

    def get_job_recommendations(self, user_skills: List[str], location: str = "", experience_level: str = "") -> List[Dict]:
        if not user_skills:
            return self.search_jobs("software developer", location)
        
        skills_query = " ".join(user_skills[:3])  
        
        employment_types = ["FULL_TIME", "PART_TIME", "CONTRACT"]
        
        return self.search_jobs(skills_query, location, limit=15, employment_types=employment_types)
    
    def get_trending_jobs(self, location: str = "") -> List[Dict]:
        """Enhanced trending jobs with AI-powered generation"""
        try:
            # Try AI-powered trending jobs first
            if self.ai_data_service:
                logger.info("🤖 Using AI data service for trending jobs")
                ai_trending = self.ai_data_service.generate_trending_jobs(
                    location=location or "Remote",
                    count=12
                )
                if ai_trending:
                    return ai_trending
        except Exception as e:
            logger.warning(f"AI trending jobs failed: {e}")
        
        # Fallback to query-based search
        trending_queries = [
            "AI engineer machine learning",
            "cloud engineer AWS",
            "full stack developer React",
            "data scientist Python",
            "DevOps engineer Kubernetes"
        ]
        
        all_jobs = []
        for query in trending_queries[:3]:  
            try:
                jobs = self.search_jobs(query, location, limit=4)
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Error fetching trending jobs for query '{query}': {str(e)}")
                continue
        
        return all_jobs[:12]
    
    def search_jobs_by_company(self, company_names: List[str], location: str = "") -> List[Dict]:
        all_jobs = []
        
        for company in company_names:
            try:
                query = f"company:{company}"
                jobs = self.search_jobs(query, location, limit=5)
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Error searching jobs for company '{company}': {str(e)}")
                continue
        
        return all_jobs
    
    def get_job_details(self, job_id: str) -> Optional[Dict]:
        try:
            if not self.client or not self.parent:
                logger.warning("Google Cloud Talent Solution API not available")
                return None
            
            job_name = f"{self.parent}/jobs/{job_id}"
            job = self.client.get_job(name=job_name)
            
            return self._parse_job_result(job)
            
        except Exception as e:
            logger.error(f"Error fetching job details for ID '{job_id}': {str(e)}")
            return None
    def get_salary_insights(self, job_title: str, location: str = "") -> Dict:
        """Enhanced salary insights with AI-powered data generation"""
        try:
            # Try AI-powered salary insights first
            if self.ai_data_service:
                logger.info("🤖 Using AI data service for salary insights")
                ai_insights = self.ai_data_service.generate_salary_insights(
                    job_title=job_title,
                    location=location or "All locations"
                )
                if ai_insights:
                    return ai_insights
        except Exception as e:
            logger.warning(f"AI salary insights failed: {e}")
        
        # Fallback to job search analysis
        try:
            jobs = self.search_jobs(job_title, location, limit=50)
            
            salaries = []
            for job in jobs:
                salary_str = job.get('salary', '')
                if salary_str and salary_str != 'Competitive salary':
                    salary_numbers = self._extract_salary_numbers(salary_str)
                    if salary_numbers:
                        salaries.extend(salary_numbers)
            
            if salaries:
                salaries.sort()
                median_salary = salaries[len(salaries) // 2]
                min_salary = min(salaries)
                max_salary = max(salaries)
                
                return {
                    'median_salary': median_salary,
                    'min_salary': min_salary,
                    'max_salary': max_salary,
                    'sample_size': len(salaries),
                    'job_title': job_title,
                    'location': location or 'All locations'
                }
            else:
                return self._get_default_salary_insights(job_title, location)
                
        except Exception as e:
            logger.error(f"Error getting salary insights: {str(e)}")
            return self._get_default_salary_insights(job_title, location)
    
    def _extract_salary_numbers(self, salary_str: str) -> List[int]:
        clean_str = re.sub(r'[^\d\s\-,k]', '', salary_str.lower())
        
        # Find all numbers
        numbers = re.findall(r'\d+', clean_str)
        
        salary_values = []
        for num_str in numbers:
            try:
                num = int(num_str)
                if 'k' in salary_str.lower():
                    num *= 1000
                if 30000 <= num <= 500000:
                    salary_values.append(num)
            except ValueError:
                continue
        
        return salary_values
    
    def _get_default_salary_insights(self, job_title: str, location: str) -> Dict:
        salary_estimates = {
            'software engineer': {'min': 70000, 'max': 150000, 'median': 110000},
            'data scientist': {'min': 80000, 'max': 160000, 'median': 120000},
            'product manager': {'min': 90000, 'max': 180000, 'median': 135000},
            'devops engineer': {'min': 75000, 'max': 155000, 'median': 115000},
            'frontend developer': {'min': 60000, 'max': 130000, 'median': 95000},
            'backend developer': {'min': 70000, 'max': 140000, 'median': 105000},
            'full stack developer': {'min': 65000, 'max': 135000, 'median': 100000}
        }
        
        title_lower = job_title.lower()
        for key, values in salary_estimates.items():
            if key in title_lower:
                return {
                    'median_salary': values['median'],
                    'min_salary': values['min'],
                    'max_salary': values['max'],
                    'sample_size': 0,
                    'job_title': job_title,
                    'location': location or 'All locations',
                    'note': 'Industry estimate'
                }
        
        return {
            'median_salary': 95000,
            'min_salary': 60000,
            'max_salary': 140000,
            'sample_size': 0,
            'job_title': job_title,
            'location': location or 'All locations',
            'note': 'General industry estimate'
        }
    
    def validate_api_access(self) -> bool:
        """Validate Google Cloud Talent Solution API access"""
        try:
            if not self.client or not self.parent:
                return False
            
            request = talent.SearchJobsRequest(
                parent=self.parent,
                request_metadata=talent.RequestMetadata(
                    user_id="test_user",
                    session_id="validation_session",
                    domain="portfolio-ai.com"
                ),
                job_query=talent.JobQuery(query="test"),
                page_size=1
            )
            
            response = self.client.search_jobs(request=request)
            logger.info("Google Cloud Talent Solution API access validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Google Cloud Talent Solution API validation failed: {str(e)}")
            return False
