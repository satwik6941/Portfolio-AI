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
<body>    <header>
        <nav class="container">
            <ul>
                <li><a href="#hero"><i class="fas fa-home"></i> Home</a></li>
                <li><a href="#about"><i class="fas fa-user"></i> About</a></li>
                <li><a href="#skills"><i class="fas fa-cogs"></i> Skills</a></li>
                <li><a href="#projects"><i class="fas fa-code"></i> Projects</a></li>
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
    </section>    <section id="skills" class="section">
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

    <section id="projects" class="section">
        <div class="container">
            <h2><i class="fas fa-code"></i> Featured Projects</h2>
            {% for project in projects %}
            <div class="experience-item">
                <h3>{{ project.title }}</h3>
                <div class="company">{{ project.technologies }} | {{ project.duration }}</div>
                <p>{{ project.description }}</p>
            </div>
            {% endfor %}
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
        if not filename:
            filename = f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = os.path.join(self.template_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath

    def generate_html(self, portfolio_data: Dict) -> str:
        if 'portfolio_style' in portfolio_data or 'color_scheme' in portfolio_data:
            return self.generate_html_portfolio_enhanced(portfolio_data)
        else:
            return self.generate_html_portfolio(portfolio_data)

    def get_color_scheme_styles(self, color_scheme: str) -> Dict[str, str]:
        color_schemes = {
            "Blue Gradient (Professional)": {
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "primary_color": "#667eea",
                "secondary_color": "#764ba2",
                "accent_color": "#FFD700",
                "text_color": "#333333",
                "card_bg": "#ffffff",
                "section_bg": "#f8f9fa"
            },
            "Purple Gradient (Creative)": {
                "background": "linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%)",
                "primary_color": "#8B5CF6",
                "secondary_color": "#A855F7",
                "accent_color": "#F59E0B",
                "text_color": "#2D1B69",
                "card_bg": "#FAF5FF",
                "section_bg": "#F3E8FF"
            },
            "Green Gradient (Tech)": {
                "background": "linear-gradient(135deg, #10B981 0%, #059669 100%)",
                "primary_color": "#10B981",
                "secondary_color": "#059669",
                "accent_color": "#FBBF24",
                "text_color": "#064E3B",
                "card_bg": "#F0FDF4",
                "section_bg": "#ECFDF5"
            },
            "Orange Gradient (Energy)": {
                "background": "linear-gradient(135deg, #F97316 0%, #EA580C 100%)",
                "primary_color": "#F97316",
                "secondary_color": "#EA580C",
                "accent_color": "#3B82F6",
                "text_color": "#7C2D12",
                "card_bg": "#FFF7ED",
                "section_bg": "#FFEDD5"
            },
            "Dark Theme (Modern)": {
                "background": "linear-gradient(135deg, #1F2937 0%, #111827 100%)",
                "primary_color": "#6B7280",
                "secondary_color": "#374151",
                "accent_color": "#10B981",
                "text_color": "#F9FAFB",
                "card_bg": "#374151",
                "section_bg": "#1F2937"
            }
        }
        return color_schemes.get(color_scheme, color_schemes["Blue Gradient (Professional)"])

    def get_portfolio_style_layout(self, portfolio_style: str) -> str:
        if portfolio_style == "Creative Designer":
            return """
        /* Creative Designer Style */
        body {
            font-family: 'Arial Black', Impact, sans-serif !important;
        }
        .hero {
            clip-path: polygon(0 0, 100% 0, 85% 100%, 0% 100%) !important;
        }
        .hero h1 {
            font-family: 'Arial Black', sans-serif !important;
            font-weight: 900 !important;
            letter-spacing: 3px !important;
            text-transform: uppercase !important;
            transform: skew(-5deg) !important;
            font-size: 5rem !important;
        }
        .skill-card {
            border-left: 8px solid var(--primary-color) !important;
            transform: rotate(-2deg) !important;
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
            border-radius: 25px 5px 25px 5px !important;
            background: linear-gradient(45deg, var(--card-bg) 0%, rgba(255,255,255,0.9) 100%) !important;
        }
        .skill-card:nth-child(even) {
            transform: rotate(2deg) !important;
            border-left: none !important;
            border-right: 8px solid var(--accent-color) !important;
        }
        .skill-card:hover {
            transform: rotate(0deg) scale(1.05) !important;
        }
        .experience-item {
            border-radius: 30px 10px 30px 10px !important;
            position: relative !important;
            overflow: hidden !important;
            border: 3px solid var(--primary-color) !important;
        }
        .experience-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 8px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        }
        .section h2 {
            font-family: 'Arial Black', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            background: linear-gradient(45deg, var(--primary-color), var(--accent-color)) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
        }
        nav a {
            border-radius: 15px 5px 15px 5px !important;
            transform: skew(-5deg) !important;
        }
            """
        elif portfolio_style == "Tech Developer":
            return """
        /* Tech Developer Style */
        body {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
            background-attachment: fixed !important;
        }
        .hero {
            position: relative !important;
            background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 2px, transparent 2px) !important;
            background-size: 30px 30px !important;
        }
        .hero::before {
            content: '</>' !important;
            position: absolute !important;
            top: 20% !important;
            right: 10% !important;
            font-size: 15rem !important;
            opacity: 0.1 !important;
            font-family: 'Consolas', monospace !important;
            color: var(--accent-color) !important;
        }
        .hero h1 {
            font-family: 'Consolas', monospace !important;
            position: relative !important;
        }
        .hero h1::before {
            content: '$ ' !important;
            color: var(--accent-color) !important;
        }
        .skill-card {
            background: var(--card-bg) !important;
            border: 2px solid var(--primary-color) !important;
            border-radius: 8px !important;
            position: relative !important;
            overflow: hidden !important;
        }
        .skill-card::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 4px !important;
            height: 100% !important;
            background: var(--accent-color) !important;
        }
        .skill-card:hover {
            border-color: var(--accent-color) !important;
            box-shadow: 0 0 20px rgba(var(--primary-color), 0.3) !important;
        }
        .experience-item {
            border-left: 6px solid var(--primary-color) !important;
            margin-left: 30px !important;
            position: relative !important;
            background: var(--card-bg) !important;
            border-radius: 8px !important;
        }
        .experience-item::before {
            content: '' !important;
            position: absolute !important;
            left: -12px !important;
            top: 20px !important;
            width: 12px !important;
            height: 12px !important;
            background: var(--accent-color) !important;
            border-radius: 50% !important;
        }
        .section h2 {
            font-family: 'Consolas', monospace !important;
            position: relative !important;
        }
        .section h2::before {
            content: '// ' !important;
            color: var(--primary-color) !important;
        }
        nav {
            background: rgba(0,0,0,0.8) !important;
            backdrop-filter: blur(10px) !important;
        }
        nav a {
            font-family: 'Consolas', monospace !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            border-radius: 4px !important;
        }
            """
        elif portfolio_style == "Business Executive":
            return """
        /* Business Executive Style */
        body {
            font-family: 'Times New Roman', Georgia, serif !important;
        }
        .hero {
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), var(--background) !important;
        }
        .hero h1 {
            font-family: 'Times New Roman', serif !important;
            font-weight: 300 !important;
            font-size: 4.5rem !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
        }
        .hero p {
            font-style: italic !important;
            font-size: 1.8rem !important;
        }
        .skill-card, .experience-item {
            border-radius: 0 !important;
            border: 1px solid #e5e7eb !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            background: var(--card-bg) !important;
        }
        .skill-card {
            border-top: 4px solid var(--primary-color) !important;
        }
        .experience-item {
            border-left: 4px solid var(--primary_color) !important;
        }
        .section {
            padding: 150px 0 !important;
        }
        .section h2 {
            font-family: 'Times New Roman', serif !important;
            font-weight: 300 !important;
            font-size: 3.5rem !important;
            text-transform: uppercase !important;
            letter-spacing: 3px !important;
            border-bottom: 3px solid var(--primary-color) !important;
            padding-bottom: 20px !important;
            display: inline-block !important;
        }
        nav a {
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            border: 2px solid transparent !important;
            transition: all 0.3s ease !important;
        }
        nav a:hover {
            border-color: var(--accent-color) !important;
            background: rgba(255,255,255,0.1) !important;
        }
        .btn {
            border-radius: 0 !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            border: 2px solid var(--accent-color) !important;
        }
            """
        elif portfolio_style == "Minimalist Clean":
            return """
        /* Minimalist Clean Style */
        body {
            background: #ffffff !important;
            color: #2d3748 !important;
            font-family: 'Helvetica Neue', Arial, sans-serif !important;
        }
        .hero {
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%) !important;
            color: #2d3748 !important;
            border-bottom: 1px solid #e2e8f0 !important;
        }
        .hero h1 {
            color: #2d3748 !important;
            font-weight: 200 !important;
            font-size: 3.5rem !important;
        }
        .hero p {
            color: #4a5568 !important;
            font-weight: 300 !important;
        }
        .skill-card, .experience-item {
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
            background: #ffffff !important;
        }
        .skill-card:hover, .experience-item:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            transform: translateY(-2px) !important;
        }
        .section {
            background: #ffffff !important;
            padding: 120px 0 !important;
        }
        .section:nth-child(even) {
            background: #f7fafc !important;
        }
        .section h2 {
            font-weight: 200 !important;
            font-size: 2.5rem !important;
            color: #2d3748 !important;
            margin-bottom: 3rem !important;
        }
        nav {
            background: rgba(255,255,255,0.95) !important;
            border-bottom: 1px solid #e2e8f0 !important;
        }
        nav a {
            color: #4a5568 !important;
            font-weight: 400 !important;
            border-radius: 4px !important;
        }
        nav a:hover {
            background: #edf2f7 !important;
            color: var(--primary-color) !important;
        }
        .btn {
            background: var(--primary-color) !important;
            color: white !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }
        .skill-card i {
            color: var(--primary-color) !important;
        }
        .experience-item h3 {
            color: var(--primary-color) !important;
        }
            """
        else: 
            return """
        /* Modern Professional Style */
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif !important;
        }
        .hero {
            background: var(--background) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        .hero::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            background: radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%), 
                        radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%) !important;
        }
        .hero h1 {
            font-weight: 700 !important;
            position: relative !important;
            z-index: 2 !important;
        }
        .skill-card {
            background: var(--card-bg) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            backdrop-filter: blur(10px) !important;
        }
        .skill-card:hover {
            border-color: var(--primary-color) !important;
        }
        .experience-item {
            background: var(--card-bg) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            backdrop-filter: blur(10px) !important;
        }
        .section {
            background: var(--section-bg) !important;
        }
        .section h2 {
            font-weight: 600 !important;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
        }
        nav {
            background: rgba(255,255,255,0.1) !important;
            backdrop-filter: blur(20px) !important;
        }
        nav a:hover {
            background: rgba(255,255,255,0.2) !important;
        }
            """

    def generate_html_portfolio_enhanced(self, portfolio_data: Dict) -> str:
        portfolio_style = portfolio_data.get('portfolio_style', 'Modern Professional')
        color_scheme = portfolio_data.get('color_scheme', 'Blue Gradient (Professional)')
        
        colors = self.get_color_scheme_styles(color_scheme)
        style_layout = self.get_portfolio_style_layout(portfolio_style)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ name }}}} - Portfolio</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --primary-color: {colors['primary_color']};
            --secondary-color: {colors['secondary_color']};
            --accent-color: {colors['accent_color']};
            --text-color: {colors['text_color']};
            --card-bg: {colors['card_bg']};
            --section-bg: {colors['section_bg']};
            --background: {colors['background']};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background: var(--background);
            background-attachment: fixed;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        header {{
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(15px);
            padding: 1rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        nav ul {{
            list-style: none;
            display: flex;
            justify-content: center;
            gap: 2rem;
        }}
        
        nav a {{
            color: white;
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            transition: all 0.3s ease;
        }}
        
        nav a:hover {{
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }}
        
        .hero {{
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
        }}
        
        .hero h1 {{
            font-size: 4rem;
            color: white;
            margin-bottom: 1rem;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        
        .hero p {{
            font-size: 1.5rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 2rem;
        }}
        
        .btn {{
            display: inline-block;
            padding: 1rem 2.5rem;
            background: linear-gradient(45deg, var(--accent-color), var(--primary-color));
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }}
        
        .section {{
            padding: 100px 0;
            background: var(--section-bg);
        }}
        
        .section:nth-child(even) {{
            background: var(--card-bg);
        }}
        
        .section h2 {{
            text-align: center;
            margin-bottom: 4rem;
            font-size: 3rem;
            color: var(--primary-color);
            position: relative;
        }}
        
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }}
        
        .skill-card {{
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            text-align: center;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }}
        
        .skill-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            border-color: var(--primary-color);
        }}
        
        .skill-card i {{
            font-size: 3rem;
            color: var(--primary-color);
            margin-bottom: 1rem;
        }}
        
        .skill-card h3 {{
            color: var(--text-color);
            margin-bottom: 1rem;
        }}
        
        .skill-card p {{
            color: var(--text-color);
            opacity: 0.8;
        }}
        
        .experience-item {{
            background: var(--card-bg);
            padding: 2.5rem;
            margin-bottom: 3rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border-left: 4px solid var(--accent-color);
        }}
        
        .experience-item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(0,0,0,0.2);
        }}
        
        .experience-item h3 {{
            color: var(--primary-color);
            margin-bottom: 0.5rem;
            font-size: 1.4rem;
        }}
        
        .experience-item .company {{
            color: var(--secondary-color);
            font-style: italic;
            margin-bottom: 1rem;
            font-weight: 500;
        }}
        
        .experience-item p {{
            color: var(--text-color);
        }}
        
        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 2.5rem;
            }}
            
            nav ul {{
                flex-direction: column;
                gap: 1rem;
            }}
            
            .skills-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* Style-specific customizations */
        {style_layout}
    </style>
</head>
<body>    <header>
        <nav class="container">
            <ul>
                <li><a href="#hero"><i class="fas fa-home"></i> Home</a></li>
                <li><a href="#about"><i class="fas fa-user"></i> About</a></li>
                <li><a href="#skills"><i class="fas fa-cogs"></i> Skills</a></li>
                <li><a href="#projects"><i class="fas fa-code"></i> Projects</a></li>
                <li><a href="#experience"><i class="fas fa-briefcase"></i> Experience</a></li>
                <li><a href="#contact"><i class="fas fa-envelope"></i> Contact</a></li>
            </ul>
        </nav>
    </header>

    <section id="hero" class="hero">
        <div class="container">
            <h1>{{{{ name }}}}</h1>
            <p>{{{{ headline }}}}</p>
            <a href="#contact" class="btn"><i class="fas fa-paper-plane"></i> Get In Touch</a>
        </div>
    </section>

    <section id="about" class="section">
        <div class="container">
            <h2><i class="fas fa-user-circle"></i> About Me</h2>
            <div style="text-align: center; max-width: 800px; margin: 0 auto; font-size: 1.2rem;">
                <p>{{{{ about }}}}</p>
            </div>
        </div>
    </section>    <section id="skills" class="section">
        <div class="container">
            <h2><i class="fas fa-star"></i> Skills & Expertise</h2>
            <div class="skills-grid">
                {{% for skill in skills %}}
                <div class="skill-card">
                    <i class="fas fa-code"></i>
                    <h3>{{{{ skill }}}}</h3>
                    <p>Proficient in {{{{ skill }}}} with hands-on experience</p>
                </div>
                {{% endfor %}}
            </div>
        </div>
    </section>

    <section id="projects" class="section">
        <div class="container">
            <h2><i class="fas fa-code"></i> Featured Projects</h2>
            {{% for project in projects %}}
            <div class="experience-item">
                <h3>{{{{ project.title }}}}</h3>
                <div class="company">{{{{ project.technologies }}}} | {{{{ project.duration }}}}</div>
                <p>{{{{ project.description }}}}</p>
            </div>
            {{% endfor %}}
        </div>
    </section>

    <section id="experience" class="section">
        <div class="container">
            <h2><i class="fas fa-briefcase"></i> Professional Experience</h2>
            {{% for exp in experience %}}
            <div class="experience-item">
                <h3>{{{{ exp.title }}}}</h3>
                <div class="company">{{{{ exp.company }}}} | {{{{ exp.duration }}}}</div>
                <p>{{{{ exp.description }}}}</p>
            </div>
            {{% endfor %}}
        </div>
    </section>

    <section id="contact" class="section">
        <div class="container">
            <h2><i class="fas fa-envelope"></i> Contact Me</h2>
            <div style="text-align: center;">
                <p><strong>Email:</strong> {{{{ email }}}}</p>
                <p><strong>Phone:</strong> {{{{ phone }}}}</p>
                <p><strong>LinkedIn:</strong> <a href="{{{{ linkedin }}}}" style="color: var(--primary-color);">{{{{ linkedin }}}}</a></p>
            </div>
        </div>
    </section>

    <script>
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});
    </script>
</body>
</html>        """
        
        template = Template(html_template)
        return template.render(**portfolio_data)


class ResumeGenerator:
    def __init__(self):
        pass
    
    def _clean_resume_content(self, content: str, groq_service=None) -> str:
        if groq_service:
            return self._llm_clean_content(content, groq_service, "resume")
        
        lines = content.split('\n')
        cleaned_lines = []
        
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            if re.search(email_pattern, line):
                continue
            
            if any(phrase in line.lower() for phrase in [
                'here\'s an enhanced', 'ai analysis', 'generated by ai', 'enhanced by ai',
                'i hope this enhanced', 'this resume incorporates', 'ats-optimized',
                'note that this', 'please note', 'hope this helps', 'this enhanced resume',
                'features enhanced', 'incorporates current', 'leverages industry',
                'utilizes modern', 'enhanced with', 'the enhanced version', 'incorporates key',
                'this version incorporates', 'enhanced formatting', 'ai-optimized',
                'meets your requirements', 'tailored for the role', 'here are the',
                'analysis:', 'evaluation:', 'assessment:', 'optimization:', 'enhancement:'
            ]):
                continue
                
            line = line.replace('**', '').replace('*', '').replace('###', '').replace('---', '').strip()
            
            if line and not line.startswith('*') and len(line) > 3 and not line.isspace():
                cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        if len(cleaned_content.strip()) < 100:
            original_cleaned = content.replace('**', '').replace('###', '').replace('---', '').strip()
            return original_cleaned if len(original_cleaned) > len(cleaned_content) else cleaned_content
        
        return cleaned_content
    
    def _llm_clean_content(self, content: str, groq_service, content_type: str) -> str:
        try:
            prompt = f"""
            Clean this {content_type} content by removing:
            1. AI analysis statements and commentary
            2. Instructions about formatting
            3. Meta-commentary about the document
            4. Redundant contact information
            5. References to AI generation process
            
            Keep only the actual professional {content_type} content that should appear in the final document.
            
            Content to clean:
            {content}
                Return only the cleaned content, no explanations.
            """
            
            messages = [
                {"role": "system", "content": f"You are an expert document cleaner. Remove only AI analysis and meta-commentary while preserving all actual {content_type} content."},
                {"role": "user", "content": prompt}
            ]
            cleaned = groq_service._make_request(messages, max_tokens=2000, temperature=0.2)
            return cleaned if cleaned and not cleaned.startswith("❌") else content
        except Exception as e:
            print(f"Error in LLM content cleaning: {e}")
            return content.replace('**', '').replace('###', '').replace('---', '')
    
    def generate_pdf(self, resume_content: str, user_data: Dict = None) -> bytes:
        if user_data is None:
            user_data = {}
            
        clean_content = self._clean_resume_content(resume_content)
        
        if not clean_content or len(clean_content.strip()) < 50:
            skills_text = ', '.join(user_data.get('skills', ['Communication', 'Problem Solving', 'Leadership', 'Team Collaboration', 'Analytical Thinking']))
            
            clean_content = f"""
PROFESSIONAL SUMMARY
{user_data.get('title', 'Experienced Professional')} with proven expertise in delivering high-quality solutions and driving results. Strong background in project management, technical implementation, and team collaboration. Committed to continuous learning and professional excellence.

CORE COMPETENCIES
{skills_text}

PROFESSIONAL EXPERIENCE
• Led cross-functional teams to deliver successful projects on time and within budget
• Implemented innovative solutions that improved efficiency and reduced costs
• Collaborated with stakeholders to define requirements and ensure project alignment
• Developed and maintained strong client relationships through excellent communication

EDUCATION
{user_data.get('education', 'Bachelor\'s Degree in relevant field with strong academic performance')}

ADDITIONAL QUALIFICATIONS
• Strong analytical and problem-solving capabilities
• Excellent written and verbal communication skills
• Proficient in industry-standard tools and technologies
• Demonstrated ability to work effectively in fast-paced environments
            """.strip()
        
        if len(clean_content.split()) < 30:
            clean_content += "\n\nExperienced professional with strong technical and interpersonal skills. Proven track record of delivering results and contributing to team success."
            
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Header with name
        pdf.set_font("Arial", "B", 16)
        if user_data.get('name'):
            pdf.cell(0, 10, user_data['name'], 0, 1, 'C')
        
        pdf.set_font("Arial", size=10)        
        contact_parts = []
        if user_data.get('email'):
            contact_parts.append(user_data['email'])
        if user_data.get('phone'):
            contact_parts.append(user_data['phone'])
        if user_data.get('linkedin'):
            contact_parts.append(user_data['linkedin'])
        if contact_parts:
            contact_info = " | ".join(contact_parts)
            pdf.cell(0, 8, contact_info, 0, 1, 'C')
        pdf.ln(5)
        pdf.set_font("Arial", size=11)
        lines = clean_content.split('\n')
        for line in lines:
            if line.strip():
                line = line.replace('\u2022', '•').replace('\u2013', '-').replace('\u2014', '--')
                line = line.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
                line = ''.join(char if ord(char) < 256 else '?' for char in line)
                
                if line.isupper() or ':' in line[:20]:
                    pdf.set_font("Arial", "B", 12)
                    pdf.ln(3)
                else:
                    pdf.set_font("Arial", size=11)
                
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
                pdf.ln(3)
        
        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            return pdf_output.encode('utf-8', errors='replace')
        else:
            return bytes(pdf_output)
    
    def format_resume_text(self, resume_content: str, user_data: Dict) -> str:
        contact_parts = []
        if user_data.get('name'):
            contact_parts.append(user_data['name'])
        if user_data.get('email'):
            contact_parts.append(user_data['email'])
        if user_data.get('phone'):
            contact_parts.append(user_data['phone'])
        if user_data.get('linkedin'):
            contact_parts.append(f"LinkedIn: {user_data['linkedin']}")
        
        contact_info = ' | '.join(contact_parts) if contact_parts else ''
        
        formatted_resume = f"""
{contact_info}

{resume_content}

---
Generated on {datetime.now().strftime('%B %d, %Y')}
        """
        
        return formatted_resume.strip()

    def save_resume(self, content: str, filename: str = None) -> str:
        if not filename:
            filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        filepath = filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath


class CoverLetterGenerator:
    
    def __init__(self):
        pass
    
    def _clean_cover_letter_content(self, content: str) -> str:
        lines = content.split('\n')
        cleaned_lines = []
        
        skip_patterns = [
            'Here\'s an enhanced',
            'ATS-optimized',
            'Strong action verbs',
            'Current industry trends',
            'I hope this enhanced',
            'This cover letter',
            'AI analysis',
            'Generated by AI',
            'Enhanced by AI',
            'Optimized by AI',
            'meets your requirements',
            'incorporates current',
            'leverages industry',
            'utilizes modern',
            'features enhanced',
            'this enhanced version',
            'incorporates key',
            'The enhanced cover letter',
            'incorporates trending',
            'This letter incorporates',
            'Enhanced with',
            '* **', 
            '**',    
            '###',   
            '---',   
        ]
        
        skip_entire_line_patterns = [
            'Here\'s an enhanced',
            'I hope this enhanced',
            'This cover letter incorporates',
            'The resume uses',
            'Verbs like',
            'The resume incorporates',
            'This enhanced cover letter',
            'The enhanced version',
            'This version incorporates',
            'Incorporates current',
            'Features enhanced',
            'Leverages industry',
            'Utilizes modern',
            'This incorporates',
            'Enhanced with',
            'This letter leverages',
            'Incorporates trending',
            'This enhanced version',
            'The following incorporates',
            'This letter incorporates',
        ]
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            should_skip_line = False
            for pattern in skip_entire_line_patterns:
                if pattern.lower() in line.lower():
                    should_skip_line = True
                    break
            
            if should_skip_line:
                continue
            
            for pattern in skip_patterns:
                line = line.replace(pattern, '')
            
            line = line.replace('**', '').replace('*', '').replace('###', '').strip()
            
            if line and not line.startswith('*') and len(line) > 3:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def format_cover_letter_text(self, content: str, user_data: Dict, cover_letter_data: Dict) -> str:
        header_parts = []
        if user_data.get('name'):
            header_parts.append(user_data['name'])
        if user_data.get('email'):
            header_parts.append(user_data['email'])
        if user_data.get('phone'):
            header_parts.append(user_data['phone'])
        
        header = '\n'.join(header_parts) if header_parts else ''
        
        company_name = cover_letter_data.get('company_name', 'Company')
        
        signature_name = user_data.get('name', 'Your Name')
        
        formatted_letter = f"""{header}

{datetime.now().strftime('%B %d, %Y')}

Hiring Manager
{company_name}

Dear Hiring Manager,

{content}

Sincerely,
{signature_name}

---
Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        
        return formatted_letter.strip()

    def format_cover_letter(self, content: str, user_data: Dict, company_name: str) -> str:
        header_parts = []
        if user_data.get('name'):
            header_parts.append(user_data['name'])
        if user_data.get('email'):
            header_parts.append(user_data['email'])
        if user_data.get('phone'):
            header_parts.append(user_data['phone'])
        
        header = '\n'.join(header_parts) if header_parts else ''
        
        signature_name = user_data.get('name', '')
        
        formatted_letter = f"""{header}

{datetime.now().strftime('%B %d, %Y')}

Hiring Manager
{company_name}

Dear Hiring Manager,

{content}

Sincerely,
{signature_name}
        """
        
        return formatted_letter.strip()

    def save_cover_letter(self, content: str, company_name: str, filename: str = None) -> str:
        if not filename:
            safe_company = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"cover_letter_{safe_company}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename
    
    def generate_pdf(self, cover_letter_content: str, user_data: Dict, company_name: str) -> bytes:
        if user_data is None:
            user_data = {}
        
        clean_content = self._clean_cover_letter_content(cover_letter_content)

        if not clean_content or len(clean_content.strip()) < 50:
            clean_content = f"""I am writing to express my strong interest in joining {company_name}. Based on my professional background and skills, I believe I would be a valuable addition to your team.

My experience includes strong technical and interpersonal skills, with a proven track record of delivering results in collaborative environments. I am particularly drawn to {company_name} because of your reputation for innovation and excellence in the industry.

I would welcome the opportunity to discuss how my skills and enthusiasm can contribute to your team's continued success. Thank you for considering my application.

I look forward to hearing from you soon."""
            
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.set_font("Arial", "B", 14)
        if user_data.get('name'):
            pdf.cell(0, 10, user_data['name'], 0, 1, 'L')
        
        pdf.set_font("Arial", size=11)
        if user_data.get('email'):
            pdf.cell(0, 6, user_data['email'], 0, 1, 'L')
        if user_data.get('phone'):
            pdf.cell(0, 6, user_data['phone'], 0, 1, 'L')
        pdf.ln(5)
        
        pdf.cell(0, 6, datetime.now().strftime('%B %d, %Y'), 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, 'Hiring Manager', 0, 1, 'L')
        pdf.cell(0, 6, company_name, 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 6, 'Dear Hiring Manager,', 0, 1, 'L')
        pdf.ln(3)
        lines = clean_content.split('\n')
        for line in lines:
            if line.strip():
                line = line.replace('\u2022', '•').replace('\u2013', '-').replace('\u2014', '--')
                line = line.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
                line = ''.join(char if ord(char) < 256 else '?' for char in line)
                
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
        
        pdf.ln(3)
        pdf.cell(0, 6, 'Sincerely,', 0, 1, 'L')
        pdf.ln(5)
        if user_data.get('name'):
            pdf.cell(0, 6, user_data['name'], 0, 1, 'L')
        
        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            return pdf_output.encode('utf-8', errors='replace')
        else:
            return bytes(pdf_output)
