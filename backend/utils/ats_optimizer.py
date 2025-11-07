"""
Advanced ATS Optimizer v2.0
Iteratively optimizes resume content until achieving 98%+ ATS score
Enhanced with smarter iteration logic and better job targeting
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
        self.target_score = 96  # Increased from 95 to 96
        self.max_iterations = 5  # Increased from 3 to 5
        self.min_improvement_threshold = 1  # Minimum improvement to continue
    
    async def optimize_resume_iteratively(
        self,
        initial_content: dict,
        ats_score: dict,
        job_description: Optional[dict] = None,
        min_target_score: Optional[int] = None
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
        
        print(f"\n🚀 Starting ATS Optimization v2.0")
        print(f"Initial score: {ats_score.get('overall_score', 0)}%")
        print(f"Target score: {self.target_score}%")
        print(f"Max iterations: {self.max_iterations}\n")
        
        while iteration < self.max_iterations:
            iteration += 1
            overall_score = current_score.get('overall_score', 0)
            
            # Check if we've reached target
            if overall_score >= self.target_score:
                print(f"✅ Target score achieved: {overall_score}% (iteration {iteration})")
                return current_content, current_score, iteration
            
            print(f"\n🔄 Iteration {iteration}/{self.max_iterations}")
            print(f"   Current: {overall_score}% | Gap to target: {self.target_score - overall_score}%")
            
            # Analyze and optimize weak areas
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
            improvement = new_overall - overall_score
            
            if improvement > 0:
                print(f"   ✅ Improvement: {overall_score}% → {new_overall}% (+{improvement}%)")
                current_content = optimized_content
                current_score = new_score
                
                # If we've exceeded target, we're done!
                if new_overall >= self.target_score:
                    print(f"\n🎉 Perfect! Target exceeded: {new_overall}%")
                    return current_content, current_score, iteration
            else:
                print(f"   ⚠️ No improvement in iteration {iteration}")
                # If no improvement and we're close to target, try one aggressive optimization
                if iteration < self.max_iterations and overall_score >= 90:
                    print(f"   🔥 Attempting aggressive optimization...")
                    continue
                else:
                    print(f"   🛑 Stopping optimization (no improvement)")
                    break
        
        final_score = current_score.get('overall_score', 0)
        print(f"\n🏁 Optimization complete: {final_score}% after {iteration} iterations")
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
        
        # Identify weak areas (score < 85% of max)
        weak_areas = []
        
        keyword_score = score_breakdown.get('keyword_match', 0)
        action_verbs_score = score_breakdown.get('action_verbs_usage', 0)
        quantification_score = score_breakdown.get('quantification_score', 0)
        impact_score = score_breakdown.get('impact_statements', 0)
        
        print(f"   Analyzing scores: Keywords={keyword_score}/30, Actions={action_verbs_score}/20, Quant={quantification_score}/15, Impact={impact_score}/15")
        
        # Determine optimization priorities (more aggressive thresholds)
        if keyword_score < 26:  # Less than 87% of 30
            weak_areas.append('keywords')
        if action_verbs_score < 17:  # Less than 85% of 20
            weak_areas.append('action_verbs')
        if quantification_score < 13:  # Less than 87% of 15
            weak_areas.append('quantification')
        if impact_score < 13:  # Less than 87% of 15
            weak_areas.append('impact')
        
        print(f"   Focus areas: {', '.join(weak_areas) if weak_areas else 'General refinement'}")
        
        # Priority 1: Keyword matching (most critical)
        if job_description and 'keywords' in weak_areas:
            print(f"   🔑 Optimizing keywords...")
            optimized = await self._optimize_keywords(
                optimized,
                job_description,
                score_breakdown,
                aggressive=(iteration > 2)
            )
        
        # Priority 2: Experience section (covers multiple areas)
        if any(area in weak_areas for area in ['action_verbs', 'quantification', 'impact']):
            print(f"   💼 Optimizing experience bullets...")
            optimized['experience'] = await self._optimize_experience_section(
                optimized.get('experience', []),
                job_description,
                weak_areas,
                iteration
            )
        
        # Priority 3: Summary optimization
        if keyword_score < 24 or iteration > 2:
            print(f"   ✨ Optimizing professional summary...")
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
        score_breakdown: dict,
        aggressive: bool = False
    ) -> dict:
        """
        Optimize keyword placement and density throughout resume
        Enhanced with semantic matching and strategic placement
        """
        try:
            parsed_data = job_description.get('parsed_data', {})
            required_skills = parsed_data.get('required_skills', [])[:20]  # Increased from 15
            technical_skills = parsed_data.get('technical_skills', [])[:20]  # Increased from 15
            tools = parsed_data.get('tools_and_technologies', [])[:15]  # Increased from 10
            preferred_skills = parsed_data.get('preferred_skills', [])[:10]
            
            # Analyze current coverage
            current_skills = content.get('skills', {})
            current_tech = set()
            for skill in current_skills.get('technical', []):
                if isinstance(skill, str):
                    current_tech.add(skill.lower())
            
            # Find missing critical keywords
            missing_critical = []
            missing_important = []
            
            for keyword in required_skills:
                if keyword.lower() not in current_tech:
                    missing_critical.append(keyword)
            
            for keyword in technical_skills:
                if keyword.lower() not in current_tech:
                    missing_important.append(keyword)
            
            # Strategic keyword addition
            if (missing_critical or missing_important) and current_skills:
                technical_list = current_skills.get('technical', [])
                tools_list = current_skills.get('tools', [])
                
                # Add critical missing keywords (high priority)
                added = 0
                for keyword in missing_critical[:8]:  # Add up to 8 critical
                    if keyword not in [str(s) for s in technical_list]:
                        technical_list.append(keyword)
                        added += 1
                
                # Add important keywords
                for keyword in missing_important[:5]:  # Add up to 5 important
                    if keyword not in [str(s) for s in technical_list]:
                        technical_list.append(keyword)
                        added += 1
                
                # Add tools
                for tool in tools[:6]:
                    if tool.lower() not in [str(t).lower() for t in tools_list]:
                        if tool not in [str(s) for s in technical_list]:
                            tools_list.append(tool)
                            added += 1
                
                print(f"      Added {added} critical keywords to skills section")
                
                current_skills['technical'] = technical_list
                current_skills['tools'] = tools_list
                content['skills'] = current_skills
            
            return content
        except Exception as e:
            print(f"      Error optimizing keywords: {e}")
            return content
    
    async def _optimize_experience_section(
        self,
        experience: list,
        job_description: Optional[dict],
        weak_areas: list,
        iteration: int
    ) -> list:
        """
        Optimize experience bullets for action verbs, quantification, and impact
        Enhanced with more aggressive optimization in later iterations
        """
        try:
            optimized_experience = []
            
            for idx, exp in enumerate(experience):
                bullets = exp.get('optimized_responsibilities') or exp.get('responsibilities', [])
                if not bullets:
                    optimized_experience.append(exp)
                    continue
                
                # Build focused optimization prompt
                focus_areas = []
                if 'action_verbs' in weak_areas:
                    focus_areas.append('POWERFUL action verbs (Architected, Spearheaded, Transformed)')
                if 'quantification' in weak_areas:
                    focus_areas.append('SPECIFIC metrics and numbers (%, $, scale, time)')
                if 'impact' in weak_areas:
                    focus_areas.append('MEASURABLE business impact and results')
                
                # Extract critical keywords from job
                critical_keywords = []
                if job_description:
                    parsed_data = job_description.get('parsed_data', {})
                    critical_keywords = parsed_data.get('required_skills', [])[:12] + parsed_data.get('technical_skills', [])[:12]
                
                prompt = f"""
