import streamlit as st
from typing import Dict, List
import random
import time

class InterviewSimulator:
    def __init__(self, groq_service):
        self.groq_service = groq_service
        
    def start_interview_session(self, job_description: str, user_background: Dict) -> Dict:
        questions = self.groq_service.generate_interview_questions(job_description, user_background)
        
        session = {
            'questions': questions,
            'current_question': 0,
            'answers': [],
            'scores': [],
            'feedback': [],
            'job_description': job_description,
            'user_background': user_background,
            'start_time': time.time()
        }
        
        return session
    
    def get_current_question(self, session: Dict) -> Dict:
        if session['current_question'] < len(session['questions']):
            return session['questions'][session['current_question']]
        return None
    
    def submit_answer(self, session: Dict, answer: str) -> Dict:
        current_q = self.get_current_question(session)
        if not current_q:
            return None
        
        # Evaluate the answer using Groq service
        evaluation = self.groq_service.evaluate_interview_answer(
            current_q['question'], 
            answer, 
            session['job_description']
        )
        
        # Store the answer and evaluation
        session['answers'].append(answer)
        session['scores'].append(evaluation.get('score', 5))
        session['feedback'].append(evaluation)
        
        # Move to next question
        session['current_question'] += 1
        
        return evaluation
    
    def get_final_report(self, session: Dict) -> Dict:
        if not session['answers']:
            return {
                'overall_score': 0,
                'performance_level': 'Incomplete',
                'message': 'No answers provided',
                'questions_answered': 0,
                'duration_minutes': 0,
                'detailed_feedback': []
            }
        
        avg_score = sum(session['scores']) / len(session['scores'])
        duration_minutes = int((time.time() - session['start_time']) / 60)
        
        # Determine performance level
        if avg_score >= 8:
            performance_level = "Excellent"
            message = "Outstanding performance! You demonstrated strong knowledge and communication skills."
        elif avg_score >= 6:
            performance_level = "Good"
            message = "Good performance overall. With some practice, you can achieve excellence."
        elif avg_score >= 4:
            performance_level = "Fair"
            message = "Fair performance. Focus on providing more detailed and structured answers."
        else:
            performance_level = "Needs Improvement"
            message = "Keep practicing! Consider researching common interview questions and the STAR method."
        
        return {
            'overall_score': round(avg_score, 1),
            'performance_level': performance_level,
            'message': message,
            'questions_answered': len(session['answers']),
            'duration_minutes': duration_minutes,
            'detailed_feedback': session['feedback']
        }

