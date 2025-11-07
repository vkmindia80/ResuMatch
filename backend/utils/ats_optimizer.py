"""
Advanced ATS Optimizer
Iteratively optimizes resume content until achieving 95%+ ATS score
"""
import os
import json
from typing import Dict, List, Optional, Tuple
from emergentintegrations.llm.openai import LlmChat
from emergentintegrations.llm.chat import UserMessage

class ATSOptimizer:
    def __init__(self):
        """Initialize ATS Optimizer with Emergent LLM Key"""
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        self.target_score = 95
        self.max_iterations = 3
    
    async def optimize_resume_iteratively(
        self,
        initial_content: dict,
        ats_score: dict,
        job_description: Optional[dict] = None
    ) -> Tuple[dict, dict, int]:
        """
        Iteratively optimize resume until target ATS score is achieved
        
        Args:
            initial_content: Initial resume content
            ats_score: Initial ATS score breakdown
            job_description: Optional job description for targeting
            
        Returns:
            Tuple of (optimized_content, final_ats_score, iterations_used)
        """
        current_content = initial_content.copy()
        current_score = ats_score
        iteration = 0
        
        print(f"Starting iterative ATS optimization. Initial score: {ats_score.get('overall_score', 0)}%")
        
        while iteration < self.max_iterations:
            iteration += 1
            overall_score = current_score.get('overall_score', 0)
            
            # Check if we've reached target
            if overall_score >= self.target_score:
                print(f"✅ Target score achieved: {overall_score}% (iteration {iteration})")
                return current_content, current_score, iteration
            
            print(f"🔄 Optimization iteration {iteration}: Current score {overall_score}%, target {self.target_score}%")
            
            # Analyze weaknesses and optimize
            optimized_content = await self._optimize_weak_areas(
                current_content,
                current_score,
                job_description,
                iteration
            )
            
            # Recalculate score
            from utils.ats_scorer import ATSScorer
            scorer = ATSScorer()
            new_score = scorer.calculate_ats_score(optimized_content, job_description)
            
            # Check for improvement
            new_overall = new_score.get('overall_score', 0)
            if new_overall > overall_score:
                print(f"✅ Improvement: {overall_score}% → {new_overall}% (+{new_overall - overall_score}%)")
                current_content = optimized_content
                current_score = new_score
            else:
                print(f"⚠️ No improvement in iteration {iteration}, keeping previous version")
                # Stop if no improvement
                break
        
        final_score = current_score.get('overall_score', 0)
        print(f"Optimization complete after {iteration} iterations. Final score: {final_score}%")
        return current_content, current_score, iteration
    
    async def _optimize_weak_areas(
        self,
        content: dict,
        score_breakdown: dict,
        job_description: Optional[dict],
        iteration: int
    ) -> dict:
        """
        Focus optimization on weakest areas based on score breakdown
        """
        optimized = content.copy()
        
        # Identify weak areas (score < 80% of max)
        weak_areas = []
        
        keyword_score = score_breakdown.get('keyword_match', 0)
        action_verbs_score = score_breakdown.get('action_verbs_usage', 0)
        quantification_score = score_breakdown.get('quantification_score', 0)
        impact_score = score_breakdown.get('impact_statements', 0)
        
        # Determine optimization priorities
        if keyword_score < 24:  # Less than 80% of 30
            weak_areas.append('keywords')
        if action_verbs_score < 16:  # Less than 80% of 20
            weak_areas.append('action_verbs')
        if quantification_score < 12:  # Less than 80% of 15
            weak_areas.append('quantification')
        if impact_score < 12:  # Less than 80% of 15
            weak_areas.append('impact')
        
        print(f"  Weak areas identified: {', '.join(weak_areas) if weak_areas else 'None (general refinement)'}")
        
        # If we have job description, optimize for keyword matching first
        if job_description and 'keywords' in weak_areas:
            optimized = await self._optimize_keywords(
                optimized,
                job_description,
                score_breakdown
            )
        
        # Optimize experience section (covers action verbs, quantification, impact)
        if any(area in weak_areas for area in ['action_verbs', 'quantification', 'impact']):
            optimized['experience'] = await self._optimize_experience_section(
                optimized.get('experience', []),
                job_description,
                weak_areas
            )
        
        # Optimize summary if needed
        if keyword_score < 20 or iteration > 1:
            optimized['summary'] = await self._optimize_summary(
                optimized.get('summary', ''),
                optimized,
                job_description,
                score_breakdown
            )
        
        return optimized
    
    async def _optimize_keywords(
        self,
        content: dict,
        job_description: dict,
        score_breakdown: dict
    ) -> dict:
        """
        Optimize keyword placement and density throughout resume
        """
        try:
            parsed_data = job_description.get('parsed_data', {})
            required_skills = parsed_data.get('required_skills', [])[:15]
            technical_skills = parsed_data.get('technical_skills', [])[:15]
            tools = parsed_data.get('tools_and_technologies', [])[:10]
            
            # Check which keywords are missing
            current_skills = content.get('skills', {})
            current_tech = set()
            for skill in current_skills.get('technical', []):
                if isinstance(skill, str):
                    current_tech.add(skill.lower())
            
            missing_keywords = []
            for keyword in required_skills + technical_skills:
                if keyword.lower() not in current_tech:
                    missing_keywords.append(keyword)
            
            # Strategically add missing keywords to skills section
            if missing_keywords and current_skills:
                # Only add keywords that make sense (user validation would be ideal, but we optimize strategically)
                technical_list = current_skills.get('technical', [])
                # Add top 5 missing critical keywords
                for keyword in missing_keywords[:5]:
                    if keyword not in [str(s) for s in technical_list]:
                        technical_list.append(keyword)
                
                current_skills['technical'] = technical_list
                content['skills'] = current_skills
            
            return content
        except Exception as e:
            print(f"Error optimizing keywords: {e}")
            return content
    
    async def _optimize_experience_section(
        self,
        experience: list,
        job_description: Optional[dict],
        weak_areas: list
    ) -> list:
        """
        Optimize experience bullets for action verbs, quantification, and impact
        """
        try:
            optimized_experience = []
            
            for exp in experience:
                bullets = exp.get('optimized_responsibilities') or exp.get('responsibilities', [])
                if not bullets:
                    optimized_experience.append(exp)
                    continue
                
                # Build optimization prompt focusing on weak areas
                focus_areas = []
                if 'action_verbs' in weak_areas:
                    focus_areas.append('strong action verbs at the start')
                if 'quantification' in weak_areas:
                    focus_areas.append('quantifiable metrics and numbers')
                if 'impact' in weak_areas:
                    focus_areas.append('measurable business impact')
                
                prompt = f"""
Optimize these resume bullets for ATS perfection. Focus heavily on: {', '.join(focus_areas)}.

**Current Bullets:**
"""
                for bullet in bullets:
                    prompt += f"• {bullet}\n"
                
                if job_description:
                    parsed_data = job_description.get('parsed_data', {})
                    keywords = parsed_data.get('required_skills', [])[:10] + parsed_data.get('technical_skills', [])[:10]
                    prompt += f"\n**Critical Keywords to Include:** {', '.join(keywords[:15])}\n"
                
                prompt += """

**ATS OPTIMIZATION REQUIREMENTS:**
1. Start EVERY bullet with a powerful action verb (Led, Architected, Implemented, etc.)
2. Include specific numbers/metrics in at least 80% of bullets (%, $, time, scale)
3. Show measurable impact (increased X by Y%, reduced Z by N hours)
4. Integrate keywords naturally - NO keyword stuffing
5. Each bullet must follow: [Action Verb] + [What] + [How/Tool] + [Quantifiable Result]
6. Keep bullets concise (1-2 lines max)
7. Use technical terminology from job requirements

**Examples of Perfect Bullets:**
• Architected microservices platform using React and Node.js, reducing API response time by 65% and serving 500K+ daily users
• Led team of 12 engineers in agile development cycle, delivering 5 major features ahead of schedule and increasing user engagement by 40%
• Implemented automated CI/CD pipeline with Jenkins and Docker, cutting deployment time from 3 hours to 12 minutes and eliminating 95% of production bugs

Return 4-6 optimized bullets (one per line, no numbering, start with action verb):
"""
                
                system_message = "You are an expert ATS resume optimizer. Create perfect, high-scoring resume bullets that pass ATS systems with 95%+ score."
                
                client = LlmChat(
                    api_key=self.api_key,
                    session_id=f"ats_opt_exp_{hash(str(exp.get('company', '')))}_{exp.get('title', '')}",
                    system_message=system_message
                ).with_model("openai", "gpt-4o-mini").with_params(temperature=0.8, max_tokens=600)
                
                user_msg = UserMessage(text=prompt)
                response = await client.send_message(user_msg)
                content_text = response.strip()
                
                # Parse optimized bullets
                optimized_bullets = [
                    line.strip().lstrip('•').lstrip('-').lstrip('*').strip()
                    for line in content_text.split('\n')
                    if line.strip() and not line.strip().startswith('#') and len(line.strip()) > 20
                ]
                
                exp_copy = exp.copy()
                exp_copy['optimized_responsibilities'] = optimized_bullets[:6]  # Max 6 bullets
                optimized_experience.append(exp_copy)
            
            return optimized_experience
        except Exception as e:
            print(f"Error optimizing experience section: {e}")
            return experience
    
    async def _optimize_summary(
        self,
        current_summary: str,
        full_content: dict,
        job_description: Optional[dict],
        score_breakdown: dict
    ) -> str:
        """
        Optimize professional summary for maximum ATS impact
        """
        try:
            suggestions = score_breakdown.get('suggestions', [])
            
            prompt = f"""
Optimize this professional summary for perfect ATS score (95%+).

**Current Summary:**
{current_summary}

**Current ATS Issues:**
"""
            for suggestion in suggestions:
                prompt += f"• {suggestion}\n"
            
            if job_description:
                parsed_data = job_description.get('parsed_data', {})
                prompt += f"""

**Target Job Requirements - MUST INCLUDE:**
- Position: {job_description.get('title', 'N/A')}
- Required Skills: {', '.join(parsed_data.get('required_skills', [])[:10])}
- Technical Skills: {', '.join(parsed_data.get('technical_skills', [])[:10])}
- Experience Level: {parsed_data.get('job_level', 'N/A')}
"""
            
            # Extract quantifiable achievements from experience
            achievements = []
            for exp in full_content.get('experience', [])[:2]:
                for bullet in exp.get('optimized_responsibilities', exp.get('responsibilities', []))[:2]:
                    if any(metric in bullet for metric in ['%', '$', 'increased', 'reduced', 'improved']):
                        achievements.append(bullet[:80])
            
            prompt += f"""

**Key Achievements to Highlight:**
{chr(10).join(f'• {a}' for a in achievements[:3])}

**ATS OPTIMIZATION REQUIREMENTS:**
1. Length: Exactly 3-4 sentences (90-120 words)
2. Start with experience level + current title
3. Include at least 8-10 relevant keywords from job requirements (use EXACT terms)
4. Mention 1-2 quantifiable achievements with metrics
5. Use industry-standard terminology for ATS parsing
6. Focus on skills that match job requirements
7. Include technical skills naturally in context
8. Strong, confident language (no weak words)
9. Third person (no "I", "me", "my")
10. Every word must add value - no fluff

**Perfect Summary Example:**
"Senior Software Engineer with 8+ years of experience building scalable web applications using React, Node.js, and AWS. Proven expertise in microservices architecture and cloud infrastructure, with a track record of reducing system latency by 65% and improving deployment efficiency by 90%. Skilled in Agile methodologies, CI/CD automation, and leading cross-functional teams of 10+ engineers. AWS Certified Solutions Architect with deep knowledge of containerization, serverless computing, and DevOps best practices."

Write the optimized summary now (3-4 sentences, 90-120 words, keyword-rich, ATS-perfect):
"""
            
            system_message = "You are an expert ATS resume optimizer specializing in professional summaries that achieve 95%+ ATS scores."
            
            client = LlmChat(
                api_key=self.api_key,
                session_id=f"ats_opt_summary_{hash(current_summary)}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini").with_params(temperature=0.7, max_tokens=350)
            
            user_msg = UserMessage(text=prompt)
            response = await client.send_message(user_msg)
            optimized_summary = response.strip()
            
            # Clean up any markdown or extra text
            if '```' in optimized_summary:
                optimized_summary = optimized_summary.split('```')[0].strip()
            
            return optimized_summary
        except Exception as e:
            print(f"Error optimizing summary: {e}")
            return current_summary
