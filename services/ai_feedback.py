import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def clean_json(text: str):
    if not text:
        return None

    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = text.strip()

    try:
        return json.loads(text)
    except:
        return None


def fallback(ats_score):
    return {
        "ats_score_evaluation": f"ATS Score: {ats_score}%. Needs optimization.",
        "missing_keywords": ["Python", "FastAPI", "SQL", "System Design"],
        "structural_feedback": ["Improve formatting", "Add metrics", "Use ATS keywords"],
        "quantifiable_impact_suggestions": ["Add measurable impact like % improvements"],
        "tailored_summary_suggestion": "Full Stack Developer with backend and frontend experience.",
        "optimized_resume": "Resume optimization unavailable - fallback used."
    }


def generate_feedback(resume_text: str, job_description: str, ats_score: float):

    prompt = f"""
You are an expert ATS Resume Engine.

Return ONLY valid JSON.

Schema:
{{
  "ats_score_evaluation": string,
  "missing_keywords": [string],
  "structural_feedback": [string],
  "quantifiable_impact_suggestions": [string],
  "tailored_summary_suggestion": string,
  "optimized_resume": string,
  "keyword_match_score": number,
  "job_match_score": number
}}

RULES:
- optimized_resume MUST be a full professional resume with sections:
  Summary, Skills, Experience, Projects, Education
- Make it ATS optimized
- No markdown
- No explanation

ATS SCORE: {ats_score}

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-flash-latest",
    ]

    for model in models:
        try:
            res = client.models.generate_content(
                model=model,
                contents=prompt
            )

            data = clean_json(res.text)
            if data:
                return data

        except Exception as e:
            print("Gemini error:", e)

    return fallback(ats_score)
