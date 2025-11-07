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
        """Build prompt for professional summary generation - Enhanced v2.0"""
        personal_info = profile.get("personal_info", {})
        experience = profile.get("experience", [])
        skills = profile.get("skills", {})
        
        years_of_exp = len(experience)
        title = personal_info.get("title", "Professional")
        
        # Get top technical skills
        tech_skills = []
        for skill in skills.get("technical", [])[:12]:  # Increased from 8 to 12
            if isinstance(skill, dict):
                tech_skills.append(skill.get("name", ""))
            else:
                tech_skills.append(str(skill))
        
        # Extract key achievements with metrics
        key_achievements = []
        for exp in experience[:3]:
            for resp in exp.get('responsibilities', [])[:2]:
                if any(metric in resp.lower() for metric in ['%', 'increase', 'improve', 'reduce', 'led', 'managed', '$', 'grew']):
                    key_achievements.append(resp[:120])
        
        prompt = f"""
CREATE A PERFECT ATS-OPTIMIZED PROFESSIONAL SUMMARY (TARGET: 95%+ ATS SCORE)

**Profile Information:**
- Current Title: {title}
- Years of Experience: {years_of_exp}+
- Top Technical Skills: {', '.join(tech_skills)}
- Quantified Achievements: {'; '.join(key_achievements[:3]) if key_achievements else 'Professional accomplishments across various domains'}
"""
        
        if job_description:
            parsed_data = job_description.get('parsed_data', {})
            required_skills = parsed_data.get('required_skills', [])[:15]  # Increased from 8
            technical_skills = parsed_data.get('technical_skills', [])[:15]  # Increased from 8
            tools = parsed_data.get('tools_and_technologies', [])[:10]
            
            prompt += f"""
**TARGET ROLE - CRITICAL FOR ATS OPTIMIZATION:**
- Position: {job_description.get('title', 'N/A')}
- Company: {job_description.get('company', 'N/A')}
- MUST-HAVE Required Skills: {', '.join(required_skills)}
- CRITICAL Technical Skills: {', '.join(technical_skills)}
- Key Tools/Technologies: {', '.join(tools)}
- Experience Level: {parsed_data.get('job_level', 'N/A')}

**ATS KEYWORD INTEGRATION (HIGHEST PRIORITY):**
\u26a1 MUST include 10-12 EXACT keywords from required & technical skills
\u26a1 MUST use EXACT terminology from job description (not synonyms)
\u26a1 MUST integrate keywords NATURALLY (no keyword stuffing)
\u26a1 MUST highlight matching technical skills PROMINENTLY
"""
        
        prompt += """
**MANDATORY ATS PERFECTION REQUIREMENTS:**
1. \ud83d\udccc LENGTH: Exactly 3-4 powerful sentences (90-120 words)
2. \ud83d\udd11 KEYWORDS: Include 10-12 EXACT keywords from job requirements
3. \u26a1 OPENING: Start with "[Experience Level + Title] with [X]+ years"
4. \ud83d\udcca METRICS: Include 1-2 quantifiable achievements with specific numbers
5. \ud83d\udee0\ufe0f TECHNICAL: List 8-10 relevant technologies/tools naturally
6. \ud83c\udfaf ATS-FRIENDLY: Use industry-standard terminology, no abbreviations unless standard
7. \ud83d\udca5 IMPACT-FOCUSED: Emphasize results, value delivery, and business impact
8. \ud83d\udcbc CONFIDENT: Active voice, strong language, no weak words
9. \ud83d\udeab NO PRONOUNS: Third person only (no "I", "me", "my")
10. \ud83d\udcaf PRECISION: Every word adds value - zero fluff

**PERFECT SUMMARY STRUCTURE:**
Sentence 1: [Title] with [X]+ years in [domain] specializing in [3-4 critical keywords]
Sentence 2: Proven expertise in [4-5 technical skills] with track record of [quantified achievement]
Sentence 3: Skilled in [3-4 more matching skills/tools] with experience in [relevant areas]
Sentence 4 (optional): [Certification/specialization] with focus on [specific expertise area]

**EXAMPLE OF 98% ATS SCORE SUMMARY:**
"Senior Software Engineer with 7+ years of experience building scalable web applications using React, Node.js, Python, and AWS cloud infrastructure. Proven expertise in microservices architecture, CI/CD automation, and agile methodologies, consistently delivering projects that reduced system latency by 65% and increased deployment efficiency by 80%. Skilled in Docker, Kubernetes, PostgreSQL, MongoDB, and RESTful API development with hands-on experience leading cross-functional teams of 10+ engineers. AWS Certified Solutions Architect specializing in serverless computing, infrastructure-as-code, and DevOps best practices."

Write the perfect professional summary now (3-4 sentences, 90-120 words, keyword-rich, ATS-optimized):
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
**PERFECT ATS OPTIMIZATION FORMULA:**
[POWER VERB] + [Specific Action] + [Technology/Method Used] + [QUANTIFIED Result with Numbers] + [Business Impact]

**MANDATORY ATS PERFECTION REQUIREMENTS:**

1. \u26a1 **POWER ACTION VERBS** - Start EVERY bullet with these:
   - Leadership: Spearheaded, Orchestrated, Directed, Championed, Mentored
   - Creation: Architected, Engineered, Pioneered, Designed, Built
   - Improvement: Transformed, Optimized, Revolutionized, Streamlined, Accelerated
   - Achievement: Delivered, Exceeded, Achieved, Accomplished, Attained
   - Technical: Implemented, Automated, Integrated, Developed, Programmed

2. \ud83d\udcca **AGGRESSIVE QUANTIFICATION** - Include 2+ metrics per bullet:
   - Percentages: "increased by 45%", "reduced by 68%"
   - Scale: "serving 2M+ users", "processing 500K+ daily transactions"
   - Money: "$3M cost savings", "$15M revenue growth"
   - Time: "from 4 hours to 12 minutes", "50% faster delivery"
   - Team: "led team of 15", "managed 8 engineers"
   - Quality: "99.99% uptime", "eliminated 94% of bugs"

3. \ud83c\udfaf **KEYWORD INTEGRATION** - Naturally weave in job requirements:
   - Use EXACT technical terms from job posting
   - Include 2-3 relevant keywords per bullet
   - Mention specific tools/technologies used
   - Match industry terminology precisely

4. \ud83d\udca5 **IMPACT DEMONSTRATION** - Show measurable business value:
   \u274c Before: "Worked on web applications"
   \u2705 After: "Architected cloud-native web platform using React and AWS, serving 2M+ users with 99.9% uptime and reducing infrastructure costs by 40%"

5. \ud83d\udee0\ufe0f **TECHNICAL SPECIFICITY**:
   - Name exact technologies (React, Node.js, PostgreSQL, Docker, Kubernetes)
   - Include methodologies (Agile, CI/CD, microservices, serverless)
   - Specify tools/platforms (AWS, Jenkins, GitHub Actions, Terraform)

6. \ud83d\udcaf **ATS-FRIENDLY FORMATTING**:
   - Use full names, not abbreviations (JavaScript not JS)
   - Standard industry terms only
   - Each bullet 1-2 lines maximum
   - Clear, parseable structure

7. \ud83c\udd99 **RELEVANCE & PRIORITY**:
   - Most impressive achievements first
   - Directly relevant to target role
   - Recent/current work emphasized

**EXAMPLES OF PERFECT 98%+ ATS SCORE BULLETS:**
\u2022 "Spearheaded microservices migration using Docker, Kubernetes, and AWS ECS, reducing deployment time by 73% and enabling 2M+ daily active users with 99.99% uptime while cutting infrastructure costs by $450K annually"
\u2022 "Architected real-time analytics platform processing 800K+ transactions daily using Python, Apache Kafka, and PostgreSQL, delivering insights 85% faster and driving $2.5M in data-driven revenue growth"
\u2022 "Transformed legacy monolith to cloud-native architecture using React, Node.js, and serverless AWS Lambda, improving page load speed by 68% and increasing user engagement by 42% across 500K+ monthly active users"
\u2022 "Led cross-functional team of 12 engineers in agile development of enterprise SaaS platform, implementing CI/CD pipeline with Jenkins that accelerated release cycles by 60% and eliminated 91% of production bugs"

Return 4-6 PERFECT ATS-optimized bullets (one per line, start with power verb, NO numbering/symbols):
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
        
        soft_skills = profile_skills.get('soft', [])
        tools = profile_skills.get('tools', [])
        languages = profile_skills.get('languages', [])
        
        parsed_data = job_description.get('parsed_data', {})
        required_skills = parsed_data.get('required_skills', [])
        technical_skills = parsed_data.get('technical_skills', [])
        tools_tech = parsed_data.get('tools_and_technologies', [])
        
        prompt = f"""
