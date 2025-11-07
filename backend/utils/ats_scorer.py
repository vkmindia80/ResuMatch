"""
ATS (Applicant Tracking System) Scoring Algorithm
Analyzes resumes for ATS compatibility and provides actionable feedback
Now uses Enhanced ATS Scorer for better accuracy
"""
import re
from typing import Dict, List, Tuple
from utils.enhanced_ats_scorer import EnhancedATSScorer

class ATSScorer(EnhancedATSScorer):
    """
    Wrapper class that extends EnhancedATSScorer
    Maintains backward compatibility while providing enhanced scoring
    """
    def __init__(self):
        super().__init__()
    # Strong action verbs for resume bullets
    ACTION_VERBS = {
        'leadership': ['led', 'managed', 'directed', 'coordinated', 'supervised', 'mentored', 'guided'],
        'achievement': ['achieved', 'accomplished', 'exceeded', 'surpassed', 'delivered', 'completed'],
        'creation': ['created', 'developed', 'designed', 'built', 'established', 'launched', 'implemented'],
        'improvement': ['improved', 'enhanced', 'optimized', 'streamlined', 'increased', 'reduced', 'transformed'],
        'analysis': ['analyzed', 'evaluated', 'assessed', 'researched', 'investigated', 'identified'],
        'communication': ['presented', 'communicated', 'collaborated', 'partnered', 'liaised', 'negotiated']
    }
    
    # Quantifiable metrics patterns
    QUANTIFIER_PATTERNS = [
        r'\d+%',  # Percentages
        r'\$\d+[KkMm]?',  # Dollar amounts
        r'\d+\+?\s*(users|customers|clients|members|employees)',  # User counts
        r'\d+\s*(hours|days|weeks|months|years)',  # Time
        r'\d+x',  # Multipliers
        r'top\s+\d+',  # Rankings
    ]
    
    def calculate_ats_score(
        self,
        resume_content: dict,
        job_description: dict = None
    ) -> dict:
        """
        Calculate comprehensive ATS score
        
        Args:
            resume_content: Resume content dictionary
            job_description: Optional job description for keyword matching
            
        Returns:
            Dictionary with overall score and component scores
        """
        scores = {}
        
        # Component 1: Keyword Match (30 points)
        scores['keyword_match'] = self._score_keyword_match(resume_content, job_description)
        
        # Component 2: Format Compatibility (20 points)
        scores['format_compatibility'] = self._score_format_compatibility(resume_content)
        
        # Component 3: Action Verbs Usage (20 points)
        scores['action_verbs'] = self._score_action_verbs(resume_content)
        
        # Component 4: Quantification (15 points)
        scores['quantification'] = self._score_quantification(resume_content)
        
        # Component 5: Impact Statements (15 points)
        scores['impact_statements'] = self._score_impact_statements(resume_content)
        
        # Calculate overall score
        overall = sum(scores.values())
        
        # Generate suggestions
        suggestions = self._generate_suggestions(scores, resume_content, job_description)
        
        return {
            'overall_score': min(overall, 100),
            'keyword_match': scores['keyword_match'],
            'format_compatibility': scores['format_compatibility'],
            'action_verbs_usage': scores['action_verbs'],
            'quantification_score': scores['quantification'],
            'impact_statements': scores['impact_statements'],
            'suggestions': suggestions,
            'strengths': self._identify_strengths(scores),
            'weaknesses': self._identify_weaknesses(scores)
        }
    
    def _score_keyword_match(self, resume: dict, job_desc: dict = None) -> int:
        """Score based on keyword matching with job description"""
        if not job_desc:
            return 15  # Base score without job description
        
        # Extract keywords from job description
        parsed_data = job_desc.get('parsed_data', {})
        job_keywords = set()
        
        for key in ['required_skills', 'technical_skills', 'tools_and_technologies', 'preferred_skills']:
            job_keywords.update([kw.lower() for kw in parsed_data.get(key, [])])
        
        if not job_keywords:
            return 15
        
        # Extract keywords from resume
        resume_keywords = set()
        
        # From skills
        skills = resume.get('skills', {})
        for skill in skills.get('technical', []):
            if isinstance(skill, dict):
                resume_keywords.add(skill.get('name', '').lower())
            else:
                resume_keywords.add(str(skill).lower())
        resume_keywords.update([tool.lower() for tool in skills.get('tools', [])])
        
        # From experience
        for exp in resume.get('experience', []):
            resume_keywords.update([tech.lower() for tech in exp.get('technologies', [])])
        
        # Calculate match percentage
        matched = job_keywords.intersection(resume_keywords)
        match_percentage = len(matched) / len(job_keywords) if job_keywords else 0
        
        # Score out of 30
        score = int(match_percentage * 30)
        return score
    
    def _score_format_compatibility(self, resume: dict) -> int:
        """Score format compatibility (simple text, proper sections)"""
        score = 0
        
        # Check for essential sections (4 points each)
        if resume.get('header'):
            score += 4
        if resume.get('summary'):
            score += 4
        if resume.get('experience'):
            score += 4
        if resume.get('education'):
            score += 4
        if resume.get('skills'):
            score += 4
        
        return min(score, 20)
    
    def _score_action_verbs(self, resume: dict) -> int:
        """Score usage of strong action verbs"""
        all_action_verbs = []
        for verbs in self.ACTION_VERBS.values():
            all_action_verbs.extend(verbs)
        
        action_verb_count = 0
        total_bullets = 0
        
        # Check experience bullets
        for exp in resume.get('experience', []):
            responsibilities = exp.get('optimized_responsibilities', exp.get('responsibilities', []))
            for bullet in responsibilities:
                total_bullets += 1
                bullet_lower = bullet.lower()
                # Check if starts with action verb
                for verb in all_action_verbs:
                    if bullet_lower.startswith(verb):
                        action_verb_count += 1
                        break
        
        if total_bullets == 0:
            return 10  # Base score
        
        # Score based on percentage
        percentage = action_verb_count / total_bullets
        score = int(percentage * 20)
        return min(score, 20)
    
    def _score_quantification(self, resume: dict) -> int:
        """Score usage of quantifiable metrics"""
        quantified_count = 0
        total_bullets = 0
        
        # Check experience bullets
        for exp in resume.get('experience', []):
            responsibilities = exp.get('optimized_responsibilities', exp.get('responsibilities', []))
            for bullet in responsibilities:
                total_bullets += 1
                # Check for quantifiers
                for pattern in self.QUANTIFIER_PATTERNS:
                    if re.search(pattern, bullet, re.IGNORECASE):
                        quantified_count += 1
                        break
        
        if total_bullets == 0:
            return 7  # Base score
        
        # Score based on percentage
        percentage = quantified_count / total_bullets
        score = int(percentage * 15)
        return min(score, 15)
    
    def _score_impact_statements(self, resume: dict) -> int:
        """Score presence of impact-focused statements"""
        impact_keywords = [
            'improved', 'increased', 'reduced', 'saved', 'generated', 'achieved',
            'exceeded', 'delivered', 'boosted', 'enhanced', 'optimized', 'transformed'
        ]
        
        impact_count = 0
        total_bullets = 0
        
        # Check experience bullets
        for exp in resume.get('experience', []):
            responsibilities = exp.get('optimized_responsibilities', exp.get('responsibilities', []))
            for bullet in responsibilities:
                total_bullets += 1
                bullet_lower = bullet.lower()
                # Check for impact keywords
                for keyword in impact_keywords:
                    if keyword in bullet_lower:
                        impact_count += 1
                        break
        
        if total_bullets == 0:
            return 7  # Base score
        
        # Score based on percentage
        percentage = impact_count / total_bullets
        score = int(percentage * 15)
        return min(score, 15)
    
    def _generate_suggestions(self, scores: dict, resume: dict, job_desc: dict = None) -> List[str]:
        """Generate actionable improvement suggestions"""
        suggestions = []
        
        # Keyword match suggestions
        if scores['keyword_match'] < 15:
            if job_desc:
                suggestions.append("Add more relevant keywords from the job description to your resume")
                suggestions.append("Ensure your skills section includes the technical requirements mentioned in the job posting")
            else:
                suggestions.append("Tailor your resume to include keywords from the target job description")
        
        # Format suggestions
        if scores['format_compatibility'] < 15:
            suggestions.append("Ensure all key sections are present: header, summary, experience, education, skills")
        
        # Action verbs suggestions
        if scores['action_verbs'] < 12:
            suggestions.append("Start more bullet points with strong action verbs (Led, Developed, Implemented, etc.)")
            suggestions.append("Replace passive voice with active, achievement-focused language")
        
        # Quantification suggestions
        if scores['quantification'] < 8:
            suggestions.append("Add quantifiable metrics to your achievements (percentages, dollar amounts, time saved)")
            suggestions.append("Include specific numbers to demonstrate impact (e.g., 'Reduced processing time by 40%')")
        
        # Impact suggestions
        if scores['impact_statements'] < 8:
            suggestions.append("Focus more on results and impact rather than just responsibilities")
            suggestions.append("Use words like 'improved', 'increased', 'reduced' to show measurable outcomes")
        
        return suggestions
    
    def _identify_strengths(self, scores: dict) -> List[str]:
        """Identify resume strengths"""
        strengths = []
        
        if scores['keyword_match'] >= 20:
            strengths.append("Strong keyword alignment with job requirements")
        if scores['format_compatibility'] >= 16:
            strengths.append("Well-structured format with all essential sections")
        if scores['action_verbs'] >= 15:
            strengths.append("Excellent use of strong action verbs")
        if scores['quantification'] >= 10:
            strengths.append("Good use of quantifiable metrics")
        if scores['impact_statements'] >= 10:
            strengths.append("Impact-focused achievements highlighted")
        
        return strengths if strengths else ["Resume has a solid foundation to build upon"]
    
    def _identify_weaknesses(self, scores: dict) -> List[str]:
        """Identify areas for improvement"""
        weaknesses = []
        
        if scores['keyword_match'] < 15:
            weaknesses.append("Limited keyword matching - needs better alignment with job requirements")
        if scores['format_compatibility'] < 12:
            weaknesses.append("Missing some essential resume sections")
        if scores['action_verbs'] < 12:
            weaknesses.append("Needs more strong action verbs to start bullet points")
        if scores['quantification'] < 8:
            weaknesses.append("Limited use of quantifiable metrics and numbers")
        if scores['impact_statements'] < 8:
            weaknesses.append("Could better emphasize results and impact")
        
        return weaknesses if weaknesses else []
