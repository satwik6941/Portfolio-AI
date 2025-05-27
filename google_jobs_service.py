import os
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class GoogleJobsService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('JOBS_API_KEY')
        if not self.api_key:
            raise ValueError("JOBS_API_KEY environment variable is required")
            
        self.base_url = "https://jobs.googleapis.com/v4"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[Dict]:
        """
        Search for jobs using Google Cloud Talent Solution API
        """
        try:
            # Construct search request
            search_request = {
                "requestMetadata": {
                    "userId": "portfolio_ai_user",
                    "sessionId": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "domain": "portfolio-ai.com"
                },
                "jobQuery": {
                    "query": query,
                    "locationFilters": [{"address": location}] if location else [],
                    "jobCategories": ["SOFTWARE_ENGINEERING", "INFORMATION_TECHNOLOGY"],
                    "employmentTypes": ["FULL_TIME", "PART_TIME", "CONTRACT"]
                },
                "enableBroadening": True,
                "pageSize": limit,
                "orderBy": "relevance desc"
            }
            
            # Make API request
            endpoint = f"{self.base_url}/projects/YOUR_PROJECT_ID/jobs:search"
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=search_request,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_job_results(data.get('matchingJobs', []))
            else:
                print(f"Error searching jobs: {response.status_code} - {response.text}")
                return self._get_mock_jobs(query, location, limit)
                
        except Exception as e:
            print(f"Exception in job search: {str(e)}")
            return self._get_mock_jobs(query, location, limit)
    
    def _parse_job_results(self, matching_jobs: List[Dict]) -> List[Dict]:
        """Parse Google Cloud Talent Solution API results"""
        parsed_jobs = []
        
        for match in matching_jobs:
            job = match.get('job', {})
            
            # Extract job details
            job_data = {
                'title': job.get('title', 'Software Developer'),
                'company': job.get('company', {}).get('displayName', 'Tech Company'),
                'location': self._extract_location(job.get('addresses', [])),
                'description': job.get('description', 'Exciting opportunity in software development'),
                'employment_type': job.get('employmentTypes', ['FULL_TIME'])[0],
                'posted_date': self._parse_date(job.get('postingCreateTime')),
                'url': job.get('applicationInfo', {}).get('uris', [''])[0] or '#',
                'salary': self._extract_salary(job.get('compensationInfo')),
                'requirements': self._extract_requirements(job.get('qualifications')),
                'skills': self._extract_skills(job.get('description', ''))
            }
            
            parsed_jobs.append(job_data)
        
        return parsed_jobs
    
    def _extract_location(self, addresses: List[str]) -> str:
        """Extract location from addresses array"""
        if addresses:
            return addresses[0]
        return "Remote"
    
    def _parse_date(self, date_string: str) -> str:
        """Parse and format posting date"""
        if not date_string:
            return "Recently"
        
        try:
            # Parse ISO format date
            date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            days_ago = (datetime.now() - date_obj.replace(tzinfo=None)).days
            
            if days_ago == 0:
                return "Today"
            elif days_ago == 1:
                return "Yesterday"
            elif days_ago < 7:
                return f"{days_ago} days ago"
            else:
                return date_obj.strftime("%B %d, %Y")
        except:
            return "Recently"
    
    def _extract_salary(self, compensation_info: Dict) -> str:
        """Extract salary information"""
        if not compensation_info:
            return "Competitive salary"
        
        entries = compensation_info.get('entries', [])
        if entries:
            entry = entries[0]
            amount = entry.get('amount', {})
            currency = amount.get('currencyCode', 'USD')
            
            if 'units' in amount:
                return f"{currency} {amount['units']:,}"
            elif entry.get('range'):
                range_info = entry['range']
                min_amount = range_info.get('min', {}).get('units', 0)
                max_amount = range_info.get('max', {}).get('units', 0)
                return f"{currency} {min_amount:,} - {max_amount:,}"
        
        return "Competitive salary"
    
    def _extract_requirements(self, qualifications: Dict) -> List[str]:
        """Extract job requirements"""
        requirements = []
        
        if qualifications:
            # Extract education requirements
            education = qualifications.get('educationLevels', [])
            if education:
                requirements.append(f"Education: {education[0]}")
            
            # Extract experience requirements
            experience = qualifications.get('experienceInMonths')
            if experience:
                years = experience // 12
                requirements.append(f"{years}+ years experience")
        
        # Default requirements if none found
        if not requirements:
            requirements = [
                "Bachelor's degree in relevant field",
                "Strong problem-solving skills",
                "Team collaboration experience"
            ]
        
        return requirements
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description"""
        common_skills = [
            'Python', 'JavaScript', 'Java', 'React', 'Node.js', 'SQL', 'AWS',
            'Docker', 'Kubernetes', 'Git', 'Agile', 'Scrum', 'REST API',
            'Machine Learning', 'Data Analysis', 'Cloud Computing'
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:8]  # Limit to 8 skills
    
    def _get_mock_jobs(self, query: str, location: str, limit: int) -> List[Dict]:
        """Fallback mock jobs when API is unavailable"""
        mock_jobs = [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Solutions',
                'location': location or 'San Francisco, CA',
                'description': 'Join our innovative team to build cutting-edge software solutions using modern technologies.',
                'employment_type': 'FULL_TIME',
                'posted_date': 'Today',
                'url': '#',
                'salary': 'USD 120,000 - 150,000',
                'requirements': ['5+ years experience', 'Computer Science degree', 'Strong coding skills'],
                'skills': ['Python', 'React', 'AWS', 'Docker']
            },
            {
                'title': 'Full Stack Developer',
                'company': 'StartupHub Inc',
                'location': location or 'New York, NY',
                'description': 'Build end-to-end web applications in a fast-paced startup environment.',
                'employment_type': 'FULL_TIME',
                'posted_date': '2 days ago',
                'url': '#',
                'salary': 'USD 90,000 - 120,000',
                'requirements': ['3+ years experience', 'Bachelor\'s degree', 'Full stack development'],
                'skills': ['JavaScript', 'Node.js', 'React', 'MongoDB']
            },
            {
                'title': 'Frontend Developer',
                'company': 'Digital Agency Pro',
                'location': location or 'Remote',
                'description': 'Create beautiful, responsive user interfaces using modern frontend frameworks.',
                'employment_type': 'CONTRACT',
                'posted_date': '1 week ago',
                'url': '#',
                'salary': 'USD 70 - 90 per hour',
                'requirements': ['2+ years experience', 'Portfolio required', 'UI/UX knowledge'],
                'skills': ['React', 'TypeScript', 'CSS', 'Figma']
            },
            {
                'title': 'Data Scientist',
                'company': 'AI Innovations Lab',
                'location': location or 'Boston, MA',
                'description': 'Analyze complex datasets and build machine learning models to drive business insights.',
                'employment_type': 'FULL_TIME',
                'posted_date': '3 days ago',
                'url': '#',
                'salary': 'USD 100,000 - 140,000',
                'requirements': ['PhD/Masters preferred', '3+ years ML experience', 'Statistical analysis'],
                'skills': ['Python', 'Machine Learning', 'SQL', 'TensorFlow']
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudFirst Technologies',
                'location': location or 'Seattle, WA',
                'description': 'Design and maintain scalable cloud infrastructure and deployment pipelines.',
                'employment_type': 'FULL_TIME',
                'posted_date': '5 days ago',
                'url': '#',
                'salary': 'USD 110,000 - 135,000',
                'requirements': ['4+ years DevOps experience', 'Cloud certifications preferred', 'Automation expertise'],
                'skills': ['AWS', 'Docker', 'Kubernetes', 'Terraform']
            }
        ]
        
        # Filter by query if provided
        if query:
            query_lower = query.lower()
            filtered_jobs = []
            for job in mock_jobs:
                if (query_lower in job['title'].lower() or 
                    query_lower in job['description'].lower() or
                    any(query_lower in skill.lower() for skill in job['skills'])):
                    filtered_jobs.append(job)
            
            if filtered_jobs:
                return filtered_jobs[:limit]
        
        return mock_jobs[:limit]
    
    def get_job_recommendations(self, user_skills: List[str], location: str = "") -> List[Dict]:
        """Get job recommendations based on user skills"""
        if not user_skills:
            return self.search_jobs("software developer", location)
        
        # Create query from user skills
        skills_query = " ".join(user_skills[:3])  # Use top 3 skills
        return self.search_jobs(skills_query, location)
    
    def get_trending_jobs(self, location: str = "") -> List[Dict]:
        """Get trending/popular jobs"""
        trending_queries = [
            "remote software engineer",
            "AI developer",
            "cloud engineer",
            "full stack developer",
            "data scientist"
        ]
        
        all_jobs = []
        for query in trending_queries[:2]:  # Limit to 2 queries
            jobs = self.search_jobs(query, location, limit=3)
            all_jobs.extend(jobs)
        
        return all_jobs[:10]
