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
    
    def search_unknown_terms(self, text: str, context: str = "") -> Dict[str, str]:
        """Search for unknown or technical terms and return explanations"""
        if not search:
            return {}
            
        # Extract potentially unknown terms (technical terms, company names, etc.)
        unknown_terms = self._extract_unknown_terms(text)
        search_results = {}
        
        for term in unknown_terms[:5]:  # Limit to 5 terms to avoid rate limiting
            try:                # Search for the term
                search_query = f"{term} definition meaning {context}" if context else f"{term} definition meaning"
                results = list(search(search_query, num_results=2, sleep_interval=2))
                
                if results:
                    # Get brief explanation using AI
                    explanation = self._get_term_explanation(term, search_query)
                    if explanation and len(explanation) > 10:
                        search_results[term] = explanation
                        
            except Exception as e:
                print(f"Search error for term '{term}': {e}")
                continue
                
        return search_results
    
    def _extract_unknown_terms(self, text: str) -> List[str]:
        """Extract potentially unknown terms from text"""
        # Look for technical terms, acronyms, company names, etc.
        patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms like AI, ML, API, AWS
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b',  # CamelCase terms like JavaScript
            r'\b\w+(?:\.js|\.py|\.net|\.io|\.com)\b',  # Technology extensions
            r'\b(?:React|Angular|Vue|Django|Flask|Laravel|Spring|Docker|Kubernetes|TensorFlow|PyTorch)\b',  # Common tech terms
        ]
        
        terms = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.update(matches)
            
        # Filter out common words and very short terms
        common_words = {'The', 'This', 'That', 'And', 'Or', 'But', 'For', 'In', 'On', 'At', 'To', 'Of', 'API', 'UI', 'UX'}
        filtered_terms = []
        for term in terms:
            if (term not in common_words and 
                len(term) > 2 and 
                not term.isdigit() and 
                term.upper() not in ['CEO', 'CTO', 'HR', 'IT']):
                filtered_terms.append(term)
                
        return filtered_terms[:10]  # Limit to 10 terms
    
    def _get_term_explanation(self, term: str, search_query: str) -> str:
        """Get a brief explanation of a term using AI"""
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
        """Generate enhanced cover letter with specified tone and Google search integration"""
        
        # Search for unknown terms in job description for better understanding
        search_results = self.search_unknown_terms(job_description, f"{company_name} job requirements")
        
        # Enhance prompt with search results
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
        """Generate enhanced resume with AI improvements and Google search integration"""
        enhancements = user_data.get('ai_enhancements', [])
        style = user_data.get('resume_style', 'Professional ATS-Optimized')
        skills_input = user_data.get('skills_input', '')
        
        # Search for unknown terms in skills and experience for better understanding
        search_context_text = f"{skills_input} {user_data.get('experience', '')} {user_data.get('title', '')}"
        search_results = self.search_unknown_terms(search_context_text, "career skills technology")
        
        # Enhance prompt with search results
        search_context = ""
        if search_results:
            search_context = "\n\nResearched technical context:\n"
            for term, explanation in search_results.items():
                search_context += f"- {term}: {explanation}\n"
        
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
        
        Create a professional resume with:
        1. Compelling professional summary using current industry terminology
        2. Quantified achievements with metrics
        3. Industry-specific keywords (informed by research above)
        4. ATS-optimized formatting
        5. Strong action verbs
        6. Relevant technical skills highlighted with proper context
        7. Current industry trends and terminology integration
        
        Format for both ATS and human readability, ensuring technical terms are used correctly.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert resume writer who creates compelling, ATS-optimized resumes with quantified achievements and current industry knowledge."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=2000, temperature=0.6)

    def generate_tailored_resume(self, user_data: Dict[str, Any], job_description: str) -> str:
        """Generate resume tailored to specific job with Google search integration"""
        # Search for unknown terms in job description for better understanding
        search_results = self.search_unknown_terms(job_description, "job requirements career skills")
        
        # Enhance the user data with search context
        enhanced_user_data = user_data.copy()
        if search_results:
            # Add search context to the job description
            search_context = "\n\nResearched job context:\n"
            for term, explanation in search_results.items():
                search_context += f"- {term}: {explanation}\n"
            enhanced_job_description = job_description + search_context
        else:
            enhanced_job_description = job_description
            
        return self.generate_resume(enhanced_user_data, enhanced_job_description)

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

    def generate_portfolio(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate professional portfolio content"""
        prompt = f"""
        Create a professional portfolio for:
        
        Name: {user_data.get('name', 'Professional')}
        Title: {user_data.get('title', 'Professional')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        Education: {user_data.get('education', '')}
        
        Generate content for these portfolio sections:
        1. Professional summary (2-3 compelling sentences)
        2. About section (150-200 words, engaging and personal)
        3. Skills organized by category
        4. Project highlights (3-4 impressive projects based on skills)
        5. Call-to-action statement
        
        Make it professional, engaging, and showcase expertise. Return as JSON with keys: summary, about, skills_categories, projects, cta
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

    def generate_enhanced_portfolio(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced portfolio with AI improvements"""
        prompt = f"""
        Create an enhanced professional portfolio for:
        
        Name: {user_data.get('name', 'Professional')}
        Title: {user_data.get('title', 'Professional')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        Portfolio Style: {user_data.get('portfolio_style', 'Modern Professional')}
        
        Generate enhanced portfolio content with:
        1. Professional headline that captures attention
        2. Compelling about section (150-200 words)
        3. Skills organized by categories
        4. 3-4 impressive project examples based on skills
        5. Professional achievements
        6. Call-to-action statements
          Return as JSON with keys: headline, about, skills_categories, projects, achievements, cta
        """
        
        messages = [
            {"role": "system", "content": "You are an expert portfolio developer who creates impressive professional portfolios. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1500, temperature=0.8)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "headline": f"Experienced {user_data.get('title', 'Professional')}",
                "about": f"Professional with extensive experience in {user_data.get('title', 'their field')}.",
                "skills_categories": {"Technical": user_data.get('skills', [])},
                "projects": [],
                "achievements": ["Delivered successful projects", "Strong problem-solving abilities"],
                "cta": "Let's collaborate on your next project!"
            }

    def enhance_portfolio_content(self, portfolio_content: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance existing portfolio content with AI improvements"""
        prompt = f"""
        Enhance the following portfolio content with more compelling and professional language:
        
        Current Portfolio Content:
        {json.dumps(portfolio_content, indent=2)}
        
        User Profile:
        Name: {user_data.get('name', 'Professional')}
        Title: {user_data.get('title', 'Professional')}
        Skills: {', '.join(user_data.get('skills', []))}
        Experience: {user_data.get('experience', 'Professional experience')}
        
        Enhance the content to:
        1. Make headlines more attention-grabbing
        2. Improve about section with better storytelling
        3. Add more impressive project descriptions
        4. Include quantified achievements
        5. Make call-to-action more compelling
        6. Add industry-specific keywords
        
        Return the enhanced content as JSON with the same structure but improved content.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert portfolio enhancer who creates compelling professional content. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1500, temperature=0.7)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            # Return original content if enhancement fails
            return portfolio_content

    def generate_deployment_guide(self, hosting_platform: str, user_data: Dict[str, Any]) -> str:
        """Generate deployment guide for specified hosting platform"""
        prompt = f"""
        Create a comprehensive deployment guide for hosting a portfolio website on {hosting_platform}.
        
        User Profile: {user_data.get('name', 'User')} - {user_data.get('title', 'Professional')}
        
        Provide a detailed guide including:
        1. Step-by-step deployment instructions
        2. Prerequisites and account setup
        3. File preparation tips
        4. Custom domain configuration (if applicable)
        5. Best practices for optimization
        6. Troubleshooting common issues
        7. Performance optimization tips
        
        Make it beginner-friendly but comprehensive. Format in markdown.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert web deployment consultant who creates clear, actionable guides."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1500, temperature=0.6)

    def get_deployment_quick_start(self, hosting_platform: str) -> Dict[str, str]:
        """Get quick start information for deployment platform"""
        quick_start_guides = {
            "GitHub Pages (Recommended)": {
                "steps": """
### 🚀 GitHub Pages Quick Start

1. **Create Repository**: Create a new public repository named `your-username.github.io`
2. **Upload Files**: Upload your HTML file (rename to `index.html`)
3. **Enable Pages**: Go to Settings → Pages → Source: Deploy from branch
4. **Select Branch**: Choose `main` branch and `/ (root)` folder
5. **Access Site**: Your portfolio will be live at `https://your-username.github.io`

**Pro Tips:**
- Use a custom domain by adding a CNAME file
- Enable HTTPS in repository settings
- Use GitHub Actions for automatic deployments
                """,
                "tip": "💡 GitHub Pages is free and perfect for portfolios! Your site updates automatically when you push changes."
            },
            "Netlify (Easy Deploy)": {
                "steps": """
### 🚀 Netlify Quick Start

1. **Sign Up**: Create a free Netlify account
2. **Drag & Drop**: Simply drag your HTML file to the Netlify deploy area
3. **Instant Deploy**: Your site goes live immediately with a random URL
4. **Custom Domain**: Add your own domain in Site Settings → Domain Management
5. **SSL**: HTTPS is enabled automatically

**Pro Tips:**
- Connect to GitHub for continuous deployment
- Use Netlify Forms for contact functionality
- Enable branch previews for testing
                """,
                "tip": "💡 Netlify offers instant deployment with drag-and-drop simplicity. Perfect for quick portfolio launches!"
            },
            "Vercel (Developer Friendly)": {
                "steps": """
### 🚀 Vercel Quick Start

1. **Install CLI**: `npm i -g vercel` or use web interface
2. **Deploy**: Run `vercel` in your project folder or drag files to dashboard
3. **Configure**: Set up custom domain and environment variables
4. **Optimize**: Vercel automatically optimizes your site
5. **Monitor**: Use analytics to track performance

**Pro Tips:**
- Integrate with Git for automatic deployments
- Use Vercel Functions for backend features
- Enable Web Analytics for insights
                """,
                "tip": "💡 Vercel provides excellent performance optimization and developer experience. Great for modern portfolios!"
            },
            "Custom Domain Setup": {
                "steps": """
### 🚀 Custom Domain Quick Start

1. **Purchase Domain**: Buy a domain from providers like Google Domains, Namecheap, or GoDaddy
2. **Configure DNS**: Point your domain to your hosting service:
   - For GitHub Pages: Add CNAME record pointing to `your-username.github.io`
   - For Netlify: Add CNAME record or use Netlify nameservers
   - For Vercel: Add CNAME record or use Vercel nameservers
3. **Enable HTTPS**: Most platforms enable SSL automatically
4. **Test**: Verify your domain works and redirects properly

**Pro Tips:**
- Use a .com domain for better professional credibility
- Set up email forwarding for professional communication
- Consider domain privacy protection
                """,
                "tip": "💡 A custom domain makes your portfolio look more professional and memorable to employers and clients!"
            }
        }
        
        return quick_start_guides.get(hosting_platform, {
            "steps": "Please select a valid hosting platform for detailed instructions.",
            "tip": "Choose GitHub Pages for free hosting, Netlify for easy deployment, or Vercel for advanced features."
        })

    def evaluate_resume_quality(self, resume_content: str, job_description: str = "") -> Dict[str, Any]:
        """Evaluate resume quality and ATS compatibility"""
        context = f"\n\nTarget Job: {job_description}" if job_description else ""
        
        prompt = f"""
        Evaluate this resume for quality and ATS compatibility:
        
        Resume Content:
        {resume_content}
        {context}
        
        Provide evaluation on:
        1. Overall ATS compatibility score (0-100)
        2. Keyword optimization
        3. Format and structure
        4. Content quality
        5. Quantified achievements
        6. Skills relevance
        7. Professional language
        
        Return as JSON with:
        {{
            "overall_score": 85,
            "checks": {{
                "ATS Format": true,
                "Keywords Present": true,
                "Quantified Results": false,
                "Action Verbs": true,
                "Skills Match": true,
                "Professional Tone": true
            }},
            "suggestions": ["Add quantified achievements", "Include more keywords"]
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert resume evaluator and ATS specialist. Return only valid JSON."},
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
                "overall_score": 75,
                "checks": {
                    "ATS Format": True,
                    "Keywords Present": True,
                    "Quantified Results": False,
                    "Action Verbs": True,
                    "Skills Match": True,
                    "Professional Tone": True
                },
                "suggestions": ["Review and optimize content", "Add more specific achievements"]
            }

    def optimize_resume_further(self, resume_content: str, user_data: Dict[str, Any]) -> str:
        """Further optimize resume with AI enhancements"""
        prompt = f"""
        Further optimize this resume to make it more compelling and ATS-friendly:
        
        Current Resume:
        {resume_content}
        
        User Profile:
        Skills: {', '.join(user_data.get('skills', []))}
        Title: {user_data.get('title', 'Professional')}
        
        Enhance by:
        1. Adding more powerful action verbs
        2. Including quantified achievements where possible
        3. Optimizing keyword density
        4. Improving professional language
        5. Better formatting for ATS systems
        6. Adding industry-specific terminology
        7. Strengthening impact statements
        
        Return the optimized resume content.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert resume optimizer who creates compelling, ATS-optimized resumes."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=2000, temperature=0.6)

    def analyze_resume_job_match(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        """Analyze how well resume matches job requirements"""
        prompt = f"""
        Analyze how well this resume matches the job requirements:
        
        Resume:
        {resume_content}
        
        Job Description:
        {job_description}
        
        Provide analysis with:
        1. Match percentage (0-100)
        2. Number of matching keywords
        3. Missing key requirements
        4. Suggestions for improvement
        5. Strengths that align with job
        
        Return as JSON:
        {{
            "match_percentage": 85,
            "keyword_matches": 12,
            "missing_requirements": ["Python", "Machine Learning"],
            "suggestions": ["Add Python experience", "Highlight ML projects"],
            "strengths": ["Strong leadership experience", "Relevant industry background"]
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert job match analyzer. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1000, temperature=0.3)
        
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
                "missing_requirements": ["Check job requirements"],
                "suggestions": ["Tailor resume to job description"],
                "strengths": ["Professional experience", "Relevant skills"]
            }

    def health_check(self) -> bool:
        """Check if the Groq service is accessible"""
        test_messages = [
            {"role": "user", "content": "Hello, are you working?"}
        ]
        
        response = self._make_request(test_messages, max_tokens=50, temperature=0.1)
        return not response.startswith("❌")
    
    def parse_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text using AI to extract structured data"""
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
        """Fallback method for basic resume parsing using regex patterns"""
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
        
        # Basic experience extraction
        exp_pattern = r'(?i)(experience|work history|employment)(.*?)(?=education|skills|projects|$)'
        exp_match = re.search(exp_pattern, text, re.DOTALL)
        if exp_match:
            data['experience'] = exp_match.group(2).strip()[:500]
        
        # Basic education extraction
        edu_pattern = r'(?i)(education|academic|degree)(.*?)(?=experience|skills|projects|$)'
        edu_match = re.search(edu_pattern, text, re.DOTALL)
        if edu_match:
            data['education'] = edu_match.group(2).strip()[:300]
        
        return data

    def analyze_cover_letter_quality(self, cover_letter: str, job_description: str = "") -> Dict[str, Any]:
        """Analyze cover letter quality and provide feedback"""
        prompt = f"""
        Analyze this cover letter for quality and effectiveness:
        
        Cover Letter:
        {cover_letter}
        
        Job Description:
        {job_description}
        
        Evaluate and return JSON with:
        {{
            "engagement_score": 88,
            "relevance_score": 85,
            "checks": {{
                "Professional tone": true,
                "Specific examples": true,
                "Clear call to action": true,
                "Proper length": true,
                "Keywords included": false
            }}
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert career counselor analyzing cover letters. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=500, temperature=0.3)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            return {
                "engagement_score": 85,
                "relevance_score": 80,
                "checks": {
                    "Professional tone": True,
                    "Specific examples": True,
                    "Clear call to action": True,
                    "Proper length": True,
                    "Keywords included": True
                }
            }
