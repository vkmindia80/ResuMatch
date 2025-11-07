"""
Enhanced ATS Scorer with Advanced Algorithms
Provides more accurate ATS scoring with semantic matching and detailed analysis
Version 2.0 - Improved keyword matching and semantic analysis
"""
import re
from typing import Dict, List, Tuple, Set
from collections import Counter

class EnhancedATSScorer:
    # Strong action verbs categorized by impact
    ACTION_VERBS = {
        'leadership': ['led', 'managed', 'directed', 'coordinated', 'supervised', 'mentored', 'guided', 'oversaw', 'spearheaded', 'orchestrated'],
        'achievement': ['achieved', 'accomplished', 'exceeded', 'surpassed', 'delivered', 'completed', 'attained', 'reached', 'realized'],
        'creation': ['created', 'developed', 'designed', 'built', 'established', 'launched', 'implemented', 'engineered', 'architected', 'pioneered'],
        'improvement': ['improved', 'enhanced', 'optimized', 'streamlined', 'increased', 'reduced', 'transformed', 'upgraded', 'modernized', 'accelerated'],
        'analysis': ['analyzed', 'evaluated', 'assessed', 'researched', 'investigated', 'identified', 'diagnosed', 'measured', 'quantified'],
        'communication': ['presented', 'communicated', 'collaborated', 'partnered', 'liaised', 'negotiated', 'influenced', 'facilitated']
    }
    
    # Comprehensive quantifier patterns
    QUANTIFIER_PATTERNS = [
        r'\d+%',  # Percentages
        r'\d+\+%',  # Percentages with plus
        r'\$\d+[\d,]*[KkMmBb]?',  # Dollar amounts
        r'\d+[KkMmBb]\+?\s*(users|customers|clients|members|employees|visitors)',  # User counts with K/M/B
        r'\d+[,\d]*\+?\s*(users|customers|clients|members|employees|teams|people|projects)',  # Large numbers
        r'\d+\s*(hour|day|week|month|year)s?',  # Time periods
        r'\d+x',  # Multipliers
        r'top\s+\d+',  # Rankings
        r'\d+[,\d]*\s*(records|transactions|requests|queries)',  # Volume metrics
        r'from\s+\d+.*to\s+\d+',  # Before/after comparisons
    ]
    
    # ATS-friendly section headers
    STANDARD_HEADERS = [
        'professional summary', 'summary', 'profile',
        'experience', 'work experience', 'professional experience', 'employment history',
        'education', 'academic background',
        'skills', 'technical skills', 'core competencies',
        'projects', 'certifications', 'achievements'
    ]
    
    # Technology synonyms and variations for better matching
    TECH_SYNONYMS = {
        'javascript': ['js', 'ecmascript', 'javascript'],
        'typescript': ['ts', 'typescript'],
        'react': ['react', 'react.js', 'reactjs'],
        'node': ['node', 'node.js', 'nodejs'],
        'python': ['python', 'py', 'python3'],
        'java': ['java', 'jdk', 'jre'],
        'aws': ['amazon web services', 'aws', 'amazon cloud'],
        'gcp': ['google cloud', 'gcp', 'google cloud platform'],
        'azure': ['microsoft azure', 'azure', 'azure cloud'],
        'kubernetes': ['k8s', 'kubernetes', 'kube'],
        'docker': ['docker', 'containerization'],
        'ci/cd': ['ci/cd', 'continuous integration', 'continuous deployment', 'jenkins', 'github actions'],
        'sql': ['sql', 'mysql', 'postgresql', 'postgres', 'database'],
        'mongodb': ['mongodb', 'mongo', 'nosql'],
        'api': ['api', 'rest api', 'restful api', 'web services'],
        'machine learning': ['ml', 'machine learning', 'ai', 'artificial intelligence'],
        'agile': ['agile', 'scrum', 'kanban', 'sprint'],
    }
    
    def calculate_ats_score(
        self,
        resume_content: dict,
        job_description: dict = None
    ) -> dict:
        """
        Calculate comprehensive ATS score with enhanced algorithms
        
        Args:
            resume_content: Resume content dictionary
            job_description: Optional job description for keyword matching
            
        Returns:
            Dictionary with overall score and detailed component scores
        """
        scores = {}
        
        # Component 1: Keyword Match (30 points) - Most critical for ATS
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
        
        # Generate detailed suggestions
        suggestions = self._generate_suggestions(scores, resume_content, job_description)
        
        # Advanced analysis
        keyword_density = self._analyze_keyword_density(resume_content, job_description)
        formatting_issues = self._check_formatting_issues(resume_content)
        
        return {
            'overall_score': min(overall, 100),
            'keyword_match': scores['keyword_match'],
            'format_compatibility': scores['format_compatibility'],
            'action_verbs_usage': scores['action_verbs'],
            'quantification_score': scores['quantification'],
            'impact_statements': scores['impact_statements'],
            'suggestions': suggestions,
            'strengths': self._identify_strengths(scores),
            'weaknesses': self._identify_weaknesses(scores),
            'keyword_density': keyword_density,
            'formatting_issues': formatting_issues,
            'grade': self._get_grade(overall)
        }
    
    def _normalize_keyword(self, keyword: str) -> Set[str]:
        """
        Normalize keyword to include synonyms and variations
        """
        keyword_lower = keyword.lower().strip()
        variations = {keyword_lower}
        
        # Check for known synonyms
        for key, synonyms in self.TECH_SYNONYMS.items():
            if keyword_lower in synonyms or keyword_lower == key:
                variations.update(synonyms)
        
        # Add common variations
        # Remove special characters for matching
        clean_keyword = re.sub(r'[^a-z0-9\s]', '', keyword_lower)
        variations.add(clean_keyword)
        
        # Add version without spaces
        variations.add(keyword_lower.replace(' ', ''))
        variations.add(keyword_lower.replace('.', ''))
        
        return variations
    
    def _score_keyword_match(self, resume: dict, job_desc: dict = None) -> int:
        """
        Enhanced keyword matching with semantic understanding and synonym support
        """
        if not job_desc:
            return 15  # Base score without job description
        
        parsed_data = job_desc.get('parsed_data', {})
        
        # Extract job keywords with priority weighting
        required_skills = parsed_data.get('required_skills', [])
        technical_skills = parsed_data.get('technical_skills', [])
        tools = parsed_data.get('tools_and_technologies', [])
        preferred_skills = parsed_data.get('preferred_skills', [])
        
        # Build weighted keyword sets
        critical_keywords = set()  # Must-have keywords (weight: 3x)
        important_keywords = set()  # Important keywords (weight: 2x)
        nice_to_have = set()  # Preferred keywords (weight: 1x)
        
        for skill in required_skills[:15]:  # Top 15 required
            critical_keywords.add(skill.lower().strip())
        
        for skill in technical_skills[:15]:  # Top 15 technical
            important_keywords.add(skill.lower().strip())
        
        for tool in tools[:10]:  # Top 10 tools
            important_keywords.add(tool.lower().strip())
        
        for skill in preferred_skills[:10]:  # Top 10 preferred
            nice_to_have.add(skill.lower().strip())
        
        all_job_keywords = critical_keywords | important_keywords | nice_to_have
        
        if not all_job_keywords:
            return 15
        
        # Extract resume text and keywords
        resume_text = self._extract_all_text(resume).lower()
        resume_keywords = self._extract_resume_keywords(resume)
        
        # Calculate matches with semantic awareness
        critical_matches = 0
        important_matches = 0
        preferred_matches = 0
        
        # Check critical keywords with variations
        for keyword in critical_keywords:
            variations = self._normalize_keyword(keyword)
            if any(var in resume_text for var in variations) or any(var in resume_keywords for var in variations):
                critical_matches += 1
        
        # Check important keywords
        for keyword in important_keywords:
            variations = self._normalize_keyword(keyword)
            if any(var in resume_text for var in variations) or any(var in resume_keywords for var in variations):
                important_matches += 1
        
        # Check preferred keywords
        for keyword in nice_to_have:
            variations = self._normalize_keyword(keyword)
            if any(var in resume_text for var in variations) or any(var in resume_keywords for var in variations):
                preferred_matches += 1
        
        # Calculate weighted score
        critical_rate = critical_matches / len(critical_keywords) if critical_keywords else 1.0
        important_rate = important_matches / len(important_keywords) if important_keywords else 1.0
        preferred_rate = preferred_matches / len(nice_to_have) if nice_to_have else 1.0
        
        # Weighted scoring (critical keywords are most important)
        weighted_score = (
            critical_rate * 15 +      # Critical: 15 points max
            important_rate * 10 +     # Important: 10 points max
            preferred_rate * 5        # Preferred: 5 points max
        )
        
        return min(30, int(weighted_score))
    
    def _extract_resume_keywords(self, resume: dict) -> Set[str]:
        """
        Extract all keywords from resume for matching
        """
        keywords = set()
        
        # From skills section
        skills = resume.get('skills', {})
        for skill in skills.get('technical', []):
            skill_name = skill if isinstance(skill, str) else skill.get('name', '')
            if skill_name:
                keywords.add(skill_name.lower().strip())
        
        for tool in skills.get('tools', []):
            keywords.add(tool.lower().strip())
        
        for soft in skills.get('soft', []):
            keywords.add(soft.lower().strip())
        
        # From experience
        for exp in resume.get('experience', []):
            for tech in exp.get('technologies', []):
                keywords.add(tech.lower().strip())
        
        # From certifications
        for cert in resume.get('certifications', []):
            name = cert.get('name', '') if isinstance(cert, dict) else cert
            keywords.add(name.lower().strip())
        
        return keywords
    
    def _score_format_compatibility(self, resume: dict) -> int:
        """
        Score format compatibility with enhanced checks
        """
        score = 0
        
        # Check for essential sections (3 points each)
        if resume.get('header'):
            score += 3
        if resume.get('summary') and len(resume.get('summary', '')) > 50:
            score += 4  # Summary is critical
        if resume.get('experience') and len(resume.get('experience', [])) > 0:
            score += 4  # Experience is critical
        if resume.get('education') and len(resume.get('education', [])) > 0:
            score += 3
        if resume.get('skills'):
            score += 3
        
        # Bonus for additional sections
        if resume.get('projects'):
            score += 1
        if resume.get('certifications'):
            score += 2  # Certifications are valuable
        
        return min(score, 20)
    
    def _score_action_verbs(self, resume: dict) -> int:
        """
        Enhanced action verb scoring
        """
        all_action_verbs = []
        for verbs in self.ACTION_VERBS.values():
            all_action_verbs.extend(verbs)
        
        action_verb_count = 0
        strong_verb_count = 0  # Verbs from leadership, creation, improvement
        total_bullets = 0
        
        strong_categories = ['leadership', 'creation', 'improvement', 'achievement']
        strong_verbs = []
        for cat in strong_categories:
            strong_verbs.extend(self.ACTION_VERBS.get(cat, []))
        
        # Check experience bullets
        for exp in resume.get('experience', []):
            responsibilities = exp.get('optimized_responsibilities', exp.get('responsibilities', []))
            for bullet in responsibilities:
                total_bullets += 1
                bullet_lower = bullet.lower().strip()
                first_word = bullet_lower.split()[0] if bullet_lower.split() else ''
                
                # Check if starts with action verb
                if first_word in all_action_verbs:
                    action_verb_count += 1
                    if first_word in strong_verbs:
                        strong_verb_count += 1
        
        if total_bullets == 0:
            return 10  # Base score
        
        # Calculate scores
        action_percentage = action_verb_count / total_bullets
        strong_percentage = strong_verb_count / total_bullets
        
        # Base score from action verb usage
        base_score = int(action_percentage * 15)
        
        # Bonus for strong verbs
        bonus = int(strong_percentage * 5)
        
        return min(20, base_score + bonus)
    
    def _score_quantification(self, resume: dict) -> int:
        """
        Enhanced quantification scoring
        """
        quantified_count = 0
        high_impact_count = 0  # Bullets with multiple metrics
        total_bullets = 0
        
        # Check experience bullets
        for exp in resume.get('experience', []):
            responsibilities = exp.get('optimized_responsibilities', exp.get('responsibilities', []))
            for bullet in responsibilities:
                total_bullets += 1
                matches = 0
                
                # Check for quantifiers
                for pattern in self.QUANTIFIER_PATTERNS:
                    if re.search(pattern, bullet, re.IGNORECASE):
                        matches += 1
                
                if matches > 0:
                    quantified_count += 1
                    if matches >= 2:  # Multiple metrics = high impact
                        high_impact_count += 1
        
        if total_bullets == 0:
            return 7  # Base score
        
        # Calculate scores
        quantified_percentage = quantified_count / total_bullets
        high_impact_percentage = high_impact_count / total_bullets
        
        # Base score
        base_score = int(quantified_percentage * 12)
        
        # Bonus for high-impact bullets
        bonus = int(high_impact_percentage * 3)
        
        return min(15, base_score + bonus)
    
    def _score_impact_statements(self, resume: dict) -> int:
        """
        Enhanced impact statement scoring
        """
        impact_keywords = [
            'improved', 'increased', 'reduced', 'saved', 'generated', 'achieved',
            'exceeded', 'delivered', 'boosted', 'enhanced', 'optimized', 'transformed',
            'accelerated', 'streamlined', 'eliminated', 'maximized', 'minimized'
        ]
        
        impact_count = 0
        strong_impact_count = 0  # Impact with quantification
        total_bullets = 0
        
        # Check experience bullets
        for exp in resume.get('experience', []):
            responsibilities = exp.get('optimized_responsibilities', exp.get('responsibilities', []))
            for bullet in responsibilities:
                total_bullets += 1
                bullet_lower = bullet.lower()
                
                # Check for impact keywords
                has_impact = False
                for keyword in impact_keywords:
                    if keyword in bullet_lower:
                        has_impact = True
                        break
                
                if has_impact:
                    impact_count += 1
                    
                    # Check if impact is quantified
                    has_number = any(re.search(pattern, bullet, re.IGNORECASE) for pattern in self.QUANTIFIER_PATTERNS)
                    if has_number:
                        strong_impact_count += 1
        
        if total_bullets == 0:
            return 7  # Base score
        
        # Calculate scores
        impact_percentage = impact_count / total_bullets
        strong_impact_percentage = strong_impact_count / total_bullets
        
        # Base score
        base_score = int(impact_percentage * 10)
        
        # Bonus for quantified impact
        bonus = int(strong_impact_percentage * 5)
        
        return min(15, base_score + bonus)
    
    def _analyze_keyword_density(self, resume: dict, job_desc: dict = None) -> dict:
        """
        Analyze keyword density to prevent stuffing
        """
        if not job_desc:
            return {'status': 'no_job_description', 'density': 'unknown'}
        
        parsed_data = job_desc.get('parsed_data', {})
        keywords = parsed_data.get('required_skills', []) + parsed_data.get('technical_skills', [])
        
        if not keywords:
            return {'status': 'no_keywords', 'density': 'unknown'}
        
        resume_text = self._extract_all_text(resume)
        word_count = len(resume_text.split())
        
        # Count keyword occurrences
        keyword_count = 0
        for keyword in keywords:
            keyword_count += resume_text.lower().count(keyword.lower())
        
        # Calculate density
        density = (keyword_count / word_count * 100) if word_count > 0 else 0
        
        # Optimal density is 2-4%
        status = 'optimal'
        if density < 1.5:
            status = 'too_low'
        elif density > 5:
            status = 'too_high'
        
        return {
            'status': status,
            'density': f"{density:.2f}%",
            'keyword_count': keyword_count,
            'total_words': word_count,
            'recommendation': self._get_density_recommendation(density)
        }
    
    def _get_density_recommendation(self, density: float) -> str:
        """Get keyword density recommendation"""
        if density < 1.5:
            return "Add more relevant keywords from job description"
        elif density > 5:
            return "Reduce keyword repetition to avoid ATS penalties"
        else:
            return "Keyword density is optimal"
    
    def _check_formatting_issues(self, resume: dict) -> List[str]:
        """
        Check for ATS-unfriendly formatting issues
        """
        issues = []
        
        # Check header/contact info
        header = resume.get('header', {})
        if not header.get('email'):
            issues.append("Missing email address")
        if not header.get('phone'):
            issues.append("Missing phone number")
        if not header.get('location'):
            issues.append("Missing location information")
        
        # Check summary length
        summary = resume.get('summary', '')
        if len(summary.split()) < 50:
            issues.append("Professional summary is too short (should be 75-120 words)")
        elif len(summary.split()) > 150:
            issues.append("Professional summary is too long (should be 75-120 words)")
        
        # Check experience bullets
        for exp in resume.get('experience', []):
            bullets = exp.get('optimized_responsibilities', exp.get('responsibilities', []))
            if len(bullets) < 3:
                issues.append(f"Too few bullets for {exp.get('title', 'position')} at {exp.get('company', 'company')} (minimum 3-4)")
            elif len(bullets) > 7:
                issues.append(f"Too many bullets for {exp.get('title', 'position')} (maximum 6-7)")
        
        # Check skills
        skills = resume.get('skills', {})
        tech_skills = skills.get('technical', [])
        if len(tech_skills) < 5:
            issues.append("Too few technical skills listed (minimum 8-12 for strong ATS match)")
        
        return issues if issues else ["No formatting issues detected"]
    
    def _extract_all_text(self, resume: dict) -> str:
        """
        Extract all text from resume for analysis
        """
        text = ""
        
        # Summary
        text += resume.get('summary', '') + " "
        
        # Experience
        for exp in resume.get('experience', []):
            text += exp.get('title', '') + " "
            text += exp.get('company', '') + " "
            for bullet in exp.get('optimized_responsibilities', exp.get('responsibilities', [])):
                text += bullet + " "
        
        # Skills
        skills = resume.get('skills', {})
        for skill in skills.get('technical', []):
            if isinstance(skill, str):
                text += skill + " "
            elif isinstance(skill, dict):
                text += skill.get('name', '') + " "
        
        return text
    
    def _generate_suggestions(self, scores: dict, resume: dict, job_desc: dict = None) -> List[str]:
        """
        Generate actionable improvement suggestions
        """
        suggestions = []
        
        # Keyword match suggestions
        if scores['keyword_match'] < 20:
            suggestions.append("🔑 CRITICAL: Increase keyword matching - add more skills/terms from the job description")
            if job_desc:
                suggestions.append("Review job requirements and integrate missing technical skills naturally throughout resume")
        elif scores['keyword_match'] < 25:
            suggestions.append("Good keyword coverage, but can be improved - review job posting for additional relevant terms")
        
        # Action verbs suggestions
        if scores['action_verbs'] < 15:
            suggestions.append("⚡ HIGH PRIORITY: Start more bullets with strong action verbs (Architected, Spearheaded, Implemented)")
        elif scores['action_verbs'] < 18:
            suggestions.append("Good action verb usage - replace remaining weak verbs with impactful alternatives")
        
        # Quantification suggestions
        if scores['quantification'] < 10:
            suggestions.append("📊 HIGH PRIORITY: Add quantifiable metrics to 80%+ of bullets (%, time, scale, $)")
        elif scores['quantification'] < 13:
            suggestions.append("Add more specific numbers to strengthen impact (e.g., 'team of 10', '500K users')")
        
        # Impact suggestions
        if scores['impact_statements'] < 10:
            suggestions.append("💡 PRIORITY: Focus on measurable outcomes - show what changed because of your work")
        elif scores['impact_statements'] < 13:
            suggestions.append("Good impact focus - quantify more of these achievements with specific metrics")
        
        # Format suggestions
        if scores['format_compatibility'] < 18:
            suggestions.append("Ensure all standard sections are present and well-populated (Summary, Experience, Skills, Education)")
        
        return suggestions if suggestions else ["✅ Excellent! Resume is well-optimized for ATS systems"]
    
    def _identify_strengths(self, scores: dict) -> List[str]:
        """
        Identify resume strengths
        """
        strengths = []
        
        if scores['keyword_match'] >= 25:
            strengths.append("Excellent keyword alignment - strong match with job requirements")
        if scores['format_compatibility'] >= 18:
            strengths.append("Well-structured format with all essential sections")
        if scores['action_verbs'] >= 17:
            strengths.append("Strong use of impactful action verbs throughout")
        if scores['quantification'] >= 12:
            strengths.append("Excellent quantification with metrics and measurable results")
        if scores['impact_statements'] >= 12:
            strengths.append("Clear demonstration of business impact and value delivery")
        
        return strengths if strengths else ["Resume has solid fundamentals to build upon"]
    
    def _identify_weaknesses(self, scores: dict) -> List[str]:
        """
        Identify areas for improvement
        """
        weaknesses = []
        
        if scores['keyword_match'] < 20:
            weaknesses.append("CRITICAL: Low keyword matching - needs better alignment with job requirements")
        if scores['format_compatibility'] < 15:
            weaknesses.append("Missing essential resume sections or insufficient content")
        if scores['action_verbs'] < 15:
            weaknesses.append("Weak action verbs - need more powerful, results-oriented language")
        if scores['quantification'] < 10:
            weaknesses.append("Insufficient quantification - add more metrics and numbers")
        if scores['impact_statements'] < 10:
            weaknesses.append("Limited impact demonstration - focus more on measurable outcomes")
        
        return weaknesses
    
    def _get_grade(self, score: int) -> str:
        """Get letter grade for score"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        else:
            return "D"