Optimize and prioritize skills for maximum ATS score and recruiter impact.

**USER'S CURRENT SKILLS:**
- Technical: {', '.join(tech_skills)}
- Soft Skills: {', '.join(soft_skills)}
- Tools: {', '.join(tools)}
- Languages: {', '.join([lang.get('name') if isinstance(lang, dict) else lang for lang in languages])}

**JOB REQUIREMENTS (CRITICAL - Prioritize matching skills):**
- Required Skills: {', '.join(required_skills)}
- Technical Skills: {', '.join(technical_skills)}
- Tools & Technologies: {', '.join(tools_tech)}

**OPTIMIZATION STRATEGY:**

1. **PRIORITY MATCHING**: 
   - Identify user skills that EXACTLY match job requirements
   - Place matching skills at the TOP of each category
   - Use EXACT terminology from job posting (e.g., if job says "React.js", use "React.js" not "React")

2. **CATEGORIZATION**:
   - Technical: Programming languages, frameworks, methodologies
   - Soft: Leadership, communication, problem-solving, etc.
   - Tools: Software, platforms, applications
   - Languages: Spoken languages (if user has any)

3. **HONEST REPRESENTATION**:
   - DO NOT add skills the user doesn't have
   - Only reorder and recategorize existing skills
   - Keep all valuable skills even if not in job description