OPTIMIZE THESE RESUME BULLETS FOR PERFECT ATS SCORE (98%+).

**Position:** {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}

**Current Bullets:**
"""
                for i, bullet in enumerate(bullets, 1):
                    prompt += f"{i}. {bullet}\n"
                
                if critical_keywords:
                    prompt += f"\n**MUST INCLUDE THESE KEYWORDS:** {', '.join(critical_keywords[:20])}\n"
                
                prompt += f"""

**CRITICAL FOCUS ({iteration} of 5 iterations):** {', '.join(focus_areas) if focus_areas else 'Perfect ATS optimization'}

**ATS PERFECTION FORMULA:**
EVERY bullet MUST follow: [POWER VERB] + [Specific Action] + [Technology/Method] + [QUANTIFIED Result]

**MANDATORY REQUIREMENTS:**
1. ⚡ ACTION VERBS: Start EVERY bullet with: Architected, Spearheaded, Engineered, Transformed, Delivered, Optimized, Led, Implemented
2. 📊 QUANTIFICATION: Include 2+ metrics per bullet (%, numbers, $, time, scale)
3. 🎯 KEYWORDS: Naturally integrate {len(critical_keywords)} critical keywords across bullets
4. 💥 IMPACT: Show before/after, improvement %, business value
5. 🛠️ TECHNICAL: Include specific tools/technologies used
6. 💯 RESULTS-FOCUSED: Every bullet shows measurable achievement

**PERFECT BULLET EXAMPLES:**
• Architected cloud-native microservices platform using React, Node.js, and AWS ECS, reducing API latency by 72% and supporting 2M+ daily active users with 99.99% uptime
• Spearheaded agile transformation for 15-person engineering team, implementing CI/CD pipeline with Jenkins and Docker that cut deployment time from 4 hours to 8 minutes and eliminated 94% of production bugs
• Engineered real-time analytics dashboard processing 500K+ transactions daily using Python and PostgreSQL, increasing business insights delivery by 85% and enabling $2M+ in data-driven revenue growth

