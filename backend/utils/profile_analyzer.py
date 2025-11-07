from models.profile import Profile
from typing import Dict

def calculate_completeness_score(profile: Profile) -> int:
    """
    Calculate profile completeness score (0-100)
    """
    score = 0
    max_score = 100
    
    # Personal Info (30 points)
    personal = profile.personal_info
    if personal:
        if personal.full_name:
            score += 5
        if personal.email:
            score += 5
        if personal.phone:
            score += 5
        if personal.location:
            score += 5
        if personal.title:
            score += 5
        if personal.linkedin or personal.portfolio:
            score += 5
    
    # Education (20 points)
    if profile.education:
        if len(profile.education) >= 1:
            score += 10
        if len(profile.education) >= 2:
            score += 5
        # Check for detailed education info
        for edu in profile.education:
            if edu.gpa:
                score += 2
                break
        if any(edu.achievements for edu in profile.education):
            score += 3
    
    # Experience (25 points)
    if profile.experience:
        if len(profile.experience) >= 1:
            score += 10
        if len(profile.experience) >= 2:
            score += 5
        # Check for detailed experience
        for exp in profile.experience:
            if exp.responsibilities:
                score += 3
                break
        if any(exp.achievements for exp in profile.experience):
            score += 4
        if any(exp.technologies for exp in profile.experience):
            score += 3
    
    # Skills (15 points)
    if profile.skills:
        if profile.skills.technical:
            score += 5
        if profile.skills.soft:
            score += 3
        if profile.skills.languages:
            score += 3
        if profile.skills.tools:
            score += 4
    
    # Projects (5 points)
    if profile.projects:
        if len(profile.projects) >= 1:
            score += 3
        if len(profile.projects) >= 2:
            score += 2
    
    # Certifications (5 points)
    if profile.certifications:
        if len(profile.certifications) >= 1:
            score += 3
        if len(profile.certifications) >= 2:
            score += 2
    
    return min(score, max_score)

def get_missing_sections(profile: Profile) -> Dict[str, str]:
    """
    Identify missing or incomplete profile sections
    """
    missing = {}
    
    # Check personal info
    if not profile.personal_info.phone:
        missing["phone"] = "Add your phone number to make it easier for recruiters to contact you"
    if not profile.personal_info.title:
        missing["title"] = "Add a professional title (e.g., 'Software Engineer', 'Marketing Manager')"
    if not profile.personal_info.linkedin and not profile.personal_info.portfolio:
        missing["online_presence"] = "Add your LinkedIn profile or portfolio URL"
    
    # Check education
    if not profile.education:
        missing["education"] = "Add your educational background"
    
    # Check experience
    if not profile.experience:
        missing["experience"] = "Add your work experience"
    elif profile.experience:
        for exp in profile.experience:
            if not exp.responsibilities:
                missing["experience_details"] = "Add responsibilities for your work experience"
                break
    
    # Check skills
    if not profile.skills.technical:
        missing["technical_skills"] = "Add your technical skills"
    
    # Check projects
    if not profile.projects:
        missing["projects"] = "Add projects you've worked on to showcase your skills"
    
    return missing
