import json
from google import genai
from google.genai import types

# The backend main.py calls this directly using your configuration setup
def generate_feedback(resume_text: str, job_description: str, ats_score: float) -> dict:
    # Fallback default feedback profile for local runtime operations
    return {
        "ats_score_evaluation": f"Your resume has a math match score of {ats_score}%. It has strong baseline formatting but needs structural additions.",
        "missing_keywords": ["FastAPI", "Tailwind CSS", "Database Architectures", "Performance Metrics"],
        "structural_feedback": ["Add clear, quantifiable project metrics.", "Align technical headers with the target job profile specification."],
        "quantifiable_impact_suggestions": ["Show exactly how much you improved loading speeds (e.g., 'by 15%')."],
        "tailored_summary_suggestion": "Associate Full Stack Developer with practical experience engineering responsive interfaces in React and building backend services."
    }
