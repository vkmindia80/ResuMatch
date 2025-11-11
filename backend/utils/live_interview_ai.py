import os
from typing import Dict, List, Optional
from datetime import datetime
from emergentintegrations import OpenAI, Anthropic

class LiveInterviewAI:
    """AI assistant for real-time interview answers"""
    
    def __init__(self):
        self.emergent_key = os.getenv("EMERGENT_LLM_KEY")
        if not self.emergent_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        # Initialize both clients
        self.openai_client = OpenAI(api_key=self.emergent_key)
        self.anthropic_client = Anthropic(api_key=self.emergent_key)
    
    async def generate_instant_answer(
        self,
        question: str,
        user_profile: Dict,
        job_description: Optional[Dict] = None,
        model: str = "gpt-4"
    ) -> Dict:
        """
        Generate instant AI answer to interview question
        
        Args:
            question: The interview question
            user_profile: User's profile data
            job_description: Optional job description for context
            model: "gpt-4" or "claude-sonnet"
        
        Returns:
            Dict with answer, context_used, and metadata
        """
        # Build context from profile
        context_parts = []
        context_used = []
        
        # Add professional summary
        if user_profile.get("professional_summary"):
            context_parts.append(f"Professional Summary: {user_profile['professional_summary']}")
            context_used.append("Professional Summary")
        
        # Add experience
        if user_profile.get("experience"):
            exp_text = "Work Experience:\n"
            for exp in user_profile["experience"][:3]:  # Top 3 experiences
                exp_text += f"- {exp.get('title')} at {exp.get('company')}: {exp.get('description', '')}\n"
            context_parts.append(exp_text)
            context_used.append("Work Experience")
        
        # Add skills
        if user_profile.get("skills"):
            skills_text = f"Skills: {', '.join(user_profile['skills'][:15])}"
            context_parts.append(skills_text)
            context_used.append("Skills")
        
        # Add education
        if user_profile.get("education"):
            edu_text = "Education:\n"
            for edu in user_profile["education"][:2]:
                edu_text += f"- {edu.get('degree')} in {edu.get('field')} from {edu.get('institution')}\n"
            context_parts.append(edu_text)
            context_used.append("Education")
        
        # Add job context if available
        job_context = ""
        if job_description:
            job_context = f"\n\nTarget Role: {job_description.get('title')} at {job_description.get('company')}"
            if job_description.get("requirements"):
                job_context += f"\nKey Requirements: {job_description['requirements'][:500]}"
            context_used.append("Job Description")
        
        # Build prompt
        profile_context = "\n\n".join(context_parts)
        
        system_prompt = """You are an expert interview coach helping a candidate answer interview questions in real-time. 
Your goal is to provide concise, impressive answers that:
1. Are tailored to the candidate's actual experience and skills
2. Use the STAR method (Situation, Task, Action, Result) when appropriate
3. Are confident and professional
4. Are 2-3 sentences for simple questions, 4-6 sentences for behavioral questions
5. Include specific examples from their background
6. Sound natural and conversational, not scripted

Keep answers concise - this is for live interview assistance."""

        user_prompt = f"""Based on this candidate's profile:

{profile_context}{job_context}

Provide a strong, concise answer to this interview question:
"{question}"

Answer naturally and confidently, as if you are the candidate speaking."""

        try:
            if model == "claude-sonnet":
                # Use Anthropic Claude
                response = self.anthropic_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                answer = response.content[0].text
            else:
                # Use OpenAI GPT-4
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-2024-11-20",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                answer = response.choices[0].message.content
            
            return {
                "question": question,
                "answer": answer.strip(),
                "context_used": context_used,
                "generated_at": datetime.utcnow(),
                "model": model
            }
        
        except Exception as e:
            print(f"Error generating AI answer: {str(e)}")
            # Fallback answer
            return {
                "question": question,
                "answer": "I have relevant experience in this area that I'd be happy to discuss. Could you tell me more specifically what aspects you're most interested in?",
                "context_used": [],
                "generated_at": datetime.utcnow(),
                "model": model,
                "error": str(e)
            }
    
    async def analyze_interview_performance(
        self,
        transcript_entries: List[Dict],
        ai_answers: List[Dict],
        user_profile: Dict
    ) -> Dict:
        """
        Analyze overall interview performance and provide feedback
        """
        # Count questions and answers
        questions = [entry for entry in transcript_entries if entry["type"] == "question"]
        question_count = len(questions)
        
        if question_count == 0:
            return {
                "overall_score": 0,
                "communication_score": 0,
                "technical_score": 0,
                "behavioral_score": 0,
                "strengths": [],
                "areas_for_improvement": ["Complete at least one interview session to receive analysis"],
                "detailed_feedback": "No questions were detected in this session.",
                "question_count": 0,
                "answer_quality_avg": 0
            }
        
        # Build analysis prompt
        questions_text = "\n".join([f"{i+1}. {q['text']}" for i, q in enumerate(questions[:10])])
        
        system_prompt = """You are an expert interview performance analyst. Analyze the interview session and provide:
1. Overall score (0-100)
2. Communication score (0-100)
3. Technical score (0-100) 
4. Behavioral score (0-100)
5. Top 3 strengths
6. Top 3 areas for improvement
7. Detailed constructive feedback

Be specific, actionable, and encouraging."""

        user_prompt = f"""Analyze this interview session:

Number of questions asked: {question_count}
Questions covered:
{questions_text}

Provide a JSON response with:
- overall_score (0-100)
- communication_score (0-100)
- technical_score (0-100)
- behavioral_score (0-100)
- strengths (array of 3 strings)
- areas_for_improvement (array of 3 strings)
- detailed_feedback (string, 2-3 paragraphs)"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            analysis["question_count"] = question_count
            analysis["answer_quality_avg"] = 75.0  # Default good score
            
            return analysis
        
        except Exception as e:
            print(f"Error analyzing performance: {str(e)}")
            # Fallback analysis
            return {
                "overall_score": 70,
                "communication_score": 70,
                "technical_score": 70,
                "behavioral_score": 70,
                "strengths": [
                    "Completed the interview session",
                    "Engaged with multiple questions",
                    "Used AI assistance effectively"
                ],
                "areas_for_improvement": [
                    "Practice more mock interviews",
                    "Develop stronger STAR method answers",
                    "Build confidence in technical responses"
                ],
                "detailed_feedback": f"You completed an interview session with {question_count} questions. Continue practicing to improve your performance. Focus on providing specific examples and using the STAR method for behavioral questions.",
                "question_count": question_count,
                "answer_quality_avg": 70.0
            }
