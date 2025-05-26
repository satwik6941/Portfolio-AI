import requests
import json
import time
from typing import Dict, List, Optional, Any

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
                elif response.status_code == 429:  # Rate limit
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
    
    def generate_portfolio_content(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Create compelling portfolio content for a professional based on this data:
        
        Name: {user_data.get('name', 'Professional')}
        Title: {user_data.get('title', 'Professional')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Experienced professional')}
        Education: {user_data.get('education', '')}
        
        Generate content for these portfolio sections:
        1. Professional summary (2-3 compelling sentences)
        2. About section (150-200 words, engaging and personal)
        3. Skills organized by category
        4. Project highlights (3-4 impressive projects based on skills)
        5. Call-to-action statement
        
        Make it professional, engaging, and showcase expertise.        Return as JSON with keys: summary, about, skills_categories, projects, cta
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an expert portfolio writer who creates compelling professional content. Always return valid JSON."
            },
            {"role": "user", "content": prompt}
        ]
        response = self._make_request(messages, max_tokens=1500, temperature=0.8)
        
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            # Fallback if JSON parsing fails
            return {
                "summary": f"Experienced {user_data.get('title', 'professional')} with expertise in {', '.join(user_data.get('skills', [])[:3])}.",
                "about": response[:300] if response else "Professional with extensive experience in their field.",
                "skills_categories": {"Technical": user_data.get('skills', [])},
                "projects": [],
                "cta": "Let's connect and discuss opportunities!"
            }
    
    def generate_resume(self, user_data: Dict[str, Any], job_description: str = "") -> str:
        tailoring_context = f"\n\nTailor the resume for this job:\n{job_description}" if job_description else ""
        
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
        
        Create a professional, ATS-friendly resume with:
        1. Contact information
        2. Professional summary (3-4 lines)
        3. Core competencies/skills
        4. Professional experience with bullet points
        5. Education
        6. Use action verbs and quantify achievements where possible
        7. Include relevant keywords for ATS optimization
        
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
    
    def generate_cover_letter(self, user_data: Dict[str, Any], 
                            job_description: str, company_name: str) -> str:
        prompt = f"""
        Write a compelling cover letter for:
        
        Candidate: {user_data.get('name', 'Candidate')}
        Current Title: {user_data.get('title', 'Professional')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        
        Target Company: {company_name}
        Job Description: {job_description}
        
        Create a personalized cover letter that:
        1. Opens with a strong hook
        2. Highlights relevant experience and skills
        3. Shows knowledge of the company/role
        4. Demonstrates value proposition
        5. Closes with a strong call to action
        6. Maintains professional tone
        7. Is 3-4 paragraphs, around 300-400 words
        
        Make it compelling and specific to this opportunity.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an expert career counselor who writes compelling, personalized cover letters that get interviews."
            },
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1500, temperature=0.7)
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze this resume and extract structured information:
        
        {resume_text}
        
        Extract and return as JSON:
        {{
            "name": "Full name",
            "title": "Professional title/role",
            "email": "Email address",
            "phone": "Phone number",
            "summary": "Professional summary (2-3 sentences)",
            "skills": ["skill1", "skill2", "skill3"],
            "experience": [
                {{
                    "title": "Job title",
                    "company": "Company name",
                    "duration": "Start - End dates",
                    "description": "Key responsibilities and achievements"
                }}
            ],
            "education": "Education details"
        }}
        
        If information is missing, use reasonable defaults or leave empty.
        Focus on extracting the most relevant professional information.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an expert at analyzing resumes and extracting structured data. Always return valid JSON."
            },
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=2000, temperature=0.3)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "name": "Name not found",
                "title": "Title not found", 
                "email": "",
                "phone": "",
                "summary": "Professional with experience in their field.",
                "skills": [],
                "experience": [],
                "education": "Education details not available"
            }
    
    def generate_interview_question(self, user_data: Dict[str, Any], 
                                  interview_type: str, job_role: str, 
                                  question_number: int) -> str:
        prompt = f"""
        Generate an appropriate {interview_type.lower()} interview question for:
        
        Candidate Profile:
        - Role: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', [])[:5])}
        - Experience Level: {user_data.get('experience', 'Professional experience')}
        
        Target Role: {job_role}
        Question Number: {question_number}
        Interview Type: {interview_type}
        
        Create a question that:
        1. Is appropriate for the experience level
        2. Relates to the target role
        3. Matches the interview type
        4. Allows the candidate to showcase their skills
        5. Is challenging but fair
        
        Return only the question, no additional text.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an expert interviewer who creates insightful, role-appropriate interview questions."
            },
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=500, temperature=0.7)
    
    def evaluate_interview_answer(self, question: str, answer: str, 
                                user_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Evaluate this interview answer:
        
        Question: {question}
        Answer: {answer}
        
        Candidate Background:
        - Role: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', [])[:3])}
        
        Provide evaluation with:
        1. Score (1-10 scale)
        2. Strengths (2-3 points)
        3. Areas for improvement (2-3 points)
        4. Specific suggestions for better answers
        
        Return as JSON:
        {{
            "score": 8,
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"],
            "suggestions": "Specific advice for improvement"
        }}
        
        Be constructive and helpful in feedback.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an expert interview coach providing constructive feedback to help candidates improve."
            },
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1000, temperature=0.6)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            # Fallback evaluation
            return {
                "score": 7,
                "strengths": ["Clear communication", "Relevant experience"],
                "improvements": ["Add more specific examples", "Provide quantifiable results"],
                "suggestions": "Try to include specific examples and measurable outcomes to strengthen your answer."
            }
    
    def generate_final_interview_feedback(self, interview_history: List[Dict]) -> str:
        qa_pairs = []
        for i in range(0, len(interview_history), 2):
            if i + 1 < len(interview_history):
                qa_pairs.append({
                    "question": interview_history[i].get("content", ""),
                    "answer": interview_history[i + 1].get("content", "")
                })
        
        prompt = f"""
        Provide comprehensive interview feedback based on this session:
        
        Interview Q&A:
        {json.dumps(qa_pairs, indent=2)}
        
        Analyze the overall performance and provide:
        1. Overall assessment (strengths and weaknesses)
        2. Communication style feedback
        3. Technical competency evaluation
        4. Top 3 areas for improvement
        5. Specific action steps for better interviews
        6. Recommended practice areas
        7. Overall score and readiness level
        
        Be encouraging but honest, focusing on actionable improvements.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are a senior interview coach providing comprehensive performance feedback."
            },
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1500, temperature=0.6)
    
    def optimize_for_ats(self, resume_content: str, job_description: str) -> str:
        prompt = f"""
        Optimize this resume for ATS systems and the target job:
        
        Current Resume:
        {resume_content}
        
        Target Job:
        {job_description}
        
        Enhance the resume by:
        1. Adding relevant keywords from the job description
        2. Improving formatting for ATS readability
        3. Quantifying achievements where possible
        4. Using action verbs and industry terminology
        5. Ensuring proper section headers
        6. Maintaining readability for humans
        
        Return the improved resume content with better ATS compatibility.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an ATS optimization expert who improves resume compatibility while maintaining quality."
            },
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=2000, temperature=0.5)
    
    def generate_job_search_strategy(self, user_data: Dict[str, Any]) -> str:
        prompt = f"""
        Create a personalized job search strategy for:
        
        Profile:
        - Current Role: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', []))}
        - Experience: {user_data.get('experience', 'Professional experience')}
        - Goals: Career advancement and growth
        
        Provide a comprehensive strategy including:
        1. Target companies and industries
        2. Networking recommendations
        3. Skill development priorities
        4. Application approach and timeline
        5. Interview preparation focus areas
        6. Online presence optimization
        7. Salary negotiation tips
        
        Make it actionable and specific to their background.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are a career strategist who creates personalized job search plans that deliver results."
            },
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=2000, temperature=0.7)

    def health_check(self) -> bool:
        """
        Check if the Groq service is accessible
        
        Returns:
            True if service is accessible, False otherwise
        """
        test_messages = [
            {"role": "user", "content": "Hello, are you working?"}
        ]
        
        response = self._make_request(test_messages, max_tokens=50, temperature=0.1)
        return not response.startswith("❌")
    
    def generate_interview_questions(self, job_description: str, user_background: Dict) -> List[Dict]:
        prompt = f"""
        Generate 5 diverse interview questions for this job opportunity:
        
        Job Description: {job_description}
        
        Candidate Background:
        - Name: {user_background.get('name', 'Candidate')}
        - Title: {user_background.get('title', 'Professional')}
        - Skills: {', '.join(user_background.get('skills', [])[:5])}
        - Experience: {user_background.get('experience', 'Professional experience')}
        
        Create a balanced set of questions:
        1. One behavioral question (past experience/situations)
        2. One technical question (role-specific skills)
        3. One problem-solving question (hypothetical scenario)
        4. One cultural fit question (values/work style)
        5. One career goals question (future aspirations)
        
        Return as JSON array with this format:
        [
            {
                "question": "Tell me about a time when...",
                "type": "behavioral",
                "difficulty": "medium",
                "focus_area": "teamwork"
            }
        ]
        
        Make questions specific to the role and appropriate for the candidate's level.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an expert interviewer who creates comprehensive, balanced interview question sets."
            },
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1500, temperature=0.8)
        
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                questions = json.loads(json_str)
                return questions
        except:
            return [
                {
                    "question": "Tell me about yourself and why you're interested in this position.",
                    "type": "general",
                    "difficulty": "easy",
                    "focus_area": "introduction"
                },
                {
                    "question": "Describe a challenging project you worked on and how you overcame obstacles.",
                    "type": "behavioral", 
                    "difficulty": "medium",
                    "focus_area": "problem_solving"
                },
                {
                    "question": "What technical skills do you consider your strongest, and can you give an example of how you've applied them?",
                    "type": "technical",
                    "difficulty": "medium", 
                    "focus_area": "technical_skills"
                },
                {
                    "question": "How do you handle working under pressure and tight deadlines?",
                    "type": "behavioral",
                    "difficulty": "medium",
                    "focus_area": "stress_management"
                },
                {
                    "question": "Where do you see yourself in 3-5 years, and how does this role fit into your career goals?",
                    "type": "career_goals",
                    "difficulty": "easy",
                    "focus_area": "future_planning"
                }
            ]
    
    def generate_enhanced_portfolio(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced portfolio with AI-powered content and styling"""
        style = user_data.get('portfolio_style', 'Modern Professional')
        color_scheme = user_data.get('color_scheme', 'Blue Gradient')
        include_projects = user_data.get('include_projects', True)
        
        prompt = f"""
        Create an enhanced, professional portfolio for:
        
        Name: {user_data.get('name', 'Professional')}
        Title: {user_data.get('title', 'Professional')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        Education: {user_data.get('education', '')}
        
        Portfolio Style: {style}
        Color Scheme: {color_scheme}
        Include Projects: {include_projects}
        
        Generate comprehensive portfolio content including:
        1. Compelling professional headline
        2. Engaging about section (200-250 words)
        3. Skills categorized by expertise level
        4. {"3-4 realistic project examples based on skills" if include_projects else "No projects section"}
        5. Professional achievements and metrics
        6. Call-to-action statement
        
        Make it {style.lower()} in style and highly engaging.
        Return as JSON with keys: headline, about, skills_categories, projects, achievements, cta
        """
        
        messages = [
            {"role": "system", "content": "You are an expert portfolio designer who creates compelling, professional content. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=2000, temperature=0.8)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "headline": f"Innovative {user_data.get('title', 'Professional')} with expertise in {', '.join(user_data.get('skills', [])[:2])}",
                "about": f"Passionate {user_data.get('title', 'professional')} with extensive experience in delivering high-quality solutions.",
                "skills_categories": {"Technical": user_data.get('skills', [])},
                "projects": [] if not include_projects else [
                    {"name": "Sample Project", "description": "Professional project showcasing skills", "tech": user_data.get('skills', [])[:3]}
                ],
                "achievements": ["Delivered successful projects", "Strong problem-solving abilities"],
                "cta": "Let's collaborate on your next project!"
            }
    
    def enhance_portfolio_content(self, portfolio_content: Dict, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance existing portfolio content with AI improvements"""
        prompt = f"""
        Enhance this portfolio content to make it more compelling and professional:
        
        Current Portfolio:
        {json.dumps(portfolio_content, indent=2)}
        
        User Profile:
        - Name: {user_data.get('name', 'Professional')}
        - Title: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', []))}
        
        Enhance by:
        1. Making the language more engaging and dynamic
        2. Adding specific industry terminology
        3. Improving the professional tone        4. Adding more compelling achievements
        5. Creating stronger call-to-action statements
        
        Return the enhanced content as JSON with the same structure.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert content enhancer who makes portfolios more compelling and professional."},
            {"role": "user", "content": prompt}
        ]
        response = self._make_request(messages, max_tokens=2000, temperature=0.7)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return portfolio_content
    
    def generate_deployment_guide(self, hosting_option: str, user_data: Dict[str, Any]) -> str:
        """Generate deployment guide for portfolio hosting"""
        prompt = f"""
        Create a step-by-step deployment guide for hosting a portfolio website on {hosting_option}.
        
        User Profile: {user_data.get('title', 'Professional')} with {len(user_data.get('skills', []))} technical skills
        
        Provide:
        1. Prerequisites and requirements
        2. Step-by-step deployment instructions
        3. Configuration settings
        4. Custom domain setup (if applicable)
        5. Best practices and optimization tips
        6. Troubleshooting common issues
        
        Make it beginner-friendly but comprehensive.
        """
        
        messages = [
            {"role": "system", "content": "You are a deployment expert who creates clear, actionable hosting guides."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1500, temperature=0.6)
    
    def analyze_job_requirements(self, job_description: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze job requirements against user profile"""
        prompt = f"""
        Analyze this job description against the candidate's profile:
        
        Job Description:
        {job_description}
        
        Candidate Profile:
        - Title: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', []))}
        - Experience: {user_data.get('experience', 'Professional experience')}
          Provide analysis with:
        1. Keyword matches found
        2. Skills alignment percentage
        3. Experience level match
        4. Missing requirements
        5. Suggested improvements
          Return as JSON: {{"keyword_matches": number, "skills_alignment": percentage, "missing_requirements": [], "suggestions": []}}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert job analyst who evaluates candidate-job fit."},
            {"role": "user", "content": prompt}
        ]
        response = self._make_request(messages, max_tokens=1000, temperature=0.5)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {"keyword_matches": 5, "skills_alignment": 75, "missing_requirements": [], "suggestions": []}
    
    def generate_tailored_resume(self, user_data: Dict[str, Any], job_description: str) -> str:
        """Generate resume tailored to specific job"""
        return self.generate_resume(user_data, job_description)
    
    def generate_enhanced_resume(self, user_data: Dict[str, Any]) -> str:
        """Generate enhanced resume with AI improvements"""
        enhancements = user_data.get('ai_enhancements', [])
        style = user_data.get('resume_style', 'Professional ATS-Optimized')
        
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
        
        Create a professional resume with:
        1. Compelling professional summary
        2. Quantified achievements with metrics
        3. Industry-specific keywords
        4. ATS-optimized formatting
        5. Strong action verbs
        6. Relevant technical skills highlighted
        
        Format for both ATS and human readability.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert resume writer who creates compelling, ATS-optimized resumes with quantified achievements."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=2000, temperature=0.6)
    
    def evaluate_resume_quality(self, resume_content: str, job_description: str = "") -> Dict[str, Any]:
        """Evaluate resume quality and ATS compatibility"""
        prompt = f"""
        Evaluate this resume for quality and ATS compatibility:
        
        Resume:
        {resume_content}
        
        {"Target Job: " + job_description if job_description else "General evaluation"}
        
        Analyze and score (0-100):
        1. ATS compatibility
        2. Keyword optimization
        3. Content quality
        4. Format structure
        5. Achievement quantification
          Return as JSON: {{
            "overall_score": number,
            "checks": {{
                "ATS Compatible": boolean,
                "Keywords Optimized": boolean, 
                "Achievements Quantified": boolean,
                "Professional Format": boolean,
                "Contact Info Complete": boolean
            }},
            "suggestions": ["improvement1", "improvement2"]
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert resume evaluator who provides detailed quality analysis."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1000, temperature=0.4)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "overall_score": 85,
                "checks": {
                    "ATS Compatible": True,
                    "Keywords Optimized": True,
                    "Achievements Quantified": False,
                    "Professional Format": True,
                    "Contact Info Complete": True
                },
                "suggestions": ["Add quantified achievements", "Include more industry keywords"]
            }
    
    def optimize_resume_further(self, resume_content: str, user_data: Dict[str, Any]) -> str:
        """Further optimize resume with advanced AI techniques"""
        prompt = f"""
        Further optimize this resume using advanced techniques:
        
        Current Resume:
        {resume_content}
        
        User Profile: {user_data.get('title', 'Professional')} with skills in {', '.join(user_data.get('skills', [])[:5])}
        
        Apply advanced optimizations:
        1. Add specific metrics and percentages
        2. Use stronger action verbs
        3. Include industry buzzwords
        4. Improve readability and flow
        5. Enhance achievement statements
        6. Optimize for senior-level positions
        
        Return the highly optimized resume.
        """
        
        messages = [
            {"role": "system", "content": "You are a senior resume optimization expert who creates executive-level resumes."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=2000, temperature=0.5)
    
    def analyze_resume_job_match(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        """Analyze how well resume matches job requirements"""
        prompt = f"""
        Analyze the match between this resume and job description:
        
        Resume:
        {resume_content}
        
        Job Description:
        {job_description}
        
        Provide detailed analysis:
        1. Match percentage (0-100)
        2. Number of matching keywords
        3. ATS compatibility score
        4. Specific improvement suggestions
        5. Missing keywords to add
          Return as JSON: {{
            "match_percentage": number,
            "keyword_matches": number,
            "ats_score": number,
            "suggestions": ["suggestion1", "suggestion2"],
            "missing_keywords": ["keyword1", "keyword2"]
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert at analyzing resume-job fit and ATS optimization."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1000, temperature=0.4)
        
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
                "ats_score": 82,
                "suggestions": ["Add more specific keywords", "Include quantified achievements"],
                "missing_keywords": ["leadership", "project management"]
            }
    
    def generate_enhanced_cover_letter(self, user_data: Dict[str, Any], job_description: str, 
                                     company_name: str, tone: str = "Professional") -> str:
        """Generate enhanced cover letter with specified tone"""
        prompt = f"""
        Write a compelling, {tone.lower()} cover letter for:
        
        Candidate: {user_data.get('name', 'Candidate')}
        Current Title: {user_data.get('title', 'Professional')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        
        Target Company: {company_name}
        Job Description: {job_description}
        Tone: {tone}
        
        Create a personalized cover letter that:
        1. Opens with a compelling hook specific to the company
        2. Demonstrates clear understanding of the role
        3. Highlights most relevant experience and achievements
        4. Shows knowledge of company culture/values
        5. Includes specific examples and metrics
        6. Maintains {tone.lower()} tone throughout
        7. Closes with strong call to action
        8. Is 350-450 words
        
        Make it highly personalized and compelling for this specific opportunity.
        """
        
        messages = [
            {"role": "system", "content": f"You are an expert career counselor who writes compelling, {tone.lower()} cover letters that get interviews."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1500, temperature=0.7)
    
    def analyze_cover_letter_quality(self, cover_letter: str, job_description: str) -> Dict[str, Any]:
        """Analyze cover letter quality and effectiveness"""
        prompt = f"""
        Analyze this cover letter for quality and effectiveness:
        
        Cover Letter:
        {cover_letter}
        
        Target Job:
        {job_description}
        
        Evaluate (score 0-100):
        1. Overall quality and impact
        2. Personalization level
        3. Relevance to job requirements
        4. Professional tone
        5. Call to action strength
          Return as JSON: {{
            "overall_score": number,
            "personalization": number,
            "relevance": number,
            "tone_score": number,
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"],
            "suggestions": "Specific advice for enhancement"
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert cover letter evaluator who provides detailed quality analysis."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1000, temperature=0.5)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "overall_score": 85,
                "personalization": 80,
                "relevance": 88,
                "tone_score": 90,
                "strengths": ["Clear communication", "Relevant experience"],
                "improvements": ["Add more specific examples", "Strengthen opening"],
                "suggestions": "Include specific company research and quantified achievements."
            }
    
    def generate_alternative_cover_letter(self, user_data: Dict[str, Any], job_description: str, 
                                        company_name: str, alternative_tone: str) -> str:
        """Generate alternative cover letter with different tone"""
        return self.generate_enhanced_cover_letter(user_data, job_description, company_name, alternative_tone)
    
    def generate_role_specific_questions(self, job_description: str, company_name: str, 
                                       user_data: Dict[str, Any]) -> List[Dict]:
        """Generate role-specific interview questions"""
        prompt = f"""
        Generate 5 role-specific interview questions for this opportunity:
        
        Job Description: {job_description}
        Company: {company_name}
        
        Candidate Background:
        - Title: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', [])[:5])}
        - Experience: {user_data.get('experience', 'Professional experience')}
        
        Create questions that:
        1. Are specific to this role and company
        2. Test relevant technical/functional skills
        3. Assess cultural fit for the company
        4. Evaluate problem-solving abilities
        5. Are appropriate for the experience level
        
        Return as JSON array: [{"question": "...", "type": "...", "focus": "..."}]
        """
        
        messages = [
            {"role": "system", "content": "You are an expert interviewer who creates role-specific, company-tailored questions."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1200, temperature=0.7)
        
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return [
                {"question": f"Why are you interested in this role at {company_name}?", "type": "motivation", "focus": "company_fit"},
                {"question": "Describe your experience with the key technologies mentioned in the job description.", "type": "technical", "focus": "skills"},
                {"question": "How would you approach solving the main challenges mentioned in this role?", "type": "problem_solving", "focus": "approach"},
                {"question": "Tell me about a time you had to learn a new skill quickly.", "type": "behavioral", "focus": "adaptability"},
                {"question": "Where do you see yourself growing in this position?", "type": "career", "focus": "growth"}
            ]
    
    def generate_answer_tips(self, question: str, user_data: Dict[str, Any]) -> str:
        """Generate tips for answering specific interview questions"""
        prompt = f"""
        Provide expert tips for answering this interview question:
        
        Question: {question}
        
        Candidate Profile:
        - Title: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', [])[:3])}
        - Experience: {user_data.get('experience', 'Professional experience')}
        
        Provide:
        1. Key points to cover in the answer
        2. Specific examples they could use based on their background
        3. Common mistakes to avoid
        4. Structure for the response (e.g., STAR method)
        5. How to tie back to their skills and experience
        
        Make it actionable and specific to their profile.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert interview coach who provides specific, actionable answer strategies."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=800, temperature=0.6)
    
    def analyze_profile_strength(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user profile strength for job search"""
        prompt = f"""
        Analyze this professional profile for job search readiness:
        
        Profile:
        - Name: {user_data.get('name', 'Professional')}
        - Title: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', []))}
        - Experience: {user_data.get('experience', 'Professional experience')}
        - Education: {user_data.get('education', 'Education background')}
        
        Evaluate:
        1. Profile completeness (0-100)
        2. Market competitiveness
        3. Skills relevance to current market
        4. Areas for improvement
        5. Specific suggestions for enhancement
          Return as JSON: {{
            "score": number,
            "completeness": number,
            "market_relevance": number,
            "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert career analyst who evaluates professional profiles for market readiness."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1000, temperature=0.5)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "score": 75,
                "completeness": 80,
                "market_relevance": 85,
                "suggestions": [
                    "Add more quantified achievements",
                    "Include industry certifications",
                    "Expand technical skill set"
                ]
            }
    
    def analyze_job_matches(self, jobs: List[Dict], user_data: Dict[str, Any]) -> List[Dict]:
        """Enhance job listings with AI match analysis"""
        enhanced_jobs = []
        
        for job in jobs:
            try:
                prompt = f"""
                Analyze this job match for the candidate:
                
                Job: {job.get('title', 'Job Title')} at {job.get('company', 'Company')}
                Description: {job.get('description', 'Job description')[:500]}
                
                Candidate:
                - Title: {user_data.get('title', 'Professional')}
                - Skills: {', '.join(user_data.get('skills', [])[:8])}
                - Experience: {user_data.get('experience', 'Professional experience')}
                
                Return only: {{"skills_match": percentage, "experience_match": percentage, "overall_fit": percentage}}
                """
                
                messages = [
                    {"role": "system", "content": "You are an expert job matcher. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ]
                
                response = self._make_request(messages, max_tokens=200, temperature=0.3)
                
                try:
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    if json_start != -1 and json_end != 0:
                        json_str = response[json_start:json_end]
                        match_data = json.loads(json_str)
                        job.update(match_data)
                except:
                    job.update({"skills_match": 75, "experience_match": 80, "overall_fit": 77})
                
                enhanced_jobs.append(job)
            except:
                enhanced_jobs.append(job)
        
        return enhanced_jobs
    
    def generate_career_suggestions(self, user_data: Dict[str, Any], search_keywords: str) -> str:
        prompt = f"""
        Generate career suggestions based on this search and profile:
        
        Search Keywords: {search_keywords}
        
        User Profile:
        - Current Role: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', []))}
        - Experience: {user_data.get('experience', 'Professional experience')}
        
        Provide:
        1. Alternative job titles to search for
        2. Related industries to explore
        3. Skills to develop for better matches
        4. Companies known for hiring in this area
        5. Networking suggestions
        
        Make it actionable and specific.
        """
        
        messages = [
            {"role": "system", "content": "You are a career strategist who provides targeted job search advice."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1200, temperature=0.7)
    
    def generate_alert_preview(self, alert_keywords: str, user_data: Dict[str, Any]) -> str:
        prompt = f"""
        Generate a preview of job alert results for:
        
        Alert Keywords: {alert_keywords}
        
        User Profile: {user_data.get('title', 'Professional')} with {len(user_data.get('skills', []))} skills
        
        Show:
        1. Types of jobs this alert would find
        2. Typical companies that would match
        3. Expected salary ranges
        4. Required qualifications
        5. How often alerts might trigger
        
        Make it realistic and helpful.
        """
        
        messages = [
            {"role": "system", "content": "You are a job market analyst who provides realistic job alert previews."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=800, temperature=0.6)
    
    def generate_comprehensive_career_strategy(self, user_data: Dict[str, Any], 
                                             career_goals: List[str], time_horizon: str) -> str:
        prompt = f"""
        Create a comprehensive career strategy for:
        
        Profile:
        - Current Role: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', []))}
        - Experience: {user_data.get('experience', 'Professional experience')}
        
        Career Goals: {', '.join(career_goals)}
        Timeline: {time_horizon}
        
        Create a detailed strategy including:
        1. Step-by-step career roadmap
        2. Skills development plan
        3. Networking strategy
        4. Target companies and roles
        5. Salary progression expectations
        6. Key milestones and timelines
        7. Risk mitigation strategies
        8. Alternative pathways
        
        Make it specific, actionable, and realistic for the timeline.
        """
        
        messages = [
            {"role": "system", "content": "You are a senior career strategist who creates comprehensive, actionable career plans."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=2000, temperature=0.6)
    
    def analyze_career_potential(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Analyze career potential for:
        
        Profile:
        - Current Role: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', []))}
        - Experience: {user_data.get('experience', 'Professional experience')}
        
        Analyze:
        1. Market demand for their role (0-100)
        2. Salary growth potential (0-100)
        3. Skill relevance to future trends (0-100)
        4. Key growth areas to focus on
        5. Market trends affecting their field
          Return as JSON: {{
            "market_demand": number,
            "salary_growth": number,
            "skill_relevance": number,
            "growth_areas": ["area1", "area2", "area3"],
            "market_trends": ["trend1", "trend2"]
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are a career market analyst who evaluates professional potential and trends."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1000, temperature=0.5)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "market_demand": 85,
                "salary_growth": 78,                "skill_relevance": 90,
                "growth_areas": ["Leadership skills", "Digital transformation", "Data analysis"],
                "market_trends": ["Remote work adoption", "AI integration", "Skills-based hiring"]
            }
    
    def generate_learning_path(self, user_data: Dict[str, Any]) -> str:
        """Generate personalized learning path"""
        prompt = f"""
        Create a personalized learning path for:
        
        Current Profile:
        - Role: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', []))}
        - Experience: {user_data.get('experience', 'Professional experience')}
        
        Recommend:
        1. Priority skills to develop
        2. Specific courses and certifications
        3. Learning timeline (3-6 months)
        4. Free and paid resources
        5. Hands-on projects to practice
        6. How skills align with career goals
        
        Focus on high-impact, career-advancing skills.
        """
        
        messages = [
            {"role": "system", "content": "You are a learning strategist who creates targeted skill development plans."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1500, temperature=0.6)
    
    def get_deployment_quick_start(self, hosting_option: str) -> Dict[str, str]:
        """Get quick start information for deployment platforms"""
        quick_starts = {
            "GitHub Pages (Recommended)": {
                "url": "https://pages.github.com/",
                "steps": """
### 🚀 GitHub Pages Quick Start
1. **Create a GitHub account** if you don't have one
2. **Create a new repository** named `your-username.github.io`
3. **Upload your HTML file** (rename it to `index.html`)
4. **Go to Settings > Pages** in your repository
5. **Select source branch** (usually `main`)
6. **Your site will be live** at `https://your-username.github.io`
                """,
                "tip": "💡 GitHub Pages is free and perfect for portfolio hosting!"
            },
            "Netlify (Easy Deploy)": {
                "url": "https://www.netlify.com/",
                "steps": """
### 🚀 Netlify Quick Start
1. **Visit Netlify.com** and create an account
2. **Drag and drop** your HTML file into the deploy area
3. **Get instant URL** - your site is live immediately!
4. **Optional:** Connect GitHub for automatic updates
5. **Custom domain:** Add your own domain in site settings
                """,
                "tip": "💡 Netlify offers drag-and-drop deployment in seconds!"
            },
            "Vercel (Developer Friendly)": {
                "url": "https://vercel.com/",
                "steps": """
### 🚀 Vercel Quick Start
1. **Visit Vercel.com** and sign up with GitHub
2. **Import your repository** or upload files
3. **Automatic deployment** - builds and deploys instantly
4. **Get production URL** with HTTPS included
5. **Zero config** - works out of the box
                """,
                "tip": "💡 Vercel is perfect for developers with GitHub integration!"
            },
            "Custom Domain Setup": {
                "url": "https://domains.google.com/",
                "steps": """
### 🚀 Custom Domain Quick Start
1. **Purchase a domain** from Google Domains or similar
2. **Choose a hosting service** (GitHub Pages, Netlify, etc.)
3. **Configure DNS settings** to point to your host
4. **Upload your website files** to the hosting service
5. **Enable HTTPS** for security and SEO
                """,
                "tip": "💡 Custom domains give your portfolio a professional look!"
            }
        }
        
        return quick_starts.get(hosting_option, {
            "url": "https://github.com/",
            "steps": "### General deployment steps would go here",
            "tip": "💡 Choose a hosting platform that fits your needs!"
        })

    def generate_comprehensive_qa_strategy(self, user_data: Dict[str, Any], 
                                          job_description: str, company_name: str) -> str:
        """Generate comprehensive QA strategy for interviews"""
        prompt = f"""
        Create a comprehensive QA strategy for:
        
        Candidate Profile:
        - Role: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', [])[:5])}
        - Experience Level: {user_data.get('experience', 'Professional experience')}
        
        Target Role: {user_data.get('title', 'Professional')}
        Job Description: {job_description}
        Company: {company_name}
        
        Strategy Goals:
        1. Identify key focus areas for QA
        2. Develop targeted questions for each area
        3. Create a scoring rubric for responses
        4. Suggest ideal answer elements
        5. Recommend follow-up questions for depth
        6. Highlight red flags to watch for
        
        Make it detailed, structured, and tailored to the candidate and role.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an expert interview strategist who creates detailed, role-specific interview guides."
            },
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1500, temperature=0.6)
    
    def generate_candidate_scorecard(self, interview_qa: List[Dict], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a scorecard for candidate evaluation"""
        prompt = f"""
        Create a detailed scorecard for evaluating this candidate:
        
        Candidate Profile:
        - Name: {user_data.get('name', 'Candidate')}
        - Applied Role: {user_data.get('title', 'Professional')}
        - Skills: {', '.join(user_data.get('skills', []))}
        - Experience: {user_data.get('experience', 'Professional experience')}
        
        Interview Q&A:
        {json.dumps(interview_qa, indent=2)}
        
        Scorecard Sections:
        1. Overall impression
        2. Communication skills
        3. Technical expertise
        4. Problem-solving ability
        5. Cultural fit
        6. Strengths and weaknesses
        7. Recommended next steps
        
        Use a clear, structured format with ratings and comments.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an expert in candidate evaluation, providing detailed and objective scorecards."
            },
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
                "overall_impression": "Positive",
                "communication_skills": "Strong",
                "technical_expertise": "Proficient",
                "problem_solving": "Excellent",
                "cultural_fit": "Good",
                "strengths": ["Relevant experience", "Strong technical skills"],
                "weaknesses": ["Limited leadership experience"],
                "recommended_next_steps": "Proceed to final interview"
            }
    
    def parse_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text using AI to extract structured data
        """
        prompt = f"""
        Parse the following resume text and extract key information into a structured format.
        Focus on accuracy and completeness.
        
        Resume Text:
        {resume_text}
        
        Extract and return the following information as JSON:
        {{
            "name": "Full name of the person",
            "email": "Email address",
            "phone": "Phone number",
            "title": "Current or most recent job title/position",
            "skills": ["list", "of", "technical", "and", "soft", "skills"],
            "experience": "Brief summary of work experience",
            "education": "Educational background",
            "projects": ["list", "of", "notable", "projects"],
            "certifications": ["list", "of", "certifications"],
            "location": "Current location/address"
        }}
        
        Return only valid JSON. If information is not found, use empty string or empty array.
        """
        
        messages = [
            {
                "role": "system", 
                "content": "You are an expert resume parser. Extract information accurately and return only valid JSON."
            },
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1000, temperature=0.3)
        
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                parsed_data = json.loads(json_str)
                
                # Ensure required fields exist
                required_fields = ['name', 'email', 'phone', 'title', 'skills', 'experience', 'education']
                for field in required_fields:
                    if field not in parsed_data:
                        parsed_data[field] = '' if field != 'skills' else []
                
                return parsed_data
        except Exception as e:
            # Fallback parsing if AI fails
            return self._fallback_resume_parsing(resume_text)
    
    def _fallback_resume_parsing(self, text: str) -> Dict[str, Any]:
        """
        Fallback method for basic resume parsing using regex patterns
        """
        import re
        
        data = {
            'name': '',
            'email': '',
            'phone': '',
            'title': '',
            'skills': [],
            'experience': '',
            'education': '',
            'projects': [],
            'certifications': [],
            'location': ''
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            data['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            data['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        # Extract name (usually in first few lines)
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and not any(char.isdigit() for char in line) and '@' not in line:
                if len(line.split()) <= 4 and len(line) > 2:
                    data['name'] = line
                    break
        
        # Extract common skills
        skill_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'SQL',
            'Machine Learning', 'Data Analysis', 'Project Management', 'Leadership',
            'Communication', 'Problem Solving', 'Teamwork', 'Git', 'AWS', 'Docker'
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        data['skills'] = found_skills
        
        # Basic experience extraction (get text around "experience" keyword)
        exp_pattern = r'(?i)(experience|work history|employment)(.*?)(?=education|skills|projects|$)'
        exp_match = re.search(exp_pattern, text, re.DOTALL)
        if exp_match:
            data['experience'] = exp_match.group(2).strip()[:500]  # Limit length
        
        # Basic education extraction
        edu_pattern = r'(?i)(education|academic|degree)(.*?)(?=experience|skills|projects|$)'
        edu_match = re.search(edu_pattern, text, re.DOTALL)
        if edu_match:
            data['education'] = edu_match.group(2).strip()[:300]  # Limit length
        
        return data