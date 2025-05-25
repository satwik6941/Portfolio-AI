from jinja2 import Template
import os
from datetime import datetime
from typing import Dict, List
from fpdf import FPDF
import io

class PortfolioGenerator:
    def __init__(self):
        self.template_dir = "templates"
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
    
    def generate_html_portfolio(self, portfolio_data: Dict) -> str:
        """Generate complete HTML portfolio website"""
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name }} - Portfolio</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        header {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(15px);
            padding: 1rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        nav ul {
            list-style: none;
            display: flex;
            justify-content: center;
            gap: 2rem;
        }
        
        nav a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            transition: all 0.3s ease;
        }
        
        nav a:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        .hero {
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
        }
        
        .hero h1 {
            font-size: 4rem;
            color: white;
            margin-bottom: 1rem;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .hero p {
            font-size: 1.5rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 2rem;
        }
        
        .btn {
            display: inline-block;
            padding: 1rem 2.5rem;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #333;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(255, 215, 0, 0.5);
        }
        
        .section {
            padding: 100px 0;
            background: white;
        }
        
        .section:nth-child(even) {
            background: #f8f9fa;
        }
        
        .section h2 {
            text-align: center;
            margin-bottom: 4rem;
            font-size: 3rem;
            color: #333;
            position: relative;
        }
        
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }
        
        .skill-card {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .skill-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.2);
        }
        
        .skill-card i {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .experience-item {
            background: white;
            padding: 2.5rem;
            margin-bottom: 3rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .experience-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(102, 126, 234, 0.2);
        }
        
        .experience-item h3 {
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 1.4rem;
        }
        
        .experience-item .company {
            color: #666;
            font-style: italic;
            margin-bottom: 1rem;
            font-weight: 500;
        }
        
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }
            
            nav ul {
                flex-direction: column;
                gap: 1rem;
            }
            
            .skills-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <nav class="container">
            <ul>
                <li><a href="#hero"><i class="fas fa-home"></i> Home</a></li>
                <li><a href="#about"><i class="fas fa-user"></i> About</a></li>
                <li><a href="#skills"><i class="fas fa-cogs"></i> Skills</a></li>
                <li><a href="#experience"><i class="fas fa-briefcase"></i> Experience</a></li>
                <li><a href="#contact"><i class="fas fa-envelope"></i> Contact</a></li>
            </ul>
        </nav>
    </header>

    <section id="hero" class="hero">
        <div class="container">
            <h1>{{ name }}</h1>
            <p>{{ headline }}</p>
            <a href="#contact" class="btn"><i class="fas fa-paper-plane"></i> Get In Touch</a>
        </div>
    </section>

    <section id="about" class="section">
        <div class="container">
            <h2><i class="fas fa-user-circle"></i> About Me</h2>
            <div style="text-align: center; max-width: 800px; margin: 0 auto; font-size: 1.2rem;">
                <p>{{ about }}</p>
            </div>
        </div>
    </section>

    <section id="skills" class="section">
        <div class="container">
            <h2><i class="fas fa-star"></i> Skills & Expertise</h2>
            <div class="skills-grid">
                {% for skill in skills %}
                <div class="skill-card">
                    <i class="fas fa-code"></i>
                    <h3>{{ skill }}</h3>
                    <p>Proficient in {{ skill }} with hands-on experience</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <section id="experience" class="section">
        <div class="container">
            <h2><i class="fas fa-briefcase"></i> Professional Experience</h2>
            {% for exp in experience %}
            <div class="experience-item">
                <h3>{{ exp.title }}</h3>
                <div class="company">{{ exp.company }} | {{ exp.duration }}</div>
                <p>{{ exp.description }}</p>
            </div>
            {% endfor %}
        </div>
    </section>

    <section id="contact" class="section">
        <div class="container">
            <h2><i class="fas fa-envelope"></i> Contact Me</h2>
            <div style="text-align: center;">
                <p><strong>Email:</strong> {{ email }}</p>
                <p><strong>Phone:</strong> {{ phone }}</p>
                <p><strong>LinkedIn:</strong> <a href="{{ linkedin }}">{{ linkedin }}</a></p>
            </div>
        </div>
    </section>

    <script>
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    </script>
</body>
</html>        """
        
        template = Template(html_template)
        return template.render(**portfolio_data)
    
    def save_portfolio(self, html_content: str, filename: str = None) -> str:
        """Save portfolio HTML file"""
        if not filename:
            filename = f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = os.path.join(self.template_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_html(self, portfolio_data: Dict) -> str:
        """Generate complete HTML portfolio website using existing method"""
        return self.generate_html_portfolio(portfolio_data)

class ResumeGenerator:
    def __init__(self):
        pass
    
    def generate_pdf(self, resume_content: str, user_data: Dict = None) -> bytes:
        """Generate PDF resume using FPDF"""
        if user_data is None:
            user_data = {}
            
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Header with name and contact info
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, user_data.get('name', 'Resume'), 0, 1, 'C')
        
        pdf.set_font("Arial", size=10)
        contact_info = f"{user_data.get('email', '')} | {user_data.get('phone', '')} | {user_data.get('linkedin', '')}"
        pdf.cell(0, 8, contact_info, 0, 1, 'C')
        pdf.ln(5)
        
        # Resume content
        pdf.set_font("Arial", size=11)
        
        # Split content into lines and handle text wrapping
        lines = resume_content.split('\n')
        for line in lines:
            if line.strip():
                # Check if line is a header (usually all caps or contains colons)
                if line.isupper() or ':' in line[:20]:
                    pdf.set_font("Arial", "B", 12)
                    pdf.ln(3)
                else:
                    pdf.set_font("Arial", size=11)
                
                # Handle long lines
                if len(line) > 80:
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        if len(current_line + word) < 80:
                            current_line += word + " "
                        else:
                            if current_line:
                                pdf.cell(0, 6, current_line.strip(), 0, 1)
                            current_line = word + " "
                    if current_line:
                        pdf.cell(0, 6, current_line.strip(), 0, 1)
                else:
                    pdf.cell(0, 6, line, 0, 1)
            else:
                pdf.ln(3)
        
        # Convert to bytes - fix the encoding issue
        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            return pdf_output.encode('latin-1')
        else:
            return bytes(pdf_output)
    
    def format_resume_text(self, resume_content: str, user_data: Dict) -> str:
        """Format resume content into clean text format"""
        
        formatted_resume = f"""
{user_data.get('name', 'Your Name')}
{user_data.get('email', 'email@example.com')} | {user_data.get('phone', 'Phone Number')}
LinkedIn: {user_data.get('linkedin', 'linkedin.com/in/yourprofile')}

{resume_content}

---
Generated on {datetime.now().strftime('%B %d, %Y')}
        """
        
        return formatted_resume.strip()
    
    def save_resume(self, content: str, filename: str = None) -> str:
        """Save resume to text file"""
        if not filename:
            filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        filepath = filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath

class CoverLetterGenerator:
    def __init__(self):
        pass
    
    def format_cover_letter(self, content: str, user_data: Dict, company_name: str) -> str:
        """Format cover letter with proper business letter format"""
        
        formatted_letter = f"""
{user_data.get('name', 'Your Name')}
{user_data.get('email', 'email@example.com')}
{user_data.get('phone', 'Phone Number')}

{datetime.now().strftime('%B %d, %Y')}

Hiring Manager
{company_name}

Dear Hiring Manager,

{content}

Sincerely,
{user_data.get('name', 'Your Name')}
        """
        
        return formatted_letter.strip()
    
    def save_cover_letter(self, content: str, company_name: str, filename: str = None) -> str:
        """Save cover letter to file"""
        if not filename:
            safe_company = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"cover_letter_{safe_company}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename
