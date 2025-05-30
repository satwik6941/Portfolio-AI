import streamlit as st

def convert_usd_to_inr(usd_amount: float, exchange_rate: float = 83.0) -> float:
    return usd_amount * exchange_rate

def format_salary_in_inr(salary_str: str) -> str:
    """Format salary to show only in rupees (INR)"""
    if not salary_str or salary_str == "Not specified":
        return salary_str
    
    import re
    numbers = re.findall(r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', salary_str)
    
    if numbers:
        try:
            usd_amount = float(numbers[0].replace(',', ''))
            inr_amount = convert_usd_to_inr(usd_amount)
            
            if len(numbers) > 1:
                usd_amount2 = float(numbers[1].replace(',', ''))
                inr_amount2 = convert_usd_to_inr(usd_amount2)
                return f"₹{inr_amount:,.0f} - ₹{inr_amount2:,.0f}"
            else:
                return f"₹{inr_amount:,.0f}"
        except (ValueError, IndexError):
            return salary_str
    
    return salary_str

def job_search_page(job_searcher, groq_service):
    st.header("🔍 AI Job Search")
    
    if not st.session_state.get("verification_completed", False):
        st.warning("⚠️ Please complete your profile verification in the Data Input page first.")
        return
    
    st.markdown("""
    **🚀 Enhanced Job Search with AI Insights:**
    - **Real-time web scraping** from Indeed, LinkedIn, and Glassdoor
    - **AI-powered job matching** with personalized insights
    - **Market salary analysis** and application tips
    - **Latest job postings** updated in real-time
    
    **Note:** No API keys required - our enhanced scraper provides fresh job data!
    """)
    
    st.markdown("### 🔍 AI-Enhanced Job Search")
    
    # Add real-time indicator
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("🕒 Data Freshness", "Real-time", "Live scraping")
    with col_info2:
        st.metric("🎯 AI Matching", "Enabled", "Smart insights")
    with col_info3:
        st.metric("🌐 Job Sources", "3+ Sites", "Multi-platform")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("job_search_form"):
            st.markdown("**🔍 Search Parameters**")
            keywords = st.text_input("🔍 Job Keywords/Title:", placeholder="e.g., Software Engineer, Data Scientist, Product Manager")
            location = st.text_input("📍 Location:", placeholder="e.g., New York, Remote, San Francisco, London")
            
            col_a, col_b = st.columns(2)
            with col_a:
                job_type = st.selectbox("💼 Job Type:", [
                    "Full-time Jobs",
                    "Internships", 
                    "Part-time Jobs",
                    "Contract/Freelance",
                    "Both Jobs & Internships"
                ])
                
                experience_level = st.selectbox("📈 Experience Level:", [
                    "", 
                    "Entry Level (0-2 years)", 
                    "Mid Level (3-5 years)", 
                    "Senior Level (6-10 years)", 
                    "Executive (10+ years)"
                ])
                
                company_size = st.selectbox("🏢 Company Size:", [
                    "",
                    "Startup (1-50)",
                    "Small (51-200)", 
                    "Medium (201-1000)",
                    "Large (1001-5000)",
                    "Enterprise (5000+)"
                ])
            
            with col_b:
                salary_range = st.selectbox("💰 Expected Salary Range:", [
                    "Not specified",
                    "$40k - $60k",
                    "$60k - $80k", 
                    "$80k - $120k",
                    "$120k - $180k",
                    "$180k - $250k",
                    "$250k+"
                ])
                
                remote_work = st.checkbox("🏠 Include Remote Jobs", value=True)
                posted_within = st.selectbox("📅 Posted Within:", [
                    "Any time",
                    "Last 24 hours",
                    "Last 3 days",
                    "Last week",
                    "Last month"
                ])
            
            # Add advanced search options
            with st.expander("🔧 Advanced Search Options"):
                col_adv1, col_adv2 = st.columns(2)
                with col_adv1:
                    industry_filter = st.selectbox("🏭 Industry:", [
                        "Any",
                        "Technology",
                        "Finance",
                        "Healthcare", 
                        "Education",
                        "Manufacturing",
                        "Retail",
                        "Consulting",
                        "Non-profit"
                    ])
                with col_adv2:
                    job_sources = st.multiselect("🌐 Job Sources:", [
                        "Indeed",
                        "LinkedIn", 
                        "Glassdoor",
                        "Company Websites"
                    ], default=["Indeed", "LinkedIn", "Glassdoor"])
            
            submitted = st.form_submit_button("🚀 Search Latest Jobs", type="primary", use_container_width=True)
            st.caption("⚡ Real-time search across multiple job platforms with AI insights")
    
    with col2:
        if st.session_state.get("user_data"):
            st.markdown("**👤 Profile Summary:**")
            user_data = st.session_state.user_data
            st.write(f"**Name:** {user_data.get('name', 'N/A')}")
            st.write(f"**Title:** {user_data.get('title', 'N/A')}")
            st.write(f"**Skills:** {len(user_data.get('skills', []))}")
            st.write(f"**Experience:** {user_data.get('experience_level', 'N/A')}")
            
            if keywords:
                with st.spinner("🧠 Getting AI market insights..."):
                    salary_data = job_searcher.get_salary_insights(keywords, location)
                    if salary_data:
                        st.markdown("**💰 Market Insights:**")
                        median_usd = salary_data.get('median_salary', 0)
                        min_usd = salary_data.get('min_salary', 0)
                        max_usd = salary_data.get('max_salary', 0)
                        
                        if median_usd > 0:
                            median_inr = convert_usd_to_inr(median_usd)
                            st.metric("💰 Median Salary", f"₹{median_inr:,.0f}", "Per year")
                        
                        if min_usd > 0 and max_usd > 0:
                            min_inr = convert_usd_to_inr(min_usd)
                            max_inr = convert_usd_to_inr(max_usd)
                            st.write(f"**Range:** ₹{min_inr:,.0f} - ₹{max_inr:,.0f}")
                        
                        # Add demand indicator
                        demand_level = "High" if median_usd > 100000 else "Medium" if median_usd > 60000 else "Growing"
                        st.metric("📈 Market Demand", demand_level, "Based on salary trends")
        else:
            st.info("👆 Complete your profile above to get personalized job recommendations and market insights.")

    if submitted and keywords:
        with st.spinner("🔍 Searching latest jobs across multiple platforms..."):
            jobs = job_searcher.search_jobs(
                keywords=keywords, 
                location=location, 
                experience_level=experience_level,
                company_size=company_size,
                remote=remote_work,
                job_type=job_type,
                limit=25
            )
            
            if st.session_state.get("user_data") and jobs:
                with st.spinner("🧠 Analyzing job matches with AI..."):
                    enhanced_jobs = groq_service.analyze_job_matches(jobs, st.session_state.user_data)
                    jobs = enhanced_jobs
            
        if jobs:
            st.success(f"🎉 Found {len(jobs)} latest job opportunities from multiple sources!")
              # Enhanced filtering and sorting
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                sort_by = st.selectbox("📊 Sort by:", ["AI Match Score", "Date Posted", "Company", "Salary"])
            with col2:
                company_filter = st.multiselect("🏢 Filter by Company:", 
                                                options=list(set([job.get('company', '') for job in jobs])))
            with col3:
                show_only_remote = st.checkbox("🏠 Remote only")
                show_high_match = st.checkbox("🎯 High match (80%+)")
            with col4:
                view_mode = st.radio("📱 View:", ["Detailed", "Compact"])
            
            filtered_jobs = jobs
            if company_filter:
                filtered_jobs = [job for job in jobs if job.get('company') in company_filter]
            if show_only_remote:
                filtered_jobs = [job for job in jobs if job.get('remote_type')]
            if show_high_match:
                filtered_jobs = [job for job in jobs if 
                               int(str(job.get('ai_analysis', {}).get('match_score', 
                                      job.get('ai_match_score', '0'))).replace('%', '')) >= 80]
            
            # Sort jobs            if sort_by == "AI Match Score":
                filtered_jobs = sorted(filtered_jobs, key=lambda x: 
                                     int(str(x.get('ai_analysis', {}).get('match_score', 
                                            x.get('ai_match_score', '0'))).replace('%', '')), reverse=True)
            elif sort_by == "Date Posted":
                filtered_jobs = sorted(filtered_jobs, key=lambda x: x.get('posted_date', ''), reverse=True)
            
            st.info(f"📋 Showing {len(filtered_jobs)} jobs (filtered from {len(jobs)} total)")
            
            for i, job in enumerate(filtered_jobs):
                match_score = job.get('ai_analysis', {}).get('match_score', job.get('ai_match_score', 'N/A'))
                source = job.get('source', 'web_scraper')
                source_icons = {
                    'indeed': '🔵',
                    'linkedin': '🔗', 
                    'glassdoor': '🟢',
                    'google_jobs_api': '🔍',
                    'web_scraper': '🤖'
                }
                source_icon = source_icons.get(source, '🤖')
                
                # Enhanced match score display with color coding
                try:
                    score_num = int(str(match_score).replace('%', ''))
                    if score_num >= 90:
                        match_color = "🟢"
                    elif score_num >= 75:
                        match_color = "🟡"
                    elif score_num >= 60:
                        match_color = "🟠"
                    else:
                        match_color = "🔴"
                except:
                    match_color = "⚪"
                    score_num = 0
                
                job_title = f"{source_icon} {job.get('title', 'Job Title')} at {job.get('company', 'Company')}"
                match_info = f"{match_color} AI Match: {match_score}%"
                
                if view_mode == "Compact":
                    # Compact view
                    with st.container():
                        col_compact1, col_compact2, col_compact3 = st.columns([3, 1, 1])
                        with col_compact1:
                            st.markdown(f"**{job_title}**")
                            st.caption(f"📍 {job.get('location', 'N/A')} | 💰 {format_salary_in_inr(job.get('salary_range', 'Not specified'))}")
                        with col_compact2:
                            st.markdown(f"**{match_info}**")
                        with col_compact3:
                            if st.button("👀 View Details", key=f"view_{i}", use_container_width=True):
                                st.session_state[f'expanded_job_{i}'] = not st.session_state.get(f'expanded_job_{i}', False)
                        
                        if st.session_state.get(f'expanded_job_{i}', False):
                            render_detailed_job_view(job, i)
                else:
                    # Detailed view
                    with st.expander(f"{job_title} - {match_info}", expanded=False):
                        render_detailed_job_view(job, i)
        else:
            st.info("🔍 No jobs found. Try different keywords or broader search terms.")
    
    if st.session_state.get('saved_jobs'):
        st.markdown("### 💾 Your Saved Jobs")
        for i, job in enumerate(st.session_state.saved_jobs):
            with st.expander(f"{job.get('title')} at {job.get('company')}"):
                st.write(f"📍 **Location:** {job.get('location')}")
                saved_salary_display = format_salary_in_inr(job.get('salary_range', 'Not specified'))
                st.write(f"💰 **Salary:** {saved_salary_display}")
                st.write(f"📅 **Saved on:** {job.get('saved_date', 'Recently')}")
                
                if st.button(f"Remove", key=f"remove_{i}"):
                    st.session_state.saved_jobs.pop(i)
                    st.rerun()


def render_detailed_job_view(job, index):
    """Render detailed view of a job posting with enhanced AI insights"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"📍 **Location:** {job.get('location', 'N/A')}")
        salary_display = format_salary_in_inr(job.get('salary_range', 'Not specified'))
        st.write(f"💰 **Salary:** {salary_display}")
        st.write(f"📅 **Posted:** {job.get('posted_date', 'Recently')}")
        st.write(f"🏢 **Company Size:** {job.get('company_size', 'Not specified')}")
        st.write(f"⏰ **Type:** {job.get('employment_type', 'Full-time')}")
        
        if job.get('remote_type'):
            st.write("🏠 **Remote-friendly**")
        
        st.write(f"📋 **Description:** {job.get('description', 'No description available')[:300]}...")
        
        if job.get('skills'):
            st.write(f"🛠️ **Key Skills:** {', '.join(job.get('skills', [])[:5])}")
        
        if job.get('benefits'):
            st.write(f"💎 **Benefits:** {', '.join(job.get('benefits', [])[:3])}...")
        
        # Enhanced AI Analysis Section
        if job.get('ai_analysis'):
            analysis = job.get('ai_analysis')
            st.markdown("**🤖 AI Analysis:**")
            
            # Create tabs for different insights
            tab1, tab2, tab3 = st.tabs(["📊 Match Analysis", "💡 Market Insights", "🎯 Application Tips"])
            
            with tab1:
                st.info(f"**Match Level:** {analysis.get('match_level', 'N/A')}")
                if analysis.get('matched_keywords'):
                    st.success(f"**Matched Keywords:** {', '.join(analysis.get('matched_keywords', [])[:5])}")
                if analysis.get('missing_skills'):
                    st.warning(f"**Skills to Develop:** {', '.join(analysis.get('missing_skills', [])[:3])}")
            
            with tab2:
                market_insights = job.get('market_insights', {})
                col_market1, col_market2 = st.columns(2)
                with col_market1:
                    st.metric("📈 Demand Level", market_insights.get('demand_level', 'Medium'))
                    st.metric("💰 Salary Competitiveness", market_insights.get('salary_competitiveness', 'Competitive'))
                with col_market2:
                    st.metric("🚀 Growth Potential", market_insights.get('growth_potential', 'Good'))
                    st.metric("🎯 Industry Trend", market_insights.get('industry_trend', 'Stable'))
            
            with tab3:
                if job.get('application_tips'):
                    for tip in job.get('application_tips', [])[:3]:
                        st.info(f"💡 {tip}")
                else:
                    st.info("💡 Tailor your resume to highlight relevant experience")
                    st.info("🎯 Research the company culture and values")
                    st.info("📝 Write a compelling cover letter")
    
    with col2:
        # Source indicator
        source = job.get('source', 'web_scraper')
        source_names = {
            'indeed': 'Indeed',
            'linkedin': 'LinkedIn',
            'glassdoor': 'Glassdoor',
            'google_jobs_api': 'Google Jobs',
            'web_scraper': 'Multi-Platform'
        }
        st.info(f"🌐 **Source:** {source_names.get(source, 'Unknown')}")
        
        # Application buttons
        platform_name = job.get('application_platform', 'LinkedIn')
        platform_icon = job.get('platform_icon', '💼')
        
        if job.get('linkedin_url'):
            st.link_button("💼 View on LinkedIn", job['linkedin_url'], use_container_width=True)
        
        if job.get('application_url'):
            st.link_button(f"{platform_icon} Apply on {platform_name}", job['application_url'], use_container_width=True)
        
        # Enhanced action buttons
        col_action1, col_action2 = st.columns(2)
        
        with col_action1:
            if st.button(f"💾 Save Job", key=f"save_{index}", use_container_width=True):
                if 'saved_jobs' not in st.session_state:
                    st.session_state.saved_jobs = []
                st.session_state.saved_jobs.append(job)
                st.success("Job saved!")
        
        with col_action2:
            if st.button(f"📝 Generate Cover Letter", key=f"cover_{index}", use_container_width=True):
                st.session_state.cover_letter_job = job
                st.success("Job selected for cover letter!")
        
        # AI match visualization
        try:
            match_score = int(str(job.get('ai_analysis', {}).get('match_score', job.get('ai_match_score', '0'))).replace('%', ''))
            st.progress(match_score / 100, f"AI Match: {match_score}%")
        except:
            st.progress(0.7, "AI Match: Good")
