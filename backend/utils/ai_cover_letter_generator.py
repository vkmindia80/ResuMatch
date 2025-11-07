"""
AI-Powered Cover Letter Generator
Uses OpenAI via Emergent LLM Key to generate personalized cover letters
"""
import os
import json
from typing import Dict, List, Optional
from emergentintegrations.llm.openai import LlmChat


class AICoverLetterGenerator:
    def __init__(self):
        """Initialize AI Cover Letter Generator with Emergent LLM Key"""
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def generate_cover_letter(
        self,
        profile: dict,
        job_description: dict,
        tone: str = "professional"
    ) -> dict:
        """
        Generate a personalized cover letter
        
        Args:
            profile: User profile data
            job_description: Job description data
            tone: Tone of the cover letter (professional, enthusiastic, formal)
            
        Returns:
            Dictionary with cover letter sections
        """
        try:
            from emergentintegrations.llm.chat import UserMessage
            
            prompt = self._build_cover_letter_prompt(profile, job_description, tone)
            
            system_message = "You are an expert cover letter writer. Create compelling, personalized cover letters that highlight the candidate's qualifications and enthusiasm for the role."
            
            # Create chat client
            client = LlmChat(
                api_key=self.api_key,
                session_id=f"cover_letter_{hash(str(job_description.get('id', 'unknown')))}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini").with_params(temperature=0.7, max_tokens=1200)
            
            # Send message (async)
            user_msg = UserMessage(text=prompt)
            response = await client.send_message(user_msg)
            content = response.strip()
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            cover_letter_data = json.loads(content)
            return cover_letter_data
            
        except Exception as e:
            print(f"Error generating cover letter with AI: {e}")
            return self._get_fallback_cover_letter(profile, job_description)
    
    def _build_cover_letter_prompt(
        self,
        profile: dict,
        job_description: dict,
        tone: str
    ) -> str:
        """Build prompt for cover letter generation"""
        personal_info = profile.get("personal_info", {})
        experience = profile.get("experience", [])
        skills = profile.get("skills", {})
        parsed_data = job_description.get("parsed_data", {})
        
        # Get top experiences
        exp_summary = []
        for exp in experience[:3]:
            exp_summary.append(
                f"- {exp.get('title')} at {exp.get('company')}: {', '.join(exp.get('responsibilities', [])[:2])}"
            )
        
        # Get top technical skills
        tech_skills = []
        for skill in skills.get("technical", [])[:8]:
            if isinstance(skill, dict):
                tech_skills.append(skill.get("name", ""))
            else:
                tech_skills.append(str(skill))
        
        prompt = f"""
Generate a compelling cover letter for the following job application.

**Candidate Information:**
- Name: {personal_info.get('full_name', 'Candidate')}
- Current Title: {personal_info.get('title', 'Professional')}
- Email: {personal_info.get('email', '')}
- Phone: {personal_info.get('phone', '')}
- Location: {personal_info.get('location', '')}

**Recent Experience:**
{chr(10).join(exp_summary) if exp_summary else '- N/A'}

**Key Skills:** {', '.join(tech_skills)}

**Target Position:**
- Title: {job_description.get('title')}
- Company: {job_description.get('company')}
- Location: {job_description.get('location', 'N/A')}
- Required Skills: {', '.join(parsed_data.get('required_skills', [])[:6])}
- Key Responsibilities: {', '.join(parsed_data.get('responsibilities', [])[:3])}

**Desired Tone:** {tone}

**Instructions:**
1. Create a personalized cover letter with the following structure
2. Opening paragraph: Express enthusiasm and mention how you found the position
3. Body paragraphs (2-3): Highlight relevant experience, skills, and achievements that match the job requirements
4. Closing paragraph: Reiterate interest and include a call to action
5. Use specific examples from the candidate's experience
6. Match keywords from the job description naturally
7. Keep professional yet engaging
8. Total length: 3-4 paragraphs, approximately 250-350 words

**Return Format (JSON only):**
{{
  "opening": "Opening paragraph text...",
  "body": [
    "First body paragraph...",
    "Second body paragraph...",
    "Third body paragraph (optional)..."
  ],
  "closing": "Closing paragraph text...",
  "full_text": "Complete cover letter with all paragraphs..."
}}

Generate the cover letter now:
"""
        return prompt
    
    def _get_fallback_cover_letter(self, profile: dict, job_description: dict) -> dict:
        """Fallback cover letter if AI fails"""
        personal_info = profile.get("personal_info", {})
        name = personal_info.get("full_name", "Candidate")
        title = personal_info.get("title", "Professional")
        job_title = job_description.get("title", "Position")
        company = job_description.get("company", "Company")
        
        opening = f"I am writing to express my strong interest in the {job_title} position at {company}. With my background as a {title}, I am confident that I can contribute effectively to your team."
        
        body1 = f"Throughout my career, I have developed strong expertise in the key areas required for this role. My experience has equipped me with the skills necessary to excel in this position and deliver meaningful results."
        
        body2 = f"I am particularly drawn to {company} because of your reputation for innovation and excellence. I am excited about the opportunity to bring my skills and passion to your organization."
        
        closing = f"Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to {company}'s continued success. Please feel free to contact me at your convenience."
        
        full_text = f"{opening}\n\n{body1}\n\n{body2}\n\n{closing}"
        
        return {
            "opening": opening,
            "body": [body1, body2],
            "closing": closing,
            "full_text": full_text
        }
