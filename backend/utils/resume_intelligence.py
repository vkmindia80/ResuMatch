"""
Advanced Resume Intelligence
Provides A/B testing suggestions, comparison tools, and optimization recommendations
"""
from typing import Dict, List, Tuple
from datetime import datetime


class ResumeIntelligence:
    def __init__(self):
        """Initialize Resume Intelligence"""
        pass
    
    def analyze_resume_performance(
        self,
        resume: dict,
        all_user_resumes: list
    ) -> dict:
        """
        Analyze resume performance and provide insights
        
        Args:
            resume: Resume to analyze
            all_user_resumes: All resumes from the user for comparison
            
        Returns:
            Dictionary with performance analysis
        """
        try:
            ats_score = resume.get("ats_score", {}).get("overall_score", 0)
            
            # Compare with user's other resumes
            other_scores = [
                r.get("ats_score", {}).get("overall_score", 0)
                for r in all_user_resumes
                if r.get("id") != resume.get("id")
            ]
            
            avg_score = sum(other_scores) / len(other_scores) if other_scores else ats_score
            best_score = max(other_scores) if other_scores else ats_score
            
            performance_level = "excellent" if ats_score >= 95 else \
                               "good" if ats_score >= 85 else \
                               "fair" if ats_score >= 75 else "needs improvement"
            
            return {
                "current_score": ats_score,
                "average_score": round(avg_score, 1),
                "best_score": best_score,
                "performance_level": performance_level,
                "better_than_average": ats_score > avg_score,
                "improvement_potential": max(0, best_score - ats_score),
                "percentile": self._calculate_percentile(ats_score, other_scores)
            }
            
        except Exception as e:
            print(f"Error analyzing resume performance: {e}")
            return {"error": str(e)}
    
    def generate_ab_testing_suggestions(
        self,
        resume: dict
    ) -> list:
        """
        Generate A/B testing suggestions for resume improvement
        
        Args:
            resume: Resume to analyze
            
        Returns:
            List of A/B testing suggestions
        """
        suggestions = []
        
        try:
            content = resume.get("content", {})
            ats_score = resume.get("ats_score", {})
            
            # Suggestion 1: Summary variations
            if content.get("summary"):
                suggestions.append({
                    "category": "summary",
                    "test_name": "Professional Summary Variations",
                    "variant_a": {
                        "type": "Achievement-focused",
                        "description": "Lead with quantifiable achievements and impact",
                        "example": "Software Engineer with 5+ years delivering 20% performance improvements"
                    },
                    "variant_b": {
                        "type": "Skills-focused",
                        "description": "Lead with core technical skills and expertise",
                        "example": "Expert in React, Node.js, AWS with proven track record"
                    },
                    "why_test": "Different hiring managers respond to different summary styles",
                    "expected_impact": "5-10% improvement in callback rate"
                })
            
            # Suggestion 2: Experience bullet formatting
            suggestions.append({
                "category": "experience",
                "test_name": "Bullet Point Format",
                "variant_a": {
                    "type": "Action Verb + Metric",
                    "description": "Start with strong action verb, end with metric",
                    "example": "Architected microservices reducing latency by 40%"
                },
                "variant_b": {
                    "type": "Context + Action + Result",
                    "description": "Provide context before action and result",
                    "example": "In high-traffic environment, architected microservices reducing latency by 40%"
                },
                "why_test": "Format affects readability and ATS parsing",
                "expected_impact": "3-7% ATS score improvement"
            })
            
            # Suggestion 3: Skills section organization
            suggestions.append({
                "category": "skills",
                "test_name": "Skills Organization",
                "variant_a": {
                    "type": "Categorized",
                    "description": "Group skills by category (Languages, Frameworks, Tools)",
                    "example": "Languages: Python, JavaScript | Frameworks: React, Django"
                },
                "variant_b": {
                    "type": "Priority-based",
                    "description": "List most relevant skills first, regardless of category",
                    "example": "React, AWS, Python, Docker, MongoDB, Node.js"
                },
                "why_test": "Different formats help ATS and human readers differently",
                "expected_impact": "5-8% improvement in keyword matching"
            })
            
            # Suggestion 4: Length optimization
            word_count = self._estimate_word_count(content)
            if word_count > 600:
                suggestions.append({
                    "category": "length",
                    "test_name": "Resume Length",
                    "variant_a": {
                        "type": "Detailed (current)",
                        "description": f"Comprehensive details (~{word_count} words)",
                        "example": "Include all relevant details and context"
                    },
                    "variant_b": {
                        "type": "Concise",
                        "description": "Focus on highest-impact content (~450 words)",
                        "example": "Only top achievements and critical skills"
                    },
                    "why_test": "Recruiters spend ~7 seconds per resume",
                    "expected_impact": "10-15% better engagement for short-form"
                })
            
            # Suggestion 5: Keyword density
            keyword_density = ats_score.get("keyword_density", {})
            if keyword_density:
                suggestions.append({
                    "category": "keywords",
                    "test_name": "Keyword Integration",
                    "variant_a": {
                        "type": "Natural integration (current)",
                        "description": "Keywords integrated naturally in context",
                        "example": "Developed React applications with Redux state management"
                    },
                    "variant_b": {
                        "type": "Strategic placement",
                        "description": "Keywords placed in headers and bullet starts",
                        "example": "React Development: Built applications using Redux..."
                    },
                    "why_test": "ATS systems may weight keyword placement differently",
                    "expected_impact": "3-5% ATS score improvement"
                })
            
            return suggestions[:4]  # Return top 4 suggestions
            
        except Exception as e:
            print(f"Error generating A/B testing suggestions: {e}")
            return []
    
    def compare_resumes(
        self,
        resume_a: dict,
        resume_b: dict
    ) -> dict:
        """
        Compare two resumes side-by-side
        
        Args:
            resume_a: First resume
            resume_b: Second resume
            
        Returns:
            Dictionary with comparison results
        """
        try:
            score_a = resume_a.get("ats_score", {}).get("overall_score", 0)
            score_b = resume_b.get("ats_score", {}).get("overall_score", 0)
            
            # Component comparisons
            components = ["keyword_match", "format_compatibility", "action_verbs_usage", 
                         "quantification_score", "impact_statements"]
            
            component_comparison = {}
            for comp in components:
                val_a = resume_a.get("ats_score", {}).get(comp, 0)
                val_b = resume_b.get("ats_score", {}).get(comp, 0)
                
                component_comparison[comp] = {
                    "resume_a": val_a,
                    "resume_b": val_b,
                    "difference": val_b - val_a,
                    "winner": "b" if val_b > val_a else "a" if val_a > val_b else "tie"
                }
            
            # Overall winner
            winner = "resume_b" if score_b > score_a else "resume_a" if score_a > score_b else "tie"
            
            # Key differences
            differences = []
            
            if component_comparison["keyword_match"]["difference"] != 0:
                diff_val = abs(component_comparison["keyword_match"]["difference"])
                better = "Resume B" if component_comparison["keyword_match"]["winner"] == "b" else "Resume A"
                differences.append({
                    "category": "Keywords",
                    "description": f"{better} has {diff_val} more keyword matches",
                    "impact": "high" if diff_val >= 5 else "medium"
                })
            
            if component_comparison["quantification_score"]["difference"] != 0:
                diff_val = abs(component_comparison["quantification_score"]["difference"])
                better = "Resume B" if component_comparison["quantification_score"]["winner"] == "b" else "Resume A"
                differences.append({
                    "category": "Quantification",
                    "description": f"{better} has {diff_val} more quantified achievements",
                    "impact": "medium"
                })
            
            return {
                "overall_winner": winner,
                "score_difference": abs(score_b - score_a),
                "resume_a_score": score_a,
                "resume_b_score": score_b,
                "component_comparison": component_comparison,
                "key_differences": differences,
                "recommendation": self._get_comparison_recommendation(winner, score_a, score_b)
            }
            
        except Exception as e:
            print(f"Error comparing resumes: {e}")
            return {"error": str(e)}
    
    def get_industry_optimization(
        self,
        resume: dict,
        target_industry: str
    ) -> dict:
        """
        Get industry-specific optimization recommendations
        
        Args:
            resume: Resume to optimize
            target_industry: Target industry (e.g., "tech", "finance", "healthcare")
            
        Returns:
            Dictionary with industry-specific recommendations
        """
        industry_templates = {
            "tech": {
                "preferred_format": "Technical skills first, projects section prominent",
                "key_sections": ["Technical Skills", "Projects", "Experience", "Education"],
                "recommended_keywords": ["architected", "engineered", "optimized", "scaled", "deployed"],
                "emphasis": "Technical depth and measurable impact",
                "avoid": "Soft skills without technical context"
            },
            "finance": {
                "preferred_format": "Education first (if from target school), quantified impact",
                "key_sections": ["Education", "Experience", "Certifications", "Skills"],
                "recommended_keywords": ["analyzed", "forecasted", "managed", "advised", "optimized"],
                "emphasis": "Quantitative results and financial metrics",
                "avoid": "Vague statements, unquantified claims"
            },
            "healthcare": {
                "preferred_format": "Certifications prominent, patient-focused language",
                "key_sections": ["Certifications", "Clinical Experience", "Education", "Skills"],
                "recommended_keywords": ["administered", "diagnosed", "coordinated", "improved", "implemented"],
                "emphasis": "Patient outcomes and compliance",
                "avoid": "Technical jargon without context"
            },
            "marketing": {
                "preferred_format": "Results-driven, campaigns and metrics prominent",
                "key_sections": ["Experience", "Campaigns/Projects", "Skills", "Education"],
                "recommended_keywords": ["launched", "increased", "optimized", "grew", "generated"],
                "emphasis": "ROI and growth metrics",
                "avoid": "Process without results"
            },
            "general": {
                "preferred_format": "Balanced approach with clear achievements",
                "key_sections": ["Experience", "Skills", "Education", "Achievements"],
                "recommended_keywords": ["achieved", "delivered", "improved", "led", "developed"],
                "emphasis": "Clear results and progression",
                "avoid": "Buzzwords without substance"
            }
        }
        
        template = industry_templates.get(target_industry.lower(), industry_templates["general"])
        
        return {
            "target_industry": target_industry,
            "recommended_format": template["preferred_format"],
            "key_sections": template["key_sections"],
            "power_words": template["recommended_keywords"],
            "emphasis_areas": template["emphasis"],
            "things_to_avoid": template["avoid"],
            "customization_tips": self._generate_industry_tips(target_industry, resume)
        }
    
    def _calculate_percentile(self, score: float, other_scores: list) -> int:
        """Calculate percentile ranking"""
        if not other_scores:
            return 50
        
        better_count = sum(1 for s in other_scores if score > s)
        percentile = int((better_count / len(other_scores)) * 100) if other_scores else 50
        return percentile
    
    def _estimate_word_count(self, content: dict) -> int:
        """Estimate word count from resume content"""
        word_count = 0
        
        try:
            # Summary
            if content.get("summary"):
                word_count += len(content["summary"].split())
            
            # Experience
            for exp in content.get("experience", []):
                for resp in exp.get("responsibilities", []):
                    word_count += len(resp.split())
                for ach in exp.get("achievements", []):
                    word_count += len(ach.split())
            
            # Skills (rough estimate)
            skills = content.get("skills", {})
            word_count += len(skills.get("technical", [])) * 2
            word_count += len(skills.get("soft", [])) * 2
            
            return word_count
            
        except Exception as e:
            return 500  # Default estimate
    
    def _get_comparison_recommendation(self, winner: str, score_a: float, score_b: float) -> str:
        """Get recommendation based on comparison"""
        if winner == "tie":
            return "Both resumes perform similarly. Consider A/B testing with actual applications."
        
        diff = abs(score_b - score_a)
        
        if diff < 3:
            return f"{winner.replace('_', ' ').title()} is slightly better. Small optimizations can help."
        elif diff < 10:
            return f"{winner.replace('_', ' ').title()} performs notably better. Use this for applications."
        else:
            return f"{winner.replace('_', ' ').title()} significantly outperforms. Strongly recommend using this version."
    
    def _generate_industry_tips(self, industry: str, resume: dict) -> list:
        """Generate industry-specific tips"""
        tips = []
        
        if industry.lower() == "tech":
            tips = [
                "Include GitHub/portfolio links prominently",
                "List technical skills before soft skills",
                "Mention tech stack for each project",
                "Quantify performance improvements and scale"
            ]
        elif industry.lower() == "finance":
            tips = [
                "Highlight CFA, CPA, or relevant certifications",
                "Use financial metrics (ROI, NPV, etc.)",
                "Mention firms and asset sizes",
                "Show analytical and quantitative skills"
            ]
        elif industry.lower() == "healthcare":
            tips = [
                "List all certifications and licenses",
                "Emphasize patient outcomes",
                "Mention compliance and regulations",
                "Include continuing education"
            ]
        else:
            tips = [
                "Tailor content to job description",
                "Use industry-specific terminology",
                "Highlight relevant achievements",
                "Show progression and growth"
            ]
        
        return tips
