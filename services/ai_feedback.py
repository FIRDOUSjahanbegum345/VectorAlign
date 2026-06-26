import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"#{1,6}", "", text)
    return text.strip()


def fallback_response(ats_score: float):
    return {
        "ats_score_evaluation": f"ATS Score is {ats_score}%. Resume needs improvement in keyword alignment and structure.",
        "missing_keywords": ["Python", "FastAPI", "SQL", "System Design"],
        "structural_feedback": [
            "Add measurable achievements",
            "Improve project descriptions",
            "Use ATS-friendly headings"
        ],
        "quantifiable_impact_suggestions": [
            "Add performance improvements (e.g. reduced latency by 20%)"
        ],
        "tailored_summary_suggestion": "Full Stack Developer with experience in backend and frontend development."
    }


def generate_feedback(resume_text: str, job_description: str, ats_score: float) -> dict:
    prompt = f"""
You are an expert ATS resume analyzer.

Return ONLY valid JSON (no explanation, no markdown).

Schema:
{{
  "ats_score_evaluation": string,
  "missing_keywords": [string],
  "structural_feedback": [string],
  "quantifiable_impact_suggestions": [string],
  "tailored_summary_suggestion": string,
  "optimized_resume": string
}}

Rules:
- Make optimized_resume a FULL professional resume (NOT 2 lines)
- Include: Summary, Skills, Experience, Projects, Education
- Add real improvements based on job description
- Make it ATS optimized
- Do NOT include markdown

ATS Score: {ats_score}

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    model_names = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-flash-latest",
    ]

    for model in model_names:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            text = clean_text(response.text)

            # Try parse JSON
            try:
                data = json.loads(text)
                return data
            except:
                # If model fails JSON format, wrap fallback
                return fallback_response(ats_score)

        except Exception as e:
            print("Gemini error:", e)
            continue

    return fallback_response(ats_score)
