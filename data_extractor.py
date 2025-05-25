import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image
import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, List, Optional

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
    
    def parse_resume_data(self, text: str) -> Dict:
        data = {
            'name': '',
            'email': '',
            'phone': '',
            'skills': [],
            'experience': [],
            'education': [],
            'projects': []
        }
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            data['email'] = emails[0]
        
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            data['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]

        lines = text.split('\n')
        for line in lines[:5]:  
            line = line.strip()
            if line and not any(char.isdigit() for char in line) and '@' not in line:
                if len(line.split()) <= 4:  
                    data['name'] = line
                    break
        
        skill_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'SQL',
            'Machine Learning', 'Data Analysis', 'Project Management', 'Leadership',
            'Communication', 'Problem Solving', 'Teamwork'
        ]
        
        for skill in skill_keywords:
            if skill.lower() in text.lower():
                data['skills'].append(skill)
        
        return data

class JobSearcher:
    def __init__(self):
        pass
    
    def search_jobs(self, keywords: str, location: str = "", remote: bool = True) -> List[Dict]:
        
        mock_jobs = [
            {
                'title': f'{keywords} Developer',
                'company': 'Tech Corp',
                'location': location or 'Remote',
                'description': f'We are looking for a skilled {keywords} professional...',
                'requirements': [f'{keywords} experience', 'Problem solving skills'],
                'posted_date': '2025-05-20',
                'url': 'https://example.com/job1'
            },
            {
                'title': f'Senior {keywords} Engineer',
                'company': 'Innovation Inc',
                'location': location or 'Remote',
                'description': f'Join our team as a {keywords} expert...',
                'requirements': [f'5+ years {keywords}', 'Team leadership'],
                'posted_date': '2025-05-22',
                'url': 'https://example.com/job2'
            }
        ]
        
        return mock_jobs
    
    def get_job_alerts(self, user_profile: Dict, preferences: Dict) -> List[Dict]:
        skills = user_profile.get('skills', [])
        location = preferences.get('location', '')
        
        alerts = []
        for skill in skills[:3]:  
            jobs = self.search_jobs(skill, location)
            alerts.extend(jobs[:2])  
        
        return alerts