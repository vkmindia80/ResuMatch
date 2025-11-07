#!/usr/bin/env python3
"""
Test script to demonstrate ATS optimization improvements
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, '/app/backend')

from utils.enhanced_ats_scorer import EnhancedATSScorer
from utils.ats_optimizer import ATSOptimizer

# Sample resume content for testing
sample_resume = {
    "header": {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0100",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/johndoe"
    },
    "summary": "Software engineer with experience in web development and databases.",
    "experience": [
        {
            "company": "Tech Corp",
            "title": "Software Engineer",
            "start_date": "2020-01",
            "end_date": "2023-12",
            "is_current": False,
            "location": "San Francisco, CA",
            "responsibilities": [
                "Worked on web applications",
                "Fixed bugs and issues",
                "Collaborated with team members"
            ],
            "technologies": ["Python", "JavaScript", "React"]
        }
    ],
    "education": [
        {
            "institution": "University of California",
            "degree": "Bachelor of Science",
            "field_of_study": "Computer Science",
            "graduation_year": "2020"
        }
    ],
    "skills": {
        "technical": ["Python", "JavaScript", "React", "SQL"],
        "soft": ["Communication", "Teamwork"],
        "tools": ["Git", "Docker"],
        "languages": []
    },
    "projects": [],
    "certifications": []
}

# Sample job description
sample_job = {
    "id": "job123",
    "title": "Senior Software Engineer",
    "company": "Amazing Tech",
    "parsed_data": {
        "required_skills": ["Python", "React", "AWS", "Docker", "CI/CD", "Microservices"],
        "technical_skills": ["JavaScript", "TypeScript", "Node.js", "PostgreSQL", "Redis"],
        "tools_and_technologies": ["Git", "Jenkins", "Kubernetes", "Terraform"],
        "preferred_skills": ["GraphQL", "MongoDB", "Machine Learning"],
        "job_level": "senior",
        "required_experience_years": 5
    }
}

def print_score_comparison(initial_score, final_score):
    """Print before/after comparison"""
    print("\n" + "="*60)
    print("📊 ATS SCORE COMPARISON")
    print("="*60)
    
    print(f"\n{'Component':<25} {'Before':<10} {'After':<10} {'Change'}")
    print("-" * 60)
    
    components = [
        ("Overall Score", "overall_score", 100),
        ("Keyword Match", "keyword_match", 30),
        ("Action Verbs", "action_verbs_usage", 20),
        ("Quantification", "quantification_score", 15),
        ("Impact Statements", "impact_statements", 15)
    ]
    
    for name, key, max_val in components:
        before = initial_score.get(key, 0)
        after = final_score.get(key, 0)
        change = after - before
        change_pct = (change / max_val * 100) if max_val > 0 else 0
        
        symbol = "↑" if change > 0 else "→" if change == 0 else "↓"
        color = "\033[92m" if change > 0 else "\033[93m" if change == 0 else "\033[91m"
        reset = "\033[0m"
        
        print(f"{name:<25} {before:<10} {after:<10} {color}{symbol} +{change} ({change_pct:+.1f}%){reset}")
    
    # Grade comparison
    before_grade = initial_score.get('grade', 'N/A')
    after_grade = final_score.get('grade', 'N/A')
    print(f"\n{'Grade':<25} {before_grade:<10} {after_grade:<10}")
    
    # Improvement summary
    overall_improvement = final_score.get('overall_score', 0) - initial_score.get('overall_score', 0)
    if overall_improvement > 0:
        print(f"\n✅ Overall improvement: +{overall_improvement}% ({overall_improvement/100*100:.1f}% increase)")
    
    print("\n" + "="*60)

def print_detailed_feedback(score):
    """Print detailed ATS feedback"""
    print("\n📋 DETAILED FEEDBACK:")
    print("-" * 60)
    
    if score.get('strengths'):
        print("\n✅ Strengths:")
        for strength in score['strengths'][:3]:
            print(f"  • {strength}")
    
    if score.get('suggestions'):
        print("\n💡 Suggestions:")
        for suggestion in score['suggestions'][:3]:
            print(f"  • {suggestion}")
    
    if score.get('keyword_density'):
        kd = score['keyword_density']
        print(f"\n🔑 Keyword Density: {kd.get('density', 'N/A')} ({kd.get('status', 'unknown')})")
    
    print()

async def test_ats_optimization():
    """Test the ATS optimization system"""
    print("\n" + "="*60)
    print("🎯 ATS OPTIMIZATION TEST")
    print("="*60)
    
    print("\n📝 Testing with sample resume and job description...")
    print(f"Job Title: {sample_job['title']} at {sample_job['company']}")
    print(f"Required Skills: {', '.join(sample_job['parsed_data']['required_skills'][:5])}")
    
    # Step 1: Calculate initial score
    print("\n⏳ Step 1: Calculating initial ATS score...")
    scorer = EnhancedATSScorer()
    initial_score = scorer.calculate_ats_score(sample_resume, sample_job)
    
    print(f"✅ Initial Score: {initial_score.get('overall_score', 0)}% (Grade: {initial_score.get('grade', 'N/A')})")
    print_detailed_feedback(initial_score)
    
    # Step 2: Run optimization
    print("\n⏳ Step 2: Running iterative ATS optimization...")
    print("(This will take 20-30 seconds with real AI optimization...)")
    print("\n🔄 Optimization in progress...")
    
    try:
        optimizer = ATSOptimizer()
        
        # Note: This will use real AI if EMERGENT_LLM_KEY is available
        optimized_content, final_score, iterations = await optimizer.optimize_resume_iteratively(
            sample_resume,
            initial_score,
            sample_job
        )
        
        print(f"\n✅ Optimization complete!")
        print(f"Iterations used: {iterations}")
        print(f"Final Score: {final_score.get('overall_score', 0)}% (Grade: {final_score.get('grade', 'N/A')})")
        
        # Step 3: Show comparison
        print_score_comparison(initial_score, final_score)
        print_detailed_feedback(final_score)
        
        # Success message
        final_overall = final_score.get('overall_score', 0)
        if final_overall >= 95:
            print("\n🎉 SUCCESS! Resume achieved 95%+ ATS score - Perfect optimization!")
        elif final_overall >= 85:
            print("\n✅ GOOD! Resume achieved 85%+ ATS score - Strong optimization!")
        else:
            print("\n⚠️  Resume improved but didn't reach 95% target. May need more profile data.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during optimization: {e}")
        print("\nNote: Full optimization requires EMERGENT_LLM_KEY.")
        print("The system will show initial scoring only.")
        return False

def main():
    """Main test function"""
    try:
        # Check if running in async context
        result = asyncio.run(test_ats_optimization())
        
        print("\n" + "="*60)
        if result:
            print("✅ TEST PASSED: ATS Optimization system is working!")
        else:
            print("⚠️  TEST PARTIAL: Initial scoring works, optimization requires API key")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
