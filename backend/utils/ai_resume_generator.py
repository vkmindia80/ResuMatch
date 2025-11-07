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
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
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
            from emergentintegrations.llm.chat import UserMessage
            
            prompt = self._build_summary_prompt(profile, job_description)
            
            system_message = "You are an expert resume writer. Create compelling, ATS-optimized professional summaries that highlight key achievements and skills."
            
            # Create chat client
            client = LlmChat(
                api_key=self.api_key,
                session_id=f"resume_summary_{hash(profile.get('id', 'unknown'))}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini").with_params(temperature=0.7, max_tokens=300)
            
            # Send message (async)
            user_msg = UserMessage(text=prompt)
            response = await client.send_message(user_msg)
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
                
                from emergentintegrations.llm.chat import UserMessage
                
                prompt = self._build_experience_optimization_prompt(exp, job_description)
                
                system_message = "You are an expert resume writer. Transform experience descriptions into powerful, ATS-optimized bullet points using action verbs, quantifiable achievements, and impact statements."
                
                # Create chat client
                client = LlmChat(
                    api_key=self.api_key,
                    session_id=f"exp_opt_{hash(str(exp.get('company', 'unknown')))}",
                    system_message=system_message
                ).with_model("openai", "gpt-4o-mini").with_params(temperature=0.7, max_tokens=500)
                
                # Send message (async)
                user_msg = UserMessage(text=prompt)
                response = await client.send_message(user_msg)
                content = response.strip()
                
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
            
            from emergentintegrations.llm.chat import UserMessage
            
            prompt = self._build_skills_optimization_prompt(profile_skills, job_description)
            
            system_message = "You are an expert resume optimizer. Prioritize and organize skills to match job requirements while maintaining honesty. Return valid JSON only."
            
            # Create chat client
            client = LlmChat(
                api_key=self.api_key,
                session_id=f"skills_opt_{hash(str(job_description.get('id', 'unknown')))}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini").with_params(temperature=0.3, max_tokens=800)
            
            # Send message (async)
            user_msg = UserMessage(text=prompt)
            response = await client.send_message(user_msg)
            content = response.strip()
            
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
        for skill in skills.get("technical", [])[:8]:
            if isinstance(skill, dict):
                tech_skills.append(skill.get("name", ""))
            else:
                tech_skills.append(str(skill))
        
        # Extract key achievements from experience
        key_achievements = []
        for exp in experience[:3]:
            for resp in exp.get('responsibilities', [])[:2]:
                if any(metric in resp.lower() for metric in ['%', 'increase', 'improve', 'reduce', 'led', 'managed']):
                    key_achievements.append(resp[:100])
        
        prompt = f"""
Create a compelling, ATS-optimized professional summary for a resume.

**Profile Information:**
- Current Title: {title}
- Years of Experience: {years_of_exp}+
- Key Technical Skills: {', '.join(tech_skills)}
- Key Achievements: {'; '.join(key_achievements[:2]) if key_achievements else 'Various professional accomplishments'}
"""
        
        if job_description:
            parsed_data = job_description.get('parsed_data', {})
            required_skills = parsed_data.get('required_skills', [])[:8]
            technical_skills = parsed_data.get('technical_skills', [])[:8]
            
            prompt += f"""
**Target Role (CRITICAL - Optimize for ATS matching):**
- Position: {job_description.get('title', 'N/A')}
- Company: {job_description.get('company', 'N/A')}
- Required Skills: {', '.join(required_skills)}
- Technical Requirements: {', '.join(technical_skills)}
- Job Type: {job_description.get('job_type', 'N/A')}

**ATS OPTIMIZATION PRIORITY:**
- MUST include relevant keywords from required skills
- MUST use exact terminology from job description where applicable
- MUST highlight matching technical skills prominently
"""
        
        prompt += """
**Requirements:**
1. Write 3-4 powerful sentences (75-100 words total)
2. Start with years of experience and current title
3. Include SPECIFIC technical skills that match the job (use exact keywords)
4. Mention quantifiable achievements or impact (if available)
5. Use industry-standard terminology for ATS parsing
6. Include relevant keywords naturally without keyword stuffing
7. Do NOT use first person pronouns (I, me, my)
8. Focus on value proposition and results
9. Use active, confident language
10. Ensure every word adds value

**Example Structure:**
"[Title] with [X]+ years of experience in [domain/industry] specializing in [key skills]. Proven expertise in [technical skills matching job] with a track record of [achievement]. Skilled in [more matching skills] with experience in [relevant areas]. [Optional: certification or specialization]."

Write the professional summary now (3-4 sentences, no title, optimize for ATS):
"""
        return prompt
    
    def _build_experience_optimization_prompt(
        self,
        exp: dict,
        job_description: Optional[dict]
    ) -> str:
        """Build prompt for experience optimization"""
        prompt = f"""
Transform work experience into powerful, ATS-optimized bullet points that will score high with both ATS systems and recruiters.

**Position:**
- Company: {exp.get('company', 'N/A')}
- Title: {exp.get('title', 'N/A')}
- Duration: {exp.get('start_date', 'N/A')} to {'Present' if exp.get('is_current') else exp.get('end_date', 'N/A')}
- Location: {exp.get('location', 'N/A')}

**Current Responsibilities/Achievements:**
"""
        for i, resp in enumerate(exp.get('responsibilities', []), 1):
            prompt += f"{i}. {resp}\n"
        
        if job_description:
            parsed_data = job_description.get('parsed_data', {})
            required_skills = parsed_data.get('required_skills', [])[:8]
            technical_skills = parsed_data.get('technical_skills', [])[:8]
            tools = parsed_data.get('tools_and_technologies', [])[:8]
            
            prompt += f"""
**TARGET JOB REQUIREMENTS (CRITICAL for ATS matching):**
- Required Skills: {', '.join(required_skills)}
- Technical Skills: {', '.join(technical_skills)}
- Tools/Technologies: {', '.join(tools)}

**KEYWORD MATCHING PRIORITY:**
Match and incorporate these keywords naturally if relevant to the role:
{', '.join(required_skills[:15] + technical_skills[:15])}
"""
        
        prompt += """
**OPTIMIZATION FORMULA (Use CAR/STAR Method):**
[Action Verb] + [What you did] + [With what/How] + [Quantifiable Result/Impact]

**REQUIREMENTS:**
1. **Action Verbs**: Start EVERY bullet with a powerful action verb:
   - Leadership: Led, Directed, Managed, Coordinated, Supervised, Mentored
   - Creation: Developed, Built, Created, Designed, Implemented, Established
   - Improvement: Optimized, Enhanced, Streamlined, Increased, Reduced, Transformed
   - Achievement: Achieved, Accomplished, Exceeded, Delivered, Completed
   - Technical: Architected, Engineered, Programmed, Automated, Integrated

2. **Quantification**: Include numbers/metrics wherever possible:
   - Percentages (improved by 40%)
   - Numbers (managed team of 10)
   - Dollar amounts ($2M budget)
   - Time saved (reduced processing time by 50%)
   - Scale (processed 10K+ requests daily)

3. **Impact Focus**: Show RESULTS and BUSINESS IMPACT:
   - Before: "Worked on web applications"
   - After: "Architected scalable web platform serving 100K+ users, reducing load time by 60%"

4. **Keyword Integration**: Naturally incorporate relevant technical keywords and tools from job requirements

5. **ATS Formatting**:
   - Use standard terms (not abbreviations unless industry-standard)
   - Include technical skills mentioned in job posting
   - Use context that ATS can parse (no special characters)
   - Keep to 1-2 lines per bullet

6. **Relevance**: Prioritize most impressive and relevant achievements for target role

7. **Conciseness**: Maximum 2 lines per bullet, no fluff words

**EXAMPLES OF EXCELLENT BULLETS:**
- "Led cross-functional team of 8 engineers to deliver microservices architecture, reducing system latency by 45% and improving uptime to 99.9%"
- "Developed automated CI/CD pipeline using Jenkins and Docker, cutting deployment time from 2 hours to 15 minutes and eliminating 90% of production bugs"
- "Architected React-based dashboard processing 50K+ daily transactions, increasing user engagement by 35% through intuitive UX design"

Return 4-6 optimized bullet points (one per line, start with action verb, no numbering or bullet symbols):
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
