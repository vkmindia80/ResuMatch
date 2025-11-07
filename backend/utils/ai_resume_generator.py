"""
AI-Powered Resume Generator
Uses OpenAI via Emergent LLM Key to generate optimized resume content
"""
import os
import json
from typing import Dict, List, Optional
from emergentintegrations.llm.openai import LlmChat

class AIResumeGenerator:
    def __init__(self):
        """Initialize AI Resume Generator with Emergent LLM Key"""
        api_key = os.getenv('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        self.client = LlmChat(api_key=api_key, model="gpt-4o-mini")
    
    async def generate_professional_summary(
        self,
        profile: dict,
        job_description: Optional[dict] = None
    ) -> str:
        """
        Generate a personalized professional summary
        
        Args:
            profile: User profile data
            job_description: Optional job description to tailor summary
            
        Returns:
            Professional summary string
        """
        try:
            prompt = self._build_summary_prompt(profile, job_description)
            
            system_message = "You are an expert resume writer. Create compelling, ATS-optimized professional summaries that highlight key achievements and skills."
            
            response = self.client.chat(
                messages=[prompt],
                system_message=system_message,
                temperature=0.7,
                max_tokens=300
            )
            
            summary = response.strip()
            return summary
            
        except Exception as e:
            print(f"Error generating summary with AI: {e}")
            return self._get_fallback_summary(profile)
    
    async def optimize_experience_bullets(
        self,
        experience: list,
        job_description: Optional[dict] = None
    ) -> list:
        """
        Optimize experience bullet points with action verbs and impact
        
        Args:
            experience: List of experience entries
            job_description: Optional job description to match keywords
            
        Returns:
            List of experience entries with optimized bullet points
        """
        try:
            optimized_experience = []
            
            for exp in experience:
                # Skip if no responsibilities
                if not exp.get("responsibilities"):
                    optimized_experience.append(exp)
                    continue
                
                prompt = self._build_experience_optimization_prompt(exp, job_description)
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert resume writer. Transform experience descriptions into powerful, ATS-optimized bullet points using action verbs, quantifiable achievements, and impact statements."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                content = response.choices[0].message.content.strip()
                
                # Parse optimized bullets
                optimized_bullets = [
                    line.strip().lstrip('•').lstrip('-').strip()
                    for line in content.split('\n')
                    if line.strip() and not line.strip().startswith('#')
                ]
                
                exp_copy = exp.copy()
                exp_copy["optimized_responsibilities"] = optimized_bullets
                optimized_experience.append(exp_copy)
            
            return optimized_experience
            
        except Exception as e:
            print(f"Error optimizing experience with AI: {e}")
            return experience
    
    async def generate_skills_optimization(
        self,
        profile_skills: dict,
        job_description: Optional[dict] = None
    ) -> dict:
        """
        Optimize and prioritize skills based on job requirements
        
        Args:
            profile_skills: User's skills from profile
            job_description: Optional job description to match
            
        Returns:
            Optimized skills dictionary with prioritized ordering
        """
        try:
            if not job_description:
                return profile_skills
            
            prompt = self._build_skills_optimization_prompt(profile_skills, job_description)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume optimizer. Prioritize and organize skills to match job requirements while maintaining honesty. Return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            optimized_skills = json.loads(content)
            return optimized_skills
            
        except Exception as e:
            print(f"Error optimizing skills with AI: {e}")
            return profile_skills
    
    def _build_summary_prompt(self, profile: dict, job_description: Optional[dict]) -> str:
        """Build prompt for professional summary generation"""
        personal_info = profile.get("personal_info", {})
        experience = profile.get("experience", [])
        skills = profile.get("skills", {})
        
        years_of_exp = len(experience)
        title = personal_info.get("title", "Professional")
        
        # Get top technical skills
        tech_skills = []
        for skill in skills.get("technical", [])[:5]:
            if isinstance(skill, dict):
                tech_skills.append(skill.get("name", ""))
            else:
                tech_skills.append(str(skill))
        
        prompt = f"""
Create a compelling professional summary for a resume.

**Profile Information:**
- Current Title: {title}
- Years of Experience: {years_of_exp}+
- Key Technical Skills: {', '.join(tech_skills)}
"""
        
        if job_description:
            prompt += f"""
**Target Role:**
- Position: {job_description.get('title', 'N/A')}
- Company: {job_description.get('company', 'N/A')}
- Key Requirements: {', '.join(job_description.get('parsed_data', {}).get('required_skills', [])[:5])}
"""
        
        prompt += """
**Requirements:**
1. Write a 3-4 sentence professional summary
2. Highlight relevant experience and achievements
3. Include key technical skills naturally
4. Use action-oriented language
5. Make it ATS-friendly with relevant keywords
6. Do NOT use first person pronouns (I, me, my)
7. Focus on impact and value proposition

Write the professional summary now (3-4 sentences only, no title):
"""
        return prompt
    
    def _build_experience_optimization_prompt(
        self,
        exp: dict,
        job_description: Optional[dict]
    ) -> str:
        """Build prompt for experience optimization"""
        prompt = f"""
Optimize the following work experience into powerful, ATS-optimized bullet points.

**Position:**
- Company: {exp.get('company', 'N/A')}
- Title: {exp.get('title', 'N/A')}
- Duration: {exp.get('start_date', 'N/A')} to {exp.get('end_date', 'Present')}

**Current Responsibilities:**
"""
        for resp in exp.get('responsibilities', []):
            prompt += f"- {resp}\n"
        
        if job_description:
            parsed_data = job_description.get('parsed_data', {})
            required_skills = parsed_data.get('required_skills', [])[:5]
            if required_skills:
                prompt += f"\n**Target Job Requirements:** {', '.join(required_skills)}\n"
        
        prompt += """
**Optimization Requirements:**
1. Start each bullet with a strong action verb (Led, Developed, Implemented, etc.)
2. Quantify achievements where possible (percentages, numbers, metrics)
3. Show impact and results (improved, increased, reduced, etc.)
4. Include relevant technical skills naturally
5. Keep bullets concise (1-2 lines max)
6. Make them ATS-friendly
7. Prioritize most impressive achievements
8. Match keywords from target job if provided

Return 3-5 optimized bullet points (one per line, no numbering):
"""
        return prompt
    
    def _build_skills_optimization_prompt(
        self,
        profile_skills: dict,
        job_description: dict
    ) -> str:
        """Build prompt for skills optimization"""
        tech_skills = []
        for skill in profile_skills.get("technical", []):
            if isinstance(skill, dict):
                tech_skills.append(skill.get("name", ""))
            else:
                tech_skills.append(str(skill))
        
        parsed_data = job_description.get('parsed_data', {})
        
        prompt = f"""
Optimize and prioritize skills for a resume based on job requirements.

**User's Skills:**
- Technical: {', '.join(tech_skills)}
- Soft Skills: {', '.join(profile_skills.get('soft', []))}
- Tools: {', '.join(profile_skills.get('tools', []))}

**Job Requirements:**
- Required Skills: {', '.join(parsed_data.get('required_skills', []))}
- Technical Skills: {', '.join(parsed_data.get('technical_skills', []))}
- Tools: {', '.join(parsed_data.get('tools_and_technologies', []))}

**Task:**
1. Prioritize user's skills that match job requirements at the top
2. Keep the same skills the user has (don't add skills they don't have)
3. Organize into categories: technical, soft, languages, tools
4. Remove duplicates
5. Ensure relevance to the target role

Return the optimized skills in this JSON format:
{{
  "technical": [
    {{"name": "skill_name", "level": "advanced"}},
    ...
  ],
  "soft": ["skill1", "skill2", ...],
  "languages": [
    {{"name": "language_name", "fluency": "fluent"}},
    ...
  ],
  "tools": ["tool1", "tool2", ...]
}}

Return JSON only:
"""
        return prompt
    
    def _get_fallback_summary(self, profile: dict) -> str:
        """Fallback summary if AI fails"""
        personal_info = profile.get("personal_info", {})
        title = personal_info.get("title", "Professional")
        experience_count = len(profile.get("experience", []))
        
        return f"{title} with {experience_count}+ years of experience in delivering high-quality solutions. Proven track record of success in fast-paced environments with strong technical and interpersonal skills."
