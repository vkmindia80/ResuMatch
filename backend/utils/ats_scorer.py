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
    # Enhanced ATS Scorer is now used via inheritance
    # All scoring methods are provided by EnhancedATSScorer
    pass