Return 4-6 PERFECT bullets (one per line, NO numbering/symbols, start with action verb):
"""
                
                system_message = "You are an elite ATS optimization expert. Create resume bullets that achieve 98-100% ATS scores through perfect keyword integration, quantification, and impact demonstration."
                
                client = LlmChat(
                    api_key=self.api_key,
                    session_id=f"ats_v2_exp_{hash(str(exp.get('company', '')))}_{iteration}",
                    system_message=system_message
                ).with_model("openai", "gpt-4o-mini").with_params(temperature=0.85, max_tokens=700)
                
                user_msg = UserMessage(text=prompt)
                response = await client.send_message(user_msg)
                content_text = response.strip()
                
                # Parse optimized bullets
                optimized_bullets = [
                    line.strip().lstrip('•').lstrip('-').lstrip('*').strip()
                    for line in content_text.split('\n')
                    if line.strip() and not line.strip().startswith('#') and len(line.strip()) > 30
                ]
                
                exp_copy = exp.copy()
                exp_copy['optimized_responsibilities'] = optimized_bullets[:6]  # Max 6 bullets
                optimized_experience.append(exp_copy)
            
            return optimized_experience
        except Exception as e:
            print(f"      Error optimizing experience: {e}")
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
        Enhanced with better keyword integration
        """
        try:
            suggestions = score_breakdown.get('suggestions', [])
            
            prompt = f"""
OPTIMIZE THIS PROFESSIONAL SUMMARY FOR PERFECT ATS SCORE (98%+).

**Current Summary:**
{current_summary}

**ATS Issues to Fix:**
"""
            for suggestion in suggestions:
                prompt += f"• {suggestion}\n"
            
            if job_description:
                parsed_data = job_description.get('parsed_data', {})
                required_skills = parsed_data.get('required_skills', [])[:15]
                technical_skills = parsed_data.get('technical_skills', [])[:15]
                
                prompt += f"""

**TARGET JOB - MUST OPTIMIZE FOR:**
• Position: {job_description.get('title', 'N/A')}
• Company: {job_description.get('company', 'N/A')}
• CRITICAL Required Skills: {', '.join(required_skills)}
• CRITICAL Technical Skills: {', '.join(technical_skills)}
• Level: {parsed_data.get('job_level', 'N/A')}
"""
            
            # Extract top achievements
            achievements = []
            for exp in full_content.get('experience', [])[:2]:
                for bullet in exp.get('optimized_responsibilities', exp.get('responsibilities', []))[:2]:
                    if any(metric in bullet for metric in ['%', '$', 'increased', 'reduced', 'improved', 'led']):
                        achievements.append(bullet[:100])
            
            prompt += f"""

**Key Quantifiable Achievements:**
{chr(10).join(f'• {a}' for a in achievements[:3])}

**ATS PERFECTION REQUIREMENTS:**
1. 📌 LENGTH: Exactly 3-4 powerful sentences (95-125 words)
2. 🔑 KEYWORDS: Include 12-15 EXACT keywords from required/technical skills
3. 📊 METRICS: Include 2-3 quantifiable achievements with specific numbers
4. ⚡ IMPACT: Lead with experience level + strong value proposition
5. 🎯 MATCH: Use EXACT terminology from job posting (not synonyms)
6. 💼 TECHNICAL: List 8-10 relevant technologies naturally
7. 💎 POWERFUL: Strong, confident, results-focused language
8. 💯 ATS-OPTIMIZED: Third person, industry terms, no fluff

**PERFECT SUMMARY FORMULA:**
[Experience Level + Title] with [X]+ years in [domain] → [Top 5-6 CRITICAL keywords] → [Quantified achievement with %/$] → [Additional technical skills + tools] → [Certifications/specializations]

**EXAMPLE OF 98%+ ATS SCORE SUMMARY:**
"Senior Full-Stack Engineer with 8+ years of experience building scalable web applications using React, Node.js, Python, and AWS cloud infrastructure. Proven expertise in microservices architecture, CI/CD automation, and agile development methodologies, delivering projects that reduced system latency by 68% and increased user engagement by 45%. Skilled in Docker, Kubernetes, PostgreSQL, MongoDB, Redis, and GraphQL with hands-on experience leading cross-functional teams of 12+ engineers. AWS Certified Solutions Architect specializing in serverless computing, infrastructure-as-code, and DevOps best practices."

Write the PERFECT summary now (3-4 sentences, 95-125 words, keyword-packed, ATS-optimized):
"""
            
            system_message = "You are an elite ATS optimization expert specializing in professional summaries that achieve 98-100% ATS scores through strategic keyword integration and powerful impact statements."
            
            client = LlmChat(
                api_key=self.api_key,
                session_id=f"ats_v2_summary_{hash(current_summary)}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini").with_params(temperature=0.75, max_tokens=400)
            
            user_msg = UserMessage(text=prompt)
            response = await client.send_message(user_msg)
            optimized_summary = response.strip()
            
            # Clean up
            if '```' in optimized_summary:
                optimized_summary = optimized_summary.split('```')[0].strip()
            
            # Remove any leading/trailing quotes
            optimized_summary = optimized_summary.strip('"').strip("'")
            
            return optimized_summary
        except Exception as e:
            print(f"      Error optimizing summary: {e}")
            return current_summary
