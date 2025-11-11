"""
AI-powered suggestions for profile enhancements
Generates achievement suggestions and skill categorization
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

load_dotenv()


class AISuggestionEngine:
    """Generate AI-powered suggestions for profile content"""
    
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def suggest_achievements(
        self,
        job_title: str,
        company: str,
        responsibilities: List[str],
        technologies: List[str] = None
    ) -> List[str]:
        """
        Generate achievement suggestions based on role and responsibilities
        
        Args:
            job_title: Job title
            company: Company name
            responsibilities: List of responsibilities
            technologies: List of technologies used
            
        Returns:
            List of suggested achievements
        """
        system_message = """You are an expert career coach and resume writer. Your task is to generate impactful achievement statements based on job responsibilities.

Guidelines:
- Use action verbs (Achieved, Improved, Led, Developed, Increased, etc.)
- Include quantifiable metrics when possible (percentages, numbers, time saved)
- Focus on impact and results, not just tasks
- Keep each achievement concise (1-2 lines)
- Make them specific and measurable
- Return ONLY a JSON array of strings, no extra text

Example output format:
["Achievement 1", "Achievement 2", "Achievement 3"]"""

        technologies_text = f"\nTechnologies used: {', '.join(technologies)}" if technologies else ""
        responsibilities_text = "\n- ".join(responsibilities) if responsibilities else "General responsibilities"
        
        user_prompt = f"""Generate 5 impactful achievement statements for the following role:

Job Title: {job_title}
Company: {company}
Responsibilities:
- {responsibilities_text}{technologies_text}

Return a JSON array of 5 achievement suggestions."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"achievements_{hash(job_title + company)}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")
            
            response = await chat.send_message(UserMessage(text=user_prompt))
            
            # Parse JSON response
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            achievements = json.loads(response_text)
            return achievements if isinstance(achievements, list) else []
            
        except Exception as e:
            print(f"Error generating achievement suggestions: {str(e)}")
            return []
    
    async def suggest_skills(
        self,
        job_title: str = None,
        industry: str = None,
        current_skills: List[str] = None,
        experience_level: str = "Intermediate"
    ) -> Dict[str, List[str]]:
        """
        Generate skill suggestions categorized as technical and soft skills
        
        Args:
            job_title: Job title for context
            industry: Industry for context
            current_skills: Existing skills
            experience_level: Experience level (Beginner, Intermediate, Advanced, Expert)
            
        Returns:
            Dictionary with 'technical' and 'soft' skill suggestions
        """
        system_message = """You are an expert career advisor specializing in skill development. Generate relevant skill suggestions based on job role and industry.

Guidelines:
- Separate skills into technical and soft skills
- Suggest 8-10 technical skills relevant to the role
- Suggest 6-8 soft skills important for success
- Consider the experience level
- Include both current industry standards and emerging skills
- Return ONLY valid JSON, no extra text

Output format:
{
  "technical": ["Skill 1", "Skill 2", ...],
  "soft": ["Skill 1", "Skill 2", ...]
}"""

        context_parts = []
        if job_title:
            context_parts.append(f"Job Title: {job_title}")
        if industry:
            context_parts.append(f"Industry: {industry}")
        if current_skills:
            context_parts.append(f"Current Skills: {', '.join(current_skills[:10])}")
        
        context_text = "\n".join(context_parts) if context_parts else "General professional role"
        
        user_prompt = f"""Generate skill suggestions for the following profile:

{context_text}
Experience Level: {experience_level}

Provide a comprehensive list of technical skills and soft skills that would be valuable."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"skills_{hash(str(job_title) + str(industry))}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")
            
            response = await chat.send_message(UserMessage(text=user_prompt))
            
            # Parse JSON response
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            skills = json.loads(response_text)
            
            return {
                "technical": skills.get("technical", []),
                "soft": skills.get("soft", [])
            }
            
        except Exception as e:
            print(f"Error generating skill suggestions: {str(e)}")
            return {"technical": [], "soft": []}
    
    async def categorize_skills(
        self,
        skills: List[str]
    ) -> Dict[str, List[str]]:
        """
        Categorize a list of skills into technical and soft skills
        
        Args:
            skills: List of skill names
            
        Returns:
            Dictionary with categorized skills
        """
        if not skills:
            return {"technical": [], "soft": []}
        
        system_message = """You are an expert at categorizing professional skills. Classify each skill as either technical or soft.

Technical skills: Programming languages, tools, frameworks, technologies, certifications, technical methodologies
Soft skills: Communication, leadership, teamwork, problem-solving, time management, interpersonal skills