4. **ATS OPTIMIZATION**:
   - Use industry-standard naming (e.g., "JavaScript" not "JS")
   - Avoid abbreviations unless they're the standard (e.g., "SQL" is okay)
   - Group similar skills logically

5. **RELEVANCE RANKING**:
   - Most relevant/required skills first
   - Advanced/expert skills second
   - Supporting/nice-to-have skills last

**OUTPUT FORMAT** (Return as valid JSON, string arrays only - NO objects with name/level):
{{
  "technical": ["Skill1", "Skill2", "Skill3", ...],
  "soft": ["Skill1", "Skill2", "Skill3", ...],
  "tools": ["Tool1", "Tool2", "Tool3", ...],
  "languages": ["Language1", "Language2", ...]
}}

**EXAMPLE:**
If user has: Python, JavaScript, Leadership
If job requires: Python, Team Management, AWS
Output:
{{
  "technical": ["Python", "JavaScript"],
  "soft": ["Leadership"],
  "tools": ["AWS"]
}}

Return optimized skills as JSON only (NO markdown, NO explanations):
"""
        return prompt
    
    def _get_fallback_summary(self, profile: dict) -> str:
        """Fallback summary if AI fails"""
        personal_info = profile.get("personal_info", {})
        title = personal_info.get("title", "Professional")
        experience_count = len(profile.get("experience", []))
        
        return f"{title} with {experience_count}+ years of experience in delivering high-quality solutions. Proven track record of success in fast-paced environments with strong technical and interpersonal skills."
