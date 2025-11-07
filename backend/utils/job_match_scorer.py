"""
Job Match Scorer
Calculates compatibility score between user profile and job description
"""
from typing import Dict, List, Set
import re


class JobMatchScorer:
    def __init__(self):
        """Initialize Job Match Scorer"""
        pass
    
    def calculate_match_score(
        self,
        profile: dict,
        job_description: dict
    ) -> dict:
        """
        Calculate comprehensive match score between profile and job
        
        Args:
            profile: User profile data
            job_description: Job description data
            
        Returns:
            Dictionary with match score, breakdown, and recommendations
        """
        try:
            # Get parsed job data
            parsed_data = job_description.get("parsed_data", {})
            
            # Calculate component scores
            skills_score, skills_breakdown = self._calculate_skills_match(
                profile.get("skills", {}),
                parsed_data
            )
            
            experience_score, experience_breakdown = self._calculate_experience_match(
                profile.get("experience", []),
                parsed_data
            )
            
            education_score, education_breakdown = self._calculate_education_match(
                profile.get("education", []),
                parsed_data
            )
            
            keyword_score, keyword_breakdown = self._calculate_keyword_match(
                profile,
                job_description
            )
            
            # Calculate weighted overall score
            # Skills: 40%, Experience: 30%, Keywords: 20%, Education: 10%
            overall_score = int(
                (skills_score * 0.40) +
                (experience_score * 0.30) +
                (keyword_score * 0.20) +
                (education_score * 0.10)
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                overall_score,
                skills_breakdown,
                experience_breakdown,
                education_breakdown
            )
            
            # Calculate skills gap
            skills_gap = self._calculate_skills_gap(
                profile.get("skills", {}),
                parsed_data
            )
            
            return {
                "overall_score": overall_score,
                "match_level": self._get_match_level(overall_score),
                "breakdown": {
                    "skills": {
                        "score": skills_score,
                        "details": skills_breakdown
                    },
                    "experience": {
                        "score": experience_score,
                        "details": experience_breakdown
                    },
                    "education": {
                        "score": education_score,
                        "details": education_breakdown
                    },
                    "keywords": {
                        "score": keyword_score,
                        "details": keyword_breakdown
                    }
                },
                "skills_gap": skills_gap,
                "recommendations": recommendations,
                "confidence": "high" if overall_score >= 70 else "medium" if overall_score >= 50 else "low"
            }
            
        except Exception as e:
            print(f"Error calculating match score: {e}")
            return self._get_fallback_score()
    
    def _calculate_skills_match(
        self,
        profile_skills: dict,
        parsed_data: dict
    ) -> tuple:
        """Calculate skills match score"""
        try:
            # Extract profile skills
            profile_tech_skills = set()
            for skill in profile_skills.get("technical", []):
                if isinstance(skill, dict):
                    profile_tech_skills.add(skill.get("name", "").lower())
                else:
                    profile_tech_skills.add(str(skill).lower())
            
            profile_soft_skills = set(s.lower() for s in profile_skills.get("soft", []))
            profile_tools = set(t.lower() for t in profile_skills.get("tools", []))
            
            all_profile_skills = profile_tech_skills | profile_soft_skills | profile_tools
            
            # Extract required skills from job
            required_skills = set(s.lower() for s in parsed_data.get("required_skills", []))
            preferred_skills = set(s.lower() for s in parsed_data.get("preferred_skills", []))
            
            # Calculate matches
            required_matches = all_profile_skills & required_skills
            preferred_matches = all_profile_skills & preferred_skills
            
            # Calculate score
            required_count = len(required_skills)
            preferred_count = len(preferred_skills)
            
            if required_count == 0:
                score = 50  # Default if no requirements specified
            else:
                required_match_rate = len(required_matches) / required_count
                preferred_match_rate = len(preferred_matches) / preferred_count if preferred_count > 0 else 0
                
                # Weighted: 80% required, 20% preferred
                score = int((required_match_rate * 0.8 + preferred_match_rate * 0.2) * 100)
            
            breakdown = {
                "required_skills_matched": len(required_matches),
                "required_skills_total": required_count,
                "preferred_skills_matched": len(preferred_matches),
                "preferred_skills_total": preferred_count,
                "matched_skills": list(required_matches | preferred_matches),
                "missing_required": list(required_skills - all_profile_skills),
                "missing_preferred": list(preferred_skills - all_profile_skills)
            }
            
            return score, breakdown
            
        except Exception as e:
            print(f"Error calculating skills match: {e}")
            return 50, {"error": str(e)}
    
    def _calculate_experience_match(
        self,
        profile_experience: list,
        parsed_data: dict
    ) -> tuple:
        """Calculate experience match score"""
        try:
            # Calculate total years of experience
            total_years = len(profile_experience)
            
            # Get required experience
            required_years = parsed_data.get("required_experience_years", 0)
            job_level = parsed_data.get("job_level", "mid").lower()
            
            # If no specific years mentioned, estimate from job level
            if required_years == 0:
                if job_level in ["entry", "junior"]:
                    required_years = 1
                elif job_level in ["mid", "intermediate"]:
                    required_years = 3
                elif job_level in ["senior", "lead"]:
                    required_years = 5
                elif job_level in ["principal", "staff", "architect"]:
                    required_years = 8
            
            # Calculate score based on experience match
            if total_years >= required_years:
                score = min(100, 70 + (total_years - required_years) * 5)
            else:
                score = int((total_years / required_years) * 70)
            
            # Check for relevant experience (title/company match)
            job_title = parsed_data.get("title", "").lower()
            relevant_exp_count = 0
            
            for exp in profile_experience:
                exp_title = exp.get("title", "").lower()
                if any(word in exp_title for word in job_title.split()):
                    relevant_exp_count += 1
            
            # Boost score for relevant experience
            if relevant_exp_count > 0:
                score = min(100, score + (relevant_exp_count * 5))
            
            breakdown = {
                "total_years": total_years,
                "required_years": required_years,
                "meets_requirement": total_years >= required_years,
                "relevant_positions": relevant_exp_count,
                "job_level": job_level
            }
            
            return score, breakdown
            
        except Exception as e:
            print(f"Error calculating experience match: {e}")
            return 50, {"error": str(e)}
    
    def _calculate_education_match(
        self,
        profile_education: list,
        parsed_data: dict
    ) -> tuple:
        """Calculate education match score"""
        try:
            if not profile_education:
                return 50, {"message": "No education information provided"}
            
            # Get highest degree
            degree_levels = {
                "phd": 5, "doctorate": 5,
                "master": 4, "mba": 4, "ms": 4, "ma": 4,
                "bachelor": 3, "bs": 3, "ba": 3,
                "associate": 2,
                "diploma": 1, "certificate": 1
            }
            
            highest_level = 0
            for edu in profile_education:
                degree = edu.get("degree", "").lower()
                for key, level in degree_levels.items():
                    if key in degree:
                        highest_level = max(highest_level, level)
            
            # Most jobs are satisfied with bachelor's (level 3)
            if highest_level >= 3:
                score = 100
            elif highest_level >= 2:
                score = 80
            elif highest_level >= 1:
                score = 60
            else:
                score = 40
            
            breakdown = {
                "highest_degree_level": highest_level,
                "education_count": len(profile_education),
                "degrees": [edu.get("degree", "") for edu in profile_education]
            }
            
            return score, breakdown
            
        except Exception as e:
            print(f"Error calculating education match: {e}")
            return 50, {"error": str(e)}
    
    def _calculate_keyword_match(
        self,
        profile: dict,
        job_description: dict
    ) -> tuple:
        """Calculate keyword match score"""
        try:
            # Extract all text from job description
            job_text = job_description.get("original_text", "").lower()
            if not job_text:
                return 50, {"message": "No job text available"}
            
            # Extract keywords from job
            job_keywords = set(re.findall(r'\b[a-z]+\b', job_text))
            
            # Remove common words
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can'}
            job_keywords = job_keywords - stopwords
            
            # Extract all text from profile
            profile_text = ""
            
            # Add experience text
            for exp in profile.get("experience", []):
                profile_text += " " + " ".join(exp.get("responsibilities", []))
                profile_text += " " + " ".join(exp.get("achievements", []))
            
            # Add skills
            skills = profile.get("skills", {})
            for skill in skills.get("technical", []):
                if isinstance(skill, dict):
                    profile_text += " " + skill.get("name", "")
                else:
                    profile_text += " " + str(skill)
            
            profile_text = profile_text.lower()
            profile_keywords = set(re.findall(r'\b[a-z]+\b', profile_text))
            profile_keywords = profile_keywords - stopwords
            
            # Calculate overlap
            common_keywords = job_keywords & profile_keywords
            
            if len(job_keywords) == 0:
                score = 50
            else:
                score = int((len(common_keywords) / len(job_keywords)) * 100)
            
            breakdown = {
                "total_job_keywords": len(job_keywords),
                "matched_keywords": len(common_keywords),
                "match_rate": f"{(len(common_keywords) / len(job_keywords) * 100):.1f}%" if len(job_keywords) > 0 else "0%",
                "top_matched": list(common_keywords)[:15]
            }
            
            return score, breakdown
            
        except Exception as e:
            print(f"Error calculating keyword match: {e}")
            return 50, {"error": str(e)}
    
    def _calculate_skills_gap(
        self,
        profile_skills: dict,
        parsed_data: dict
    ) -> dict:
        """Calculate skills gap analysis"""
        try:
            # Extract profile skills
            profile_tech_skills = set()
            for skill in profile_skills.get("technical", []):
                if isinstance(skill, dict):
                    profile_tech_skills.add(skill.get("name", "").lower())
                else:
                    profile_tech_skills.add(str(skill).lower())
            
            # Extract required skills
            required_skills = set(s.lower() for s in parsed_data.get("required_skills", []))
            preferred_skills = set(s.lower() for s in parsed_data.get("preferred_skills", []))
            
            # Calculate gaps
            critical_gaps = list(required_skills - profile_tech_skills)
            nice_to_have_gaps = list(preferred_skills - profile_tech_skills)
            
            return {
                "critical_missing_skills": critical_gaps[:10],
                "nice_to_have_missing_skills": nice_to_have_gaps[:10],
                "total_critical_gaps": len(critical_gaps),
                "total_nice_to_have_gaps": len(nice_to_have_gaps)
            }
            
        except Exception as e:
            print(f"Error calculating skills gap: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(
        self,
        overall_score: int,
        skills_breakdown: dict,
        experience_breakdown: dict,
        education_breakdown: dict
    ) -> list:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            # Skills recommendations
            missing_required = skills_breakdown.get("missing_required", [])
            if len(missing_required) > 0:
                recommendations.append({
                    "category": "skills",
                    "priority": "high",
                    "title": "Acquire Missing Required Skills",
                    "description": f"Focus on developing: {', '.join(missing_required[:5])}",
                    "action": "Take online courses or earn certifications in these areas"
                })
            
            # Experience recommendations
            if not experience_breakdown.get("meets_requirement", False):
                recommendations.append({
                    "category": "experience",
                    "priority": "high",
                    "title": "Gain More Experience",
                    "description": f"You have {experience_breakdown.get('total_years', 0)} years, but {experience_breakdown.get('required_years', 0)} years are required",
                    "action": "Consider taking on additional projects or freelance work to build experience"
                })
            
            # Relevant experience recommendation
            if experience_breakdown.get("relevant_positions", 0) == 0:
                recommendations.append({
                    "category": "experience",
                    "priority": "medium",
                    "title": "Highlight Transferable Skills",
                    "description": "You may not have direct experience in this role",
                    "action": "Emphasize transferable skills and relevant projects in your application"
                })
            
            # Overall score recommendations
            if overall_score >= 80:
                recommendations.append({
                    "category": "application",
                    "priority": "high",
                    "title": "Strong Match - Apply Confidently",
                    "description": "Your profile is an excellent match for this role",
                    "action": "Tailor your resume and apply as soon as possible"
                })
            elif overall_score >= 60:
                recommendations.append({
                    "category": "application",
                    "priority": "medium",
                    "title": "Good Match - Apply with Preparation",
                    "description": "You meet most requirements for this role",
                    "action": "Prepare a strong cover letter highlighting your relevant experience"
                })
            else:
                recommendations.append({
                    "category": "application",
                    "priority": "low",
                    "title": "Consider Skill Development",
                    "description": "There are significant gaps between your profile and this role",
                    "action": "Focus on building skills and experience before applying"
                })
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    def _get_match_level(self, score: int) -> str:
        """Get match level description"""
        if score >= 80:
            return "Excellent Match"
        elif score >= 70:
            return "Strong Match"
        elif score >= 60:
            return "Good Match"
        elif score >= 50:
            return "Moderate Match"
        else:
            return "Weak Match"
    
    def _get_fallback_score(self) -> dict:
        """Fallback score if calculation fails"""
        return {
            "overall_score": 50,
            "match_level": "Unknown",
            "breakdown": {},
            "skills_gap": {},
            "recommendations": [
                {
                    "category": "error",
                    "priority": "high",
                    "title": "Unable to Calculate Match Score",
                    "description": "There was an error calculating your match score",
                    "action": "Please ensure your profile is complete and try again"
                }
            ],
            "confidence": "low"
        }