Return ONLY valid JSON in this format:
{
  "technical": ["Skill 1", "Skill 2", ...],
  "soft": ["Skill 1", "Skill 2", ...]
}"""

        user_prompt = f"""Categorize these skills into technical and soft skills:

{', '.join(skills)}

Return the categorized skills in JSON format."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"categorize_{hash(str(skills))}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")
            
            response = await chat.send_message(UserMessage(text=user_prompt))
            
            # Parse JSON response
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            categorized = json.loads(response_text)
            
            return {
                "technical": categorized.get("technical", []),
                "soft": categorized.get("soft", [])
            }
            
        except Exception as e:
            print(f"Error categorizing skills: {str(e)}")
            return {"technical": skills, "soft": []}
    
    async def suggest_responsibilities(
        self,
        job_title: str,
        company: str,
        current_responsibilities: List[str] = None,
        technologies: List[str] = None,
        job_description: str = None
    ) -> List[str]:
        """
        Generate responsibility suggestions based on role and context
        
        Args:
            job_title: Job title
            company: Company name
            current_responsibilities: Existing responsibilities (optional)
            technologies: List of technologies used (optional)
            job_description: Job description for context (optional)
            
        Returns:
            List of suggested responsibilities
        """
        system_message = """You are an expert resume writer specializing in crafting impactful responsibility statements.

Guidelines:
- Start with strong action verbs (Develop, Design, Implement, Manage, Lead, etc.)
- Be specific and concrete about the work performed
- Focus on day-to-day activities and core duties
- Keep each responsibility clear and concise (1 line)
- Make them relevant to the role and industry
- Return ONLY a JSON array of strings, no extra text

Example output format:
["Responsibility 1", "Responsibility 2", "Responsibility 3"]"""

        technologies_text = f"\nTechnologies: {', '.join(technologies)}" if technologies else ""
        current_resp_text = f"\nCurrent responsibilities: {', '.join(current_responsibilities[:3])}" if current_responsibilities else ""
        job_desc_text = f"\n\nJob Description Context:\n{job_description[:500]}" if job_description else ""
        
        user_prompt = f"""Generate 5 impactful responsibility statements for the following role:

Job Title: {job_title}
Company: {company}{technologies_text}{current_resp_text}{job_desc_text}

Return a JSON array of 5 responsibility suggestions that complement any existing responsibilities."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"responsibilities_{hash(job_title + company)}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")
            
            response = await chat.send_message(UserMessage(text=user_prompt))
            
            # Parse JSON response
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            responsibilities = json.loads(response_text)
            return responsibilities if isinstance(responsibilities, list) else []
            
        except Exception as e:
            print(f"Error generating responsibility suggestions: {str(e)}")
            return []
    
    async def suggest_technologies(
        self,
        job_title: str,
        company: str = None,
        current_technologies: List[str] = None,
        industry: str = None,
        job_description: str = None
    ) -> List[str]:
        """
        Generate technology/tool suggestions based on role, industry, and job description
        
        Args:
            job_title: Job title
            company: Company name (optional)
            current_technologies: Existing technologies (optional)
            industry: Industry context (optional)
            job_description: Job description to extract relevant technologies (optional)
            
        Returns:
            List of suggested technologies
        """
        system_message = """You are an expert technical recruiter and resume advisor specializing in technology stacks.

Guidelines:
- Suggest relevant technologies, tools, frameworks, and platforms for the role
- Include both current industry standards and emerging technologies
- Consider the job description requirements if provided
- Suggest 5-8 technologies that complement existing tech stack
- Focus on practical, in-demand technologies
- Return ONLY a JSON array of strings, no extra text

Example output format:
["Technology 1", "Technology 2", "Technology 3"]"""

        current_tech_text = f"\nCurrent Technologies: {', '.join(current_technologies)}" if current_technologies else ""
        industry_text = f"\nIndustry: {industry}" if industry else ""
        company_text = f"\nCompany: {company}" if company else ""
        
        # Extract key requirements from job description if provided
        job_context = ""
        if job_description:
            job_context = f"\n\nJob Description Context (extract relevant technologies):\n{job_description[:600]}"
        
        user_prompt = f"""Generate technology/tool suggestions for the following role:

Job Title: {job_title}{company_text}{industry_text}{current_tech_text}{job_context}

Return a JSON array of 5-8 technology suggestions that would be valuable for this role."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"technologies_{hash(job_title + str(industry))}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")
            
            response = await chat.send_message(UserMessage(text=user_prompt))
            
            # Parse JSON response
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            technologies = json.loads(response_text)
            return technologies if isinstance(technologies, list) else []
            
        except Exception as e:
            print(f"Error generating technology suggestions: {str(e)}")
            return []


# Singleton instance
ai_suggestion_engine = AISuggestionEngine()
