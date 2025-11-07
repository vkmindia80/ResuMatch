"""
AI-Powered Job Description Parser
Uses OpenAI via Emergent LLM Key to intelligently parse job descriptions
"""
import os
import json
from typing import Dict, List, Optional
from emergentintegrations.llm.openai import LlmChat

class AIJobParser:
    def __init__(self):
        """Initialize AI Job Parser with Emergent LLM Key"""
        api_key = os.getenv('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        self.client = LlmChat(api_key=api_key, model="gpt-4o-mini")
    
    async def parse_job_description(self, job_data: dict) -> dict:
        """
        Parse job description using AI to extract structured information
        
        Args:
            job_data: Dictionary containing title, company, description, location, job_type
            
        Returns:
            Dictionary with parsed information
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_parsing_prompt(job_data)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert job description analyzer. Extract structured information from job postings accurately and comprehensively. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low temperature for consistent extraction
                max_tokens=2000
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            parsed_data = json.loads(content)
            
            return {
                "success": True,
                "data": parsed_data
            }
            
        except Exception as e:
            print(f"Error parsing job description with AI: {e}")
            # Return basic fallback
            return {
                "success": False,
                "error": str(e),
                "data": self._get_fallback_parse(job_data)
            }
    
    def _build_parsing_prompt(self, job_data: dict) -> str:
        """Build the parsing prompt for AI"""
        return f"""
Analyze the following job posting and extract structured information in JSON format.

**Job Information:**
- Title: {job_data.get('title', 'N/A')}
- Company: {job_data.get('company', 'N/A')}
- Location: {job_data.get('location', 'N/A')}
- Job Type: {job_data.get('job_type', 'N/A')}

**Job Description:**
{job_data.get('description', '')}

**Extract and return the following information in JSON format:**

{{
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", "skill2", ...],
  "technical_skills": ["Python", "React", ...],
  "soft_skills": ["communication", "leadership", ...],
  "tools_and_technologies": ["Docker", "AWS", ...],
  "required_experience_years": 3,
  "education_requirements": ["Bachelor's degree in CS", ...],
  "responsibilities": ["Design and develop...", ...],
  "qualifications": ["3+ years experience...", ...],
  "benefits": ["Health insurance", "401k", ...],
  "company_culture_keywords": ["collaborative", "innovative", ...],
  "job_level": "mid-level",
  "industry": "Technology",
  "salary_range": "$80,000 - $120,000",
  "key_requirements_summary": "Brief 1-2 sentence summary of must-have requirements"
}}

**Guidelines:**
1. Extract all technical skills mentioned (programming languages, frameworks, tools)
2. Identify soft skills (leadership, communication, problem-solving, etc.)
3. Separate REQUIRED vs PREFERRED skills based on language used
4. Estimate experience years from phrases like "3+ years", "senior level", etc.
5. Extract specific responsibilities and qualifications
6. Identify company culture keywords from description
7. Classify job level: entry-level, mid-level, senior, lead, or executive
8. Determine the industry category
9. Extract salary if mentioned, otherwise return null
10. Return ONLY valid JSON, no additional text

Return the JSON now:
"""
    
    def _get_fallback_parse(self, job_data: dict) -> dict:
        """Fallback parsing if AI fails"""
        return {
            "required_skills": [],
            "preferred_skills": [],
            "technical_skills": [],
            "soft_skills": [],
            "tools_and_technologies": [],
            "required_experience_years": 0,
            "education_requirements": [],
            "responsibilities": [],
            "qualifications": [],
            "benefits": [],
            "company_culture_keywords": [],
            "job_level": "unknown",
            "industry": "unknown",
            "salary_range": None,
            "key_requirements_summary": job_data.get('description', '')[:200]
        }