class InterviewUI:
    def __init__(self, interview_simulator):
        self.simulator = interview_simulator
    
    def render_interview_setup(self):
        st.subheader("🎭 AI Interview Simulator")
        st.write("Practice with our AI interviewer and get real-time feedback!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer")
            company = st.text_input("Company", placeholder="e.g., Google")
            # Add number of questions slider
            num_questions = st.slider("Number of Questions", min_value=3, max_value=15, value=5, 
                                    help="Choose how many questions you want to practice with")
        
        with col2:
            experience_level = st.selectbox("Experience Level", 
                                            ["Entry Level", "Mid Level", "Senior Level", "Executive"])
            
            interview_type = st.selectbox("Interview Type", 
                                        ["General", "Technical", "Behavioral", "Case Study"])
            
            # Add difficulty level selector
            difficulty_level = st.selectbox("Difficulty Level", 
                                          ["Easy", "Medium", "Hard", "Mixed"],
                                          index=1,
                                          help="Choose the difficulty level of questions")
        
        job_description = st.text_area("Job Description (Optional)", 
                                      placeholder="Paste the job description here for more targeted questions...",
                                      key="simulator_job_description")
        
        if st.button("Start Interview", type="primary"):
            if job_title:
                if not job_description:
                    job_description = f"{job_title} position at {company}. {experience_level} level. {interview_type} interview."
                
                user_background = st.session_state.get('user_data', {})
                user_background.update({
                    'target_job_title': job_title,
                    'target_company': company,
                    'experience_level': experience_level,
                    'interview_type': interview_type,
                    'num_questions': num_questions,
                    'difficulty_level': difficulty_level
                })
                
                session = self.simulator.start_interview_session(job_description, user_background)
                
                if session and session.get('questions'):
                    st.session_state.interview_session = session
                    st.session_state.interview_active = True
                    st.success(f"✅ Interview session created with {num_questions} questions! Starting now...")
                    st.rerun()
                else:
                    st.error("❌ Failed to create interview session. Please try again.")
            else:
                st.error("Please provide at least a job title.")
    
    def render_active_interview(self):
        session = st.session_state.interview_session
        current_q = self.simulator.get_current_question(session)
        
        if not current_q:
            self.render_interview_results()
            return
        
        progress = session['current_question'] / len(session['questions'])
        st.progress(progress, text=f"Question {session['current_question'] + 1} of {len(session['questions'])}")
        
        st.subheader(f"Question {session['current_question'] + 1}")
        st.write(f"**Type:** {current_q.get('type', 'General')}")
        st.write(f"**Difficulty:** {current_q.get('difficulty', 'Medium')}")
        
        st.markdown(f"### {current_q['question']}")
        
        answer = st.text_area("Your Answer", 
                            placeholder="Take your time to provide a thoughtful answer...",
                            height=150,
                            key=f"answer_{session['current_question']}")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("Submit Answer", type="primary", disabled=not answer.strip()):
                with st.spinner("Evaluating your answer..."):
                    evaluation = self.simulator.submit_answer(session, answer)
                    if evaluation:
                        st.session_state.last_evaluation = evaluation
                        st.rerun()
        
        with col2:
            if st.button("Skip Question"):
                self.simulator.submit_answer(session, "Skipped")
                st.rerun()
        
        with col3:
            if st.button("End Interview"):
                st.session_state.interview_active = False
                st.rerun()
        
        if hasattr(st.session_state, 'last_evaluation') and st.session_state.last_evaluation:
            self.render_question_feedback(st.session_state.last_evaluation)
    
    def render_question_feedback(self, evaluation: Dict):
        st.divider()
        st.subheader("📝 Feedback on Previous Answer")
        
        score = evaluation.get('score', 5)
        
        if score >= 8:
            st.success(f"Score: {score}/10 - Excellent!")
        elif score >= 6:
            st.info(f"Score: {score}/10 - Good")
        elif score >= 4:
            st.warning(f"Score: {score}/10 - Fair")
        else:
            st.error(f"Score: {score}/10 - Needs Improvement")

        col1, col2 = st.columns(2)
        
        with col1:
            if 'strengths' in evaluation:
                st.markdown("**✅ Strengths:**")
                for strength in evaluation['strengths']:
                    st.write(f"• {strength}")
        
        with col2:
            if 'weaknesses' in evaluation:
                st.markdown("**⚠️ Areas for Improvement:**")
                for weakness in evaluation['weaknesses']:
                    st.write(f"• {weakness}")
        
        if evaluation.get('suggestions'):
            st.markdown("**💡 Suggestions:**")
            st.write(evaluation['suggestions'])
    
    def render_interview_results(self):
        session = st.session_state.interview_session
        report = self.simulator.get_final_report(session)
        
        st.subheader("🎉 Interview Complete!")
        st.balloons()
        
        score = report['overall_score']
        if score >= 8:
            st.success(f"Overall Score: {score}/10 - {report['performance_level']}")
        elif score >= 6:
            st.info(f"Overall Score: {score}/10 - {report['performance_level']}")
        elif score >= 4:
            st.warning(f"Overall Score: {score}/10 - {report['performance_level']}")
        else:
            st.error(f"Overall Score: {score}/10 - {report['performance_level']}")
        
        st.write(report['message'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Questions Answered", report['questions_answered'])
        
        with col2:
            st.metric("Duration", f"{report['duration_minutes']} min")
        
        with col3:
            st.metric("Performance Level", report['performance_level'])
        
        if st.checkbox("Show Detailed Feedback"):
            for i, feedback in enumerate(report['detailed_feedback']):
                with st.expander(f"Question {i + 1} - Score: {feedback.get('score', 'N/A')}/10"):
                    question = session['questions'][i]['question']
                    answer = session['answers'][i]
                    
                    st.write(f"**Question:** {question}")
                    st.write(f"**Your Answer:** {answer}")
                    
                    if 'feedback' in feedback:
                        st.write(f"**Feedback:** {feedback['feedback']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Practice Again", type="primary"):
                if 'interview_session' in st.session_state:
                    del st.session_state.interview_session
                if 'interview_active' in st.session_state:
                    del st.session_state.interview_active
                if 'last_evaluation' in st.session_state:
                    del st.session_state.last_evaluation
                st.rerun()
        
        with col2:
            if st.button("Download Report"):
                report_text = self._generate_report_text(report, session)
                st.download_button(
                    label="📄 Download Detailed Report",
                    data=report_text,
                    file_name=f"interview_report_{int(time.time())}.txt",
                    mime="text/plain"
                )
    
    def _generate_report_text(self, report: Dict, session: Dict) -> str:
        report_text = f"""INTERVIEW PERFORMANCE REPORT
========================================
Overall Score: {report['overall_score']}/10
Performance Level: {report['performance_level']}
Questions Answered: {report['questions_answered']}
Duration: {report['duration_minutes']} minutes

SUMMARY:
{report['message']}

DETAILED BREAKDOWN:
"""
        
        for i, (question, answer, feedback) in enumerate(zip(session['questions'], session['answers'], report['detailed_feedback'])):
            report_text += f"""
Question {i + 1}: {question['question']}
Your Answer: {answer}
Score: {feedback.get('score', 'N/A')}/10
Feedback: {feedback.get('feedback', 'No feedback available')}
{'=' * 50}"""
        
        return report_text
