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
        """Submit answer and get feedback"""
        current_q = self.get_current_question(session)
        if not current_q:
            return None
        
        evaluation = self.groq_service.evaluate_interview_answer(
            current_q['question'], 
            answer, 
            session['job_description']
        )
        
        session['answers'].append(answer)
        session['scores'].append(evaluation.get('score', 5))
        session['feedback'].append(evaluation)
        
        session['current_question'] += 1
        
        return evaluation
    
    def get_final_report(self, session: Dict) -> Dict:
        if not session['scores']:
            return {'error': 'No answers submitted'}
        
        avg_score = sum(session['scores']) / len(session['scores'])
        duration = time.time() - session['start_time']
        
        if avg_score >= 8:
            performance = "Excellent"
            message = "Outstanding performance! You're well-prepared for this role."
        elif avg_score >= 6:
            performance = "Good"
            message = "Solid performance with room for improvement in some areas."
        elif avg_score >= 4:
            performance = "Fair"
            message = "Decent start, but significant preparation needed."
        else:
            performance = "Needs Improvement"
            message = "Consider more preparation and practice before the actual interview."
        
        improvement_areas = []
        for feedback in session['feedback']:
            if 'weaknesses' in feedback:
                improvement_areas.extend(feedback['weaknesses'])
        
        report = {
            'overall_score': round(avg_score, 1),
            'performance_level': performance,
            'message': message,
            'questions_answered': len(session['answers']),
            'duration_minutes': round(duration / 60, 1),
            'detailed_feedback': session['feedback'],
            'improvement_areas': list(set(improvement_areas)),
            'strengths': self._extract_strengths(session['feedback'])
        }
        
        return report
    
    def _extract_strengths(self, feedback_list: List[Dict]) -> List[str]:
        strengths = []
        for feedback in feedback_list:
            if 'strengths' in feedback:
                strengths.extend(feedback['strengths'])
        return list(set(strengths))

    def start_interview(self, user_data: Dict, interview_type: str, job_role: str) -> str:
        job_description = f"{interview_type} for {job_role} position"
        questions = self.groq_service.generate_interview_questions(job_description, user_data)
        
        if questions and len(questions) > 0:
            return questions[0].get('question', 'Tell me about yourself and why you are interested in this position.')
        return 'Tell me about yourself and why you are interested in this position.'
    
    def process_response(self, user_response: str, conversation_history: List[Dict]) -> tuple:
        if len(conversation_history) < 3:  # Still early in interview
            feedback = "Good start! Keep your answers concise and specific."
            next_question = "What interests you most about this role and our company?"
        elif len(conversation_history) < 5:
            feedback = "Remember to provide specific examples from your experience."
            next_question = "Can you tell me about a challenging project you worked on and how you handled it?"
        else:
            feedback = "Great progress! Try to highlight your achievements with quantifiable results."
            next_question = "Do you have any questions for us about the role or company?"
        
        return next_question, feedback
    
    def end_interview(self, conversation_history: List[Dict]) -> str:
        total_responses = len([msg for msg in conversation_history if msg['role'] == 'candidate'])
        
        feedback = f"""
        **Interview Summary:**
        
        🎯 **Performance Overview:**
        - Questions answered: {total_responses}
        - Overall communication: Good
        
        💡 **Strengths demonstrated:**
        - Active participation in the interview
        - Willingness to engage with questions
        
        📈 **Areas for improvement:**
        - Provide more specific examples
        - Quantify achievements where possible
        - Practice concise but comprehensive answers
        
        🚀 **Next steps:**
        - Continue practicing interview skills
        - Research the company and role thoroughly
        - Prepare STAR method examples for behavioral questions
        """
        
        return feedback

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
        
        with col2:
            experience_level = st.selectbox("Experience Level", 
                                          ["Entry Level", "Mid Level", "Senior Level", "Executive"])
            interview_type = st.selectbox("Interview Type", 
                                        ["General", "Technical", "Behavioral", "Case Study"])
        
        job_description = st.text_area("Job Description (Optional)", 
                                     placeholder="Paste the job description here for more targeted questions...")
        
        if st.button("Start Interview", type="primary"):
            if job_title:
                if not job_description:
                    job_description = f"{job_title} position at {company}. {experience_level} role requiring relevant experience and skills."
                
                user_background = st.session_state.get('user_data', {})
                session = self.simulator.start_interview_session(job_description, user_background)
                st.session_state.interview_session = session
                st.session_state.interview_active = True
                st.rerun()
            else:
                st.error("Please provide at least a job title to start the interview.")
    
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
        
        if 'suggestions' in evaluation:
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
        lines = [
            "INTERVIEW PERFORMANCE REPORT",
            "=" * 40,
            f"Overall Score: {report['overall_score']}/10",
            f"Performance Level: {report['performance_level']}",
            f"Questions Answered: {report['questions_answered']}",
            f"Duration: {report['duration_minutes']} minutes",
            "",
            "SUMMARY:",
            report['message'],
            "",
            "DETAILED FEEDBACK:",
            "-" * 20
        ]
        
        for i, feedback in enumerate(report['detailed_feedback']):
            lines.extend([
                f"",
                f"Question {i + 1}:",
                session['questions'][i]['question'],
                f"Your Answer: {session['answers'][i]}",
                f"Score: {feedback.get('score', 'N/A')}/10",
                f"Feedback: {feedback.get('feedback', 'No feedback available')}",
                "-" * 20
            ])
        
        if report['improvement_areas']:
            lines.extend([
                "",
                "KEY IMPROVEMENT AREAS:",
                *[f"• {area}" for area in report['improvement_areas']]
            ])
        
        if report['strengths']:
            lines.extend([
                "",
                "STRENGTHS DEMONSTRATED:",
                *[f"• {strength}" for strength in report['strengths']]
            ])
        
        return "\n".join(lines)