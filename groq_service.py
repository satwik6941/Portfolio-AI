import requests
import json
import time
import re
from typing import Dict, List, Optional, Any
try:
    from googlesearch import search
except ImportError:
    print("Warning: googlesearch-python not installed. Search functionality will be limited.")
    search = None

class GroqLLM:
    def __init__(self, api_key: str, model: str = "llama3-70b-8192"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, messages: List[Dict], max_tokens: int = 2000, 
                        temperature: float = 0.7, timeout: int = 30) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                elif response.status_code == 429: 
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (2 ** attempt))
                        continue
                    else:
                        return "❌ Rate limit exceeded. Please try again later."
                else:
                    return f"❌ API Error {response.status_code}: {response.text}"
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return "❌ Request timeout. Please try again."
            except requests.exceptions.RequestException as e:
                return f"❌ Network error: {str(e)}"
            except Exception as e:
                return f"❌ Unexpected error: {str(e)}"
        
        return "❌ Failed to get response after multiple attempts."
    
    def search_unknown_terms(self, text: str, context: str = "") -> Dict[str, str]:
        if not search:
            return {}
            
        unknown_terms = self._extract_unknown_terms(text)
        search_results = {}
        
        for term in unknown_terms[:5]: 
            try:           
                search_query = f"{term} definition meaning {context}" if context else f"{term} definition meaning"
                results = list(search(search_query, num_results=2, sleep_interval=2))
                
                if results:
                    explanation = self._get_term_explanation(term, search_query)
                    if explanation and len(explanation) > 10:
                        search_results[term] = explanation
                        
            except Exception as e:
                print(f"Search error for term '{term}': {e}")
                continue
                
        return search_results
    
    def _extract_unknown_terms(self, text: str) -> List[str]:
        patterns = [
            r'\b[A-Z]{2,}\b',  
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', 
            r'\b\w+(?:\.js|\.py|\.net|\.io|\.com)\b',  
            r'\b(?:React|Angular|Vue|Django|Flask|Laravel|Spring|Docker|Kubernetes|TensorFlow|PyTorch)\b',  # Common tech terms
        ]
        
        terms = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.update(matches)
            
        common_words = {'The', 'This', 'That', 'And', 'Or', 'But', 'For', 'In', 'On', 'At', 'To', 'Of', 'API', 'UI', 'UX'}
        filtered_terms = []
        for term in terms:
            if (term not in common_words and 
                len(term) > 2 and 
                not term.isdigit() and 
                term.upper() not in ['CEO', 'CTO', 'HR', 'IT']):
                filtered_terms.append(term)
                
        return filtered_terms[:10]  
    
    def _get_term_explanation(self, term: str, search_query: str) -> str:
        try:
            prompt = f"""
            Provide a brief, clear explanation of the term "{term}" in 1-2 sentences.
            Focus on what it means in a professional/technical context.
            Be concise and accurate.
            """
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant that provides clear, concise explanations of technical and professional terms."},
                {"role": "user", "content": prompt}
            ]
            
            explanation = self._make_request(messages, max_tokens=100, temperature=0.3)
            return explanation if explanation and not explanation.startswith("❌") else ""
            
        except Exception:
            return ""

    def generate_enhanced_cover_letter(self, user_data: Dict[str, Any], job_description: str, 
                                        company_name: str, tone: str = "Professional") -> str:
        
        search_results = self.search_unknown_terms(job_description, f"{company_name} job requirements")
        
        search_context = ""
        if search_results:
            search_context = "\n\nAdditional context from research:\n"
            for term, explanation in search_results.items():
                search_context += f"- {term}: {explanation}\n"
        
        prompt = f"""
        Write a compelling, {tone.lower()} cover letter for:
        
        Candidate: {user_data.get('name', 'Candidate')}
        Current Title: {user_data.get('title', 'Professional')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        
        Target Company: {company_name}
        Job Description: {job_description}
        Tone: {tone}
        {search_context}
        
        Create a personalized cover letter that:
        1. Opens with a compelling hook specific to the company
        2. Demonstrates clear understanding of the role and technical requirements
        3. Highlights most relevant experience and achievements
        4. Shows knowledge of company culture/values and industry trends
        5. Includes specific examples and metrics
        6. Uses industry terminology correctly (informed by research above)
        7. Maintains {tone.lower()} tone throughout
        8. Closes with strong call to action
        9. Is 350-450 words
            Make it highly personalized and compelling for this specific opportunity, incorporating the researched context naturally.
        """
        
        messages = [
            {"role": "system", "content": f"You are an expert career counselor who writes compelling, {tone.lower()} cover letters that get interviews. You have access to current industry knowledge and terminology."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1500, temperature=0.7)

    def generate_enhanced_resume(self, user_data: Dict[str, Any]) -> str:
        enhancements = user_data.get('ai_enhancements', [])
        style = user_data.get('resume_style', 'Professional ATS-Optimized')
        skills_input = user_data.get('skills_input', '')
        projects = user_data.get('projects', [])
        
        search_context_text = f"{skills_input} {user_data.get('experience', '')} {user_data.get('title', '')}"
        search_results = self.search_unknown_terms(search_context_text, "career skills technology")
        
        search_context = ""
        if search_results:
            search_context = "\n\nResearched technical context:\n"
            for term, explanation in search_results.items():
                search_context += f"- {term}: {explanation}\n"
        
        projects_context = ""
        if projects:
            projects_context = "\n\nProjects to include (format using STAR method):\n"
            for i, project in enumerate(projects, 1):
                projects_context += f"\nProject {i}:\n"
                projects_context += f"- Title: {project.get('title', 'Untitled Project')}\n"
                projects_context += f"- Description: {project.get('description', 'No description provided')}\n"
                if project.get('technologies'):
                    projects_context += f"- Technologies: {project.get('technologies')}\n"
                if project.get('duration'):
                    projects_context += f"- Duration: {project.get('duration')}\n"
        
        prompt = f"""
        Create an enhanced, {style} resume for:
        
        Name: {user_data.get('name', 'Your Name')}
        Title: {user_data.get('title', 'Professional')}
        Email: {user_data.get('email', 'email@example.com')}
        Phone: {user_data.get('phone', 'Phone Number')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        Education: {user_data.get('education', 'Educational background')}
        
        Apply these AI enhancements: {', '.join(enhancements)}
        {search_context}
        {projects_context}
        
        Create a professional resume with:
        1. Compelling professional summary using current industry terminology
        2. Quantified achievements with metrics
        3. Industry-specific keywords (informed by research above)
        4. ATS-optimized formatting
        5. Strong action verbs
        6. Relevant technical skills highlighted with proper context
        7. Current industry trends and terminology integration
        8. Projects section formatted using STAR method (Situation, Task, Action, Result) - analyze each project description and reformat to highlight the situation faced, tasks undertaken, actions taken, and measurable results achieved
        
        IMPORTANT: For each project, transform the raw description into STAR format:
        - Situation: What was the context or challenge?
        - Task: What needed to be accomplished?
        - Action: What specific actions did you take?
        - Result: What measurable outcomes were achieved?
        
        Format for both ATS and human readability, ensuring technical terms are used correctly.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert resume writer who creates compelling, ATS-optimized resumes with quantified achievements and current industry knowledge."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=2000, temperature=0.6)

    def generate_tailored_resume(self, user_data: Dict[str, Any], job_description: str) -> str:
        search_results = self.search_unknown_terms(job_description, "job requirements career skills")
        projects = user_data.get('projects', [])
        
        enhanced_user_data = user_data.copy()
        if search_results:
            search_context = "\n\nResearched job context:\n"
            for term, explanation in search_results.items():
                search_context += f"- {term}: {explanation}\n"
            enhanced_job_description = job_description + search_context
        else:
            enhanced_job_description = job_description
        
        if projects:
            enhanced_user_data['projects'] = projects
            
        return self.generate_resume(enhanced_user_data, enhanced_job_description)

    def generate_resume(self, user_data: Dict[str, Any], job_description: str = "") -> str:
        tailoring_context = f"\n\nTailor the resume for this job:\n{job_description}" if job_description else ""
        projects = user_data.get('projects', [])
        
        projects_context = ""
        if projects:
            projects_context = "\n\nProjects to include (format using STAR method):\n"
            for i, project in enumerate(projects, 1):
                projects_context += f"\nProject {i}:\n"
                projects_context += f"- Title: {project.get('title', 'Untitled Project')}\n"
                projects_context += f"- Description: {project.get('description', 'No description provided')}\n"
                if project.get('technologies'):
                    projects_context += f"- Technologies: {project.get('technologies')}\n"
                if project.get('duration'):
                    projects_context += f"- Duration: {project.get('duration')}\n"
        
        prompt = f"""
        Create an ATS-optimized resume for:
        
        Name: {user_data.get('name', 'Your Name')}
        Title: {user_data.get('title', 'Professional')}
        Email: {user_data.get('email', 'email@example.com')}
        Phone: {user_data.get('phone', 'Phone Number')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        Education: {user_data.get('education', 'Educational background')}
        {tailoring_context}
        {projects_context}
        
        Create a professional, ATS-friendly resume with:
        1. Contact information
        2. Professional summary (3-4 lines)
        3. Core competencies/skills
        4. Professional experience with bullet points
        5. Projects section (if projects provided) - Format each project using STAR method
        6. Education
        7. Use action verbs and quantify achievements where possible
        8. Include relevant keywords for ATS optimization
        
        IMPORTANT: If projects are provided, create a dedicated "PROJECTS" section and format each project using the STAR method:
        - Situation: What was the context or challenge?
        - Task: What needed to be accomplished?
        - Action: What specific actions did you take?
        - Result: What measurable outcomes were achieved?
        
        Transform the raw project descriptions into compelling STAR-formatted entries that showcase impact and achievements.
        
        Format in clean, readable text suitable for both ATS and human review.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an expert resume writer specializing in ATS-optimized resumes that get results."
            },
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=2000, temperature=0.6)

    def generate_interview_questions(self, job_description: str, user_data: Dict[str, Any], num_questions: int = 5) -> List[Dict]:
        prompt = f"""
        Generate {num_questions} interview questions for this position:
        
        Job Description:
        {job_description}
        
        Candidate Profile:
        Name: {user_data.get('name', 'Candidate')}
        Title: {user_data.get('title', 'Professional')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        
        Create a mix of:
        1. Behavioral questions (STAR method)
        2. Technical questions (based on skills)
        3. Situational questions
        4. Company/role-specific questions
        
        Return as JSON array:
        [
            {
                "question": "Tell me about yourself",
                "type": "General",
                "difficulty": "Easy",
                "category": "Introduction"
            },
            ...
        ]
        """
        
        messages = [
            {"role": "system", "content": "You are an expert interview coach who creates thoughtful, relevant interview questions. Return only valid JSON array."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1500, temperature=0.7)
        
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                questions = json.loads(json_str)
                return questions if isinstance(questions, list) else []
        except:
            return [
                {"question": "Tell me about yourself and your background.", "type": "General", "difficulty": "Easy", "category": "Introduction"},
                {"question": "Why are you interested in this position?", "type": "Behavioral", "difficulty": "Easy", "category": "Motivation"},
                {"question": "Describe a challenging project you worked on and how you handled it.", "type": "Behavioral", "difficulty": "Medium", "category": "Problem Solving"},
                {"question": "What are your greatest strengths and how do they apply to this role?", "type": "General", "difficulty": "Medium", "category": "Self Assessment"},
                {"question": "Where do you see yourself in 5 years?", "type": "General", "difficulty": "Medium", "category": "Career Goals"}
            ]

    def generate_interview_question(self, user_data: Dict[str, Any], job_description: str = "") -> str:
        questions = self.generate_interview_questions(job_description, user_data, 1)
        return questions[0]['question'] if questions else "Tell me about your experience and background."

    def evaluate_interview_answer(self, question: str, answer: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Evaluate this interview answer:
        
        Question: {question}
        Answer: {answer}
        
        Candidate Profile:
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        
        Provide evaluation with:
        1. Score (1-10)
        2. Strengths in the answer
        3. Areas for improvement
        4. Specific suggestions
        
        Return as JSON:
        {
            "score": 7,
            "strengths": ["Clear communication", "Relevant example"],
            "weaknesses": ["Could be more specific", "Missing quantified results"],
            "suggestions": "Try to include specific metrics and outcomes in your examples.",
            "feedback": "Good response overall, but could be enhanced with more concrete details."
        }
        """
        
        messages = [
            {"role": "system", "content": "You are an expert interview coach providing constructive feedback. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=800, temperature=0.6)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "score": 7,
                "strengths": ["Good effort"],
                "weaknesses": ["Could provide more detail"],
                "suggestions": "Consider using the STAR method for behavioral questions.",
                "feedback": "Thank you for your response. Consider adding more specific examples."
            }

    def generate_chat_interview_question(self, context: str, user_data: Dict[str, Any], question_number: int) -> str:
        prompt = f"""
        You are conducting a conversational job interview. Generate the next question based on:
        
        {context}
        
        Candidate Background:
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        
        This is question #{question_number} of 5. Generate a natural, conversational interview question that:
        1. Flows from the previous conversation
        2. Is appropriate for the role and experience level
        3. Allows the candidate to showcase their skills
        4. Feels like a real interview conversation
        
        Return only the question text, no additional formatting.
        """
        
        messages = [
            {"role": "system", "content": "You are a professional interviewer conducting a conversational job interview. Ask thoughtful, relevant questions."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=200, temperature=0.7)
        return response if response and not response.startswith("❌") else "Can you tell me more about your relevant experience for this role?"

    def analyze_chat_interview(self, questions: List[str], answers: List[str], job_info: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        interview_content = ""
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            interview_content += f"Q{i}: {q}\nA{i}: {a}\n\n"
        
        prompt = f"""
        Analyze this complete job interview performance:
        
        Job Information:
        Position: {job_info.get('job_title', 'N/A')}
        Company: {job_info.get('company', 'N/A')}
        Experience Level: {job_info.get('experience_level', 'N/A')}
        Interview Type: {job_info.get('interview_type', 'N/A')}
        
        Interview Conversation:
        {interview_content}
        
        Candidate Profile:
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        
        Provide comprehensive analysis:
        {
            "overall_score": 8.5,
            "performance_level": "Excellent",
            "strengths": ["Strong communication", "Relevant examples", "Technical knowledge"],
            "improvement_areas": ["Could provide more specific metrics", "Expand on leadership examples"],
            "detailed_feedback": "The candidate demonstrated strong technical knowledge and communication skills...",
            "question_scores": [8, 7, 9, 8, 7],
            "recommendations": ["Practice quantifying achievements", "Prepare more leadership stories"]
        }
        """
        
        messages = [
            {"role": "system", "content": "You are an expert interview analyst providing detailed performance feedback. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1500, temperature=0.6)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "overall_score": 7.5,
                "performance_level": "Good",
                "strengths": ["Good communication", "Relevant experience"],
                "improvement_areas": ["Provide more specific examples", "Quantify achievements"],
                "detailed_feedback": "You demonstrated good knowledge and communication skills. Consider adding more specific examples and quantifiable achievements in future interviews.",
                "question_scores": [7] * len(questions),
                "recommendations": ["Practice the STAR method", "Prepare specific achievement stories"]
            }

    def chat_about_resume(self, resume_content: str, user_message: str, chat_history: List[Dict] = None) -> str:
        if chat_history is None:
            chat_history = []
        
        conversation = ""
        for msg in chat_history[-5:]: 
            role = "You" if msg['role'] == 'user' else "AI Assistant"
            conversation += f"{role}: {msg['content']}\n"
        
        prompt = f"""
        You are an expert career counselor and resume specialist. The user has uploaded their resume and wants to discuss it with you.
        
        Resume Content:
        {resume_content}
        
        Previous Conversation:
        {conversation}
        
        User's Question/Message:
        {user_message}
        
        Provide helpful, specific advice about their resume. You can:
        1. Answer questions about resume content
        2. Suggest improvements to specific sections
        3. Analyze strengths and weaknesses
        4. Provide industry-specific advice
        5. Help optimize for ATS systems
        6. Suggest additional skills or experiences to highlight
        7. Help tailor the resume for specific jobs
        
        Be conversational, supportive, and provide actionable advice.
        """
        
        messages = [
            {"role": "system", "content": "You are a friendly and expert career counselor who helps people improve their resumes. Be conversational, supportive, and provide specific, actionable advice."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1000, temperature=0.7)

    def analyze_job_requirements(self, job_description: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Analyze this job description against the candidate's profile:
        
        Job Description:
        {job_description}
        
        Candidate Profile:
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        Title: {user_data.get('title', 'Professional')}
        
        Provide analysis:
        {
            "match_percentage": 85,
            "keyword_matches": 12,
            "missing_skills": ["Python", "Docker"],
            "matching_skills": ["JavaScript", "React", "Node.js"],
            "recommendations": ["Highlight your JavaScript experience", "Consider learning Python"]
        }
        """
        
        messages = [
            {"role": "system", "content": "You are an expert job match analyzer. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=800, temperature=0.3)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "match_percentage": 75,
                "keyword_matches": 8,
                "missing_skills": ["Review job requirements"],
                "matching_skills": user_data.get('skills', [])[:5],
                "recommendations": ["Tailor your resume to match job requirements"]
            }
    
    def parse_resume_data(self, resume_text: str) -> Dict[str, Any]:
        prompt = f"""
        Extract and structure the following information from this resume text:
        
        Resume Text:
        {resume_text}
        
        Extract the following information and return as JSON:
        {{
            "name": "Full Name",
            "email": "email@example.com",
            "phone": "Phone Number",
            "title": "Job Title/Professional Title",
            "skills": ["skill1", "skill2", "skill3"],
            "experience": "Work experience summary",
            "education": "Educational background",
            "linkedin": "LinkedIn URL if found",
            "location": "Location/Address if found"
        }}
        
        Guidelines:
        1. Extract exact information from the resume
        2. For skills, create a list of individual skills
        3. For experience, provide a concise summary of work history
        4. For education, include degree, institution, and year if available
        5. Use "Not found" for any missing information
        6. Ensure valid JSON format
        """
        
        messages = [
            {"role": "system", "content": "You are an expert resume parser that extracts structured data from resume text. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1000, temperature=0.3)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                parsed_data = json.loads(json_str)
                
                if 'skills' in parsed_data and isinstance(parsed_data['skills'], str):
                    parsed_data['skills'] = [skill.strip() for skill in parsed_data['skills'].split(',') if skill.strip()]
                
                return parsed_data
        except Exception as e:
            print(f"Error parsing resume data: {e}")
            
        return self._fallback_resume_parsing(resume_text)
    
    def _fallback_resume_parsing(self, resume_text: str) -> Dict[str, Any]:
        import re
        
        parsed_data = {
            "name": "Not found",
            "email": "Not found", 
            "phone": "Not found",
            "title": "Not found",
            "skills": [],
            "experience": "Not found",
            "education": "Not found",
            "linkedin": "Not found",
            "location": "Not found"
        }
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, resume_text)
        if email_match:
            parsed_data["email"] = email_match.group()
        
        phone_pattern = r'(\+?1?[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, resume_text)
        if phone_match:
            parsed_data["phone"] = phone_match.group()
        
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, resume_text, re.IGNORECASE)
        if linkedin_match:
            parsed_data["linkedin"] = linkedin_match.group()
        
        lines = resume_text.split('\n')
        for line in lines[:5]:  
            line = line.strip()
            if line and len(line) > 3 and len(line) < 50:
                if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line):
                    parsed_data["name"] = line
                    break
        
        experience_keywords = ['experience', 'work', 'employment', 'career', 'professional']
        for keyword in experience_keywords:
            pattern = rf'{keyword}.*?(?=\n\n|\Z)'
            match = re.search(pattern, resume_text, re.IGNORECASE | re.DOTALL)
            if match:
                parsed_data["experience"] = match.group()[:200] + "..."
                break
        
        return parsed_data

    def generate_enhanced_portfolio(self, user_data: Dict[str, Any]) -> str:
        prompt = f"""
        Create a comprehensive and professional portfolio content for the following person.
        Make it engaging, well-structured, and highlight their strengths and achievements.
        
        User Data:
        Name: {user_data.get('name', 'N/A')}
        Email: {user_data.get('email', 'N/A')}
        Phone: {user_data.get('phone', 'N/A')}
        LinkedIn: {user_data.get('linkedin', 'N/A')}
        GitHub: {user_data.get('github', 'N/A')}
        Summary: {user_data.get('summary', 'N/A')}
        Skills: {user_data.get('skills', 'N/A')}
        Experience: {user_data.get('experience', 'N/A')}
        Education: {user_data.get('education', 'N/A')}
        Projects: {user_data.get('projects', 'N/A')}
        Certifications: {user_data.get('certifications', 'N/A')}
        
        Create a portfolio with the following sections:
        1. Professional Summary
        2. Core Competencies
        3. Professional Experience (with achievements)
        4. Education & Certifications
        5. Featured Projects
        6. Technical Skills
        7. Contact Information
        
        Make it professional, compelling, and tailored to showcase their unique value proposition.
        Use modern, engaging language and highlight quantifiable achievements where possible.
        """
        
        messages = [
            {"role": "system", "content": "You are a professional portfolio writer with expertise in creating compelling personal portfolios that showcase candidates in the best light."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            return self._make_request(messages, max_tokens=2500, temperature=0.8)
        except Exception as e:
            return f"Error generating enhanced portfolio: {str(e)}"

    def generate_deployment_guide(self, hosting_option: str, user_data: Dict[str, Any]) -> str:
        """Generate deployment guide for the specified hosting option."""
        prompt = f"""
        Create a detailed deployment guide for hosting a portfolio website on {hosting_option}.
        
        The portfolio is for: {user_data.get('name', 'the user')}
        Portfolio type: Professional portfolio website
        
        Please provide:
        1. Step-by-step deployment instructions
        2. Prerequisites and requirements
        3. Configuration steps
        4. Best practices for {hosting_option}
        5. Common troubleshooting tips
        6. Cost considerations (if any)
        7. Domain setup (if applicable)
        8. SSL certificate setup
        9. Performance optimization tips
        
        Make the guide beginner-friendly but comprehensive.
        Include specific commands, code snippets, and configuration examples where relevant.
        """
        
        messages = [
            {"role": "system", "content": f"You are an expert in web deployment and hosting, specifically knowledgeable about {hosting_option} deployment strategies."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            return self._make_request(messages, max_tokens=2000, temperature=0.7)
        except Exception as e:
            return f"Error generating deployment guide: {str(e)}"

    def get_deployment_quick_start(self, hosting_option: str) -> str:
        quick_starts = {
            "Netlify": """
            🚀 **Netlify Quick Start**
            
            1. **Connect Repository**
                - Link your GitHub/GitLab repository
                - Authorize Netlify access
            
            2. **Configure Build Settings**
                - Build command: `npm run build` or `yarn build`
                - Publish directory: `dist` or `build`
            
            3. **Deploy**
                - Click "Deploy Site"
                - Get your live URL instantly
            
            4. **Custom Domain (Optional)**
                - Go to Domain settings
                - Add your custom domain
                - Configure DNS
            
            **Pro Tips:**
            - Enable branch deploys for testing
            - Set up form handling for contact forms
            - Use Netlify Functions for serverless features
            """,
            
            "Vercel": """
            🚀 **Vercel Quick Start**
            
            1. **Import Project**
                - Connect your Git repository
                - Select framework preset (React, Next.js, etc.)
            
            2. **Configure Project**
                - Build command: `npm run build`
                - Output directory: `out` or `dist`
            
            3. **Deploy**
                - Click "Deploy"
                - Get your production URL
            
            4. **Custom Domain**
                - Add domain in project settings
                - Configure nameservers
            
            **Pro Tips:**
            - Use Vercel Analytics for insights
            - Enable preview deployments
            - Set up environment variables for APIs
            """,
            
            "GitHub Pages": """
            🚀 **GitHub Pages Quick Start**
            
            1. **Repository Setup**
                - Create public repository
                - Upload your portfolio files
            
            2. **Enable GitHub Pages**
                - Go to Settings > Pages
                - Select source branch (main/gh-pages)
            
            3. **Configure**
                - Choose root folder or `/docs`
                - Wait for deployment
            
            4. **Access Your Site**
                - URL: `username.github.io/repository-name`
            
            **Pro Tips:**
            - Use GitHub Actions for automated builds
            - Add CNAME file for custom domains
            - Keep repository public for free hosting
            """,
            
            "Firebase": """
            🚀 **Firebase Hosting Quick Start**
            
            1. **Setup Firebase CLI**
                ```bash
                npm install -g firebase-tools
                firebase login
                ```
            
            2. **Initialize Project**
                ```bash
                firebase init hosting
                ```
            
            3. **Deploy**
                ```bash
                firebase deploy
                ```
            
            4. **Custom Domain**
                - Add domain in Firebase Console
                - Update DNS records
            
            **Pro Tips:**
            - Use Firebase Analytics
            - Enable caching rules
            - Set up multiple environments
            """
        }
        
        return quick_starts.get(hosting_option, f"""
        🚀 **{hosting_option} Quick Start**
        
        1. **Prepare Your Files**
            - Ensure all HTML, CSS, JS files are ready
            - Test locally before deployment
        
        2. **Upload to {hosting_option}**
            - Follow the platform's upload process
            - Configure any necessary settings
        
        3. **Configure Domain**
            - Set up custom domain if needed
            - Configure SSL certificate
        
        4. **Test & Optimize**
            - Check all links and functionality
            - Optimize for performance
        
        For detailed instructions, refer to {hosting_option}'s official documentation.
        """)
