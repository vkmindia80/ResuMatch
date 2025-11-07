"""
AI-Powered Interview Question Generator
Generates role-specific interview questions with STAR-format answers
"""
import os
import json
from typing import Dict, List
from emergentintegrations.llm.openai import LlmChat

class AIInterviewGenerator:
    def __init__(self):
        """Initialize AI Interview Generator with Emergent LLM Key"""
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def generate_interview_questions(
        self,
        job_description: dict,
        profile: dict,
        count: int = 25
    ) -> List[dict]:
        """
        Generate AI-powered interview questions with STAR-format answers
        
        Args:
            job_description: Job description dictionary
            profile: User profile dictionary
            count: Number of questions to generate
            
        Returns:
            List of question dictionaries with STAR answers
        """
        try:
            # Generate questions by category
            questions = []
            
            # Behavioral questions (40%)
            behavioral_count = int(count * 0.4)
            behavioral_qs = await self._generate_category_questions(
                "behavioral",
                behavioral_count,
                job_description,
                profile
            )
            questions.extend(behavioral_qs)
            
            # Technical questions (30%)
            technical_count = int(count * 0.3)
            technical_qs = await self._generate_category_questions(
                "technical",
                technical_count,
                job_description,
                profile
            )
            questions.extend(technical_qs)
            
            # Culture fit questions (15%)
            culture_count = int(count * 0.15)
            culture_qs = await self._generate_category_questions(
                "culture_fit",
                culture_count,
                job_description,
                profile
            )
            questions.extend(culture_qs)
            
            # Situational questions (15%)
            situational_count = count - len(questions)
            situational_qs = await self._generate_category_questions(
                "situational",
                situational_count,
                job_description,
                profile
            )
            questions.extend(situational_qs)
            
            return questions
            
        except Exception as e:
            print(f"Error generating interview questions with AI: {e}")
            return []
    
    async def _generate_category_questions(
        self,
        category: str,
        count: int,
        job_description: dict,
        profile: dict
    ) -> List[dict]:
        """Generate questions for a specific category"""
        try:
            prompt = self._build_question_prompt(category, count, job_description, profile)
            
            system_message = "You are an expert interview coach. Generate realistic, role-specific interview questions with STAR-format answers based on the candidate's actual experience. Return valid JSON only."
            
            response = self.client.chat(
                messages=[prompt],
                system_message=system_message,
                temperature=0.8,
                max_tokens=2500
            )
            
            content = response.strip()
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            questions_data = json.loads(content)
            
            # Ensure it's a list
            if isinstance(questions_data, dict):
                questions_data = questions_data.get("questions", [])
            
            return questions_data
            
        except Exception as e:
            print(f"Error generating {category} questions: {e}")
            return []
    
    def _build_question_prompt(
        self,
        category: str,
        count: int,
        job_description: dict,
        profile: dict
    ) -> str:
        """Build prompt for question generation"""
        
        parsed_data = job_description.get('parsed_data', {})
        personal_info = profile.get("personal_info", {})
        experience = profile.get("experience", [])
        
        # Build experience summary
        exp_summary = []
        for exp in experience[:3]:  # Top 3 experiences
            exp_summary.append(
                f"- {exp.get('title')} at {exp.get('company')}: {', '.join(exp.get('responsibilities', [])[:2])}"
            )
        
        category_descriptions = {
            "behavioral": "past experiences and how the candidate handled specific situations",
            "technical": "role-specific technical skills, problem-solving, and expertise",
            "culture_fit": "values alignment, work style, and company culture match",
            "situational": "hypothetical scenarios and how the candidate would handle them"
        }
        
        prompt = f"""
Generate {count} {category} interview questions for the following job opportunity, along with STAR-format answers based on the candidate's actual experience.

**Job Information:**
- Title: {job_description.get('title')}
- Company: {job_description.get('company')}
- Required Skills: {', '.join(parsed_data.get('required_skills', [])[:5])}
- Job Level: {parsed_data.get('job_level', 'N/A')}

**Candidate Profile:**
- Current Title: {personal_info.get('title', 'N/A')}
- Recent Experience:
{chr(10).join(exp_summary)}
- Key Skills: {', '.join([s.get('name') if isinstance(s, dict) else str(s) for s in profile.get('skills', {}).get('technical', [])[:5]])}

**Category Focus:**
{category} questions focus on {category_descriptions.get(category, 'general interview topics')}.

**Instructions:**
1. Generate {count} realistic, role-specific questions
2. Vary difficulty: mix of easy, medium, and hard questions
3. For each question, create a STAR-format answer using the candidate's ACTUAL experience
4. STAR format: Situation, Task, Action, Result
5. Make answers realistic and specific to the candidate's background
6. Keep answers concise (3-5 sentences per component)

**Return Format (JSON only):**
[
  {{
    "question": "Question text here",
    "category": "{category}",
    "difficulty": "easy|medium|hard",
    "ai_generated_answer": {{
      "situation": "Context and background...",
      "task": "The challenge or responsibility...",
      "action": "Specific steps taken...",
      "result": "Measurable outcome and impact...",
      "full_answer": "Complete STAR answer in paragraph form..."
    }}
  }},
  ...
]

Generate the {count} questions now:
"""
        return prompt
