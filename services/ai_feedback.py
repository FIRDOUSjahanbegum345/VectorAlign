import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def extract_json(text: str):
    """
    Extract JSON even if Gemini wraps it in ```json blocks.
    """
    if not text:
        return None

    text = text.strip()

    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        return None


def fallback(ats_score):
    return {
        "ats_score_evaluation": f"ATS Score: {ats_score}/100. Resume requires further optimization.",
        "missing_keywords": [],
        "structural_feedback": [
            "Improve formatting",
            "Use ATS-friendly headings",
            "Add measurable achievements",
            "Include more job-specific keywords"
        ],
        "quantifiable_impact_suggestions": [
            "Mention percentage improvements",
            "Highlight measurable project outcomes"
        ],
        "tailored_summary_suggestion":
            "AI Engineer passionate about software development, machine learning and scalable applications.",

        "optimized_resume": """PROFESSIONAL SUMMARY

• Motivated Software Engineer with experience in Python, JavaScript, HTML, CSS and Machine Learning.
• Strong knowledge of FastAPI, AI, Data Science and Web Development.
• Experienced in developing scalable applications and AI-powered solutions.
• Passionate about solving real-world engineering problems.

TECHNICAL SKILLS

• Python
• Java
• C
• HTML5
• CSS3
• JavaScript
• FastAPI
• SQL
• Machine Learning
• Scikit-learn
• Pandas
• Git
• GitHub

WORK EXPERIENCE

• Add your professional experience here.

PROJECTS

• AI Resume Analyzer
• Network Security Scanner

EDUCATION

Bachelor's Degree
Artificial Intelligence & Data Science
""",
        "keyword_match_score": ats_score,
        "job_match_score": ats_score
    }


def generate_feedback(resume_text: str, job_description: str, ats_score: float):

    prompt = f"""
You are a Senior ATS Resume Writer and Technical Recruiter.

Return ONLY valid JSON.

The JSON MUST have this exact schema:

{{
"ats_score_evaluation":"",
"missing_keywords":[],
"structural_feedback":[],
"quantifiable_impact_suggestions":[],
"tailored_summary_suggestion":"",
"optimized_resume":"",
"keyword_match_score":0,
"job_match_score":0
}}

VERY IMPORTANT:

optimized_resume MUST be a COMPLETE PROFESSIONAL RESUME.

DO NOT SUMMARIZE.

DO NOT WRITE A PARAGRAPH.

USE THIS FORMAT:

PROFESSIONAL SUMMARY
• 4-6 bullet points

TECHNICAL SKILLS
• Bullet list

WORK EXPERIENCE
• Bullet points
• Use strong action verbs
• Include measurable achievements where possible

PROJECTS
• Bullet points
• Mention technologies used
• Mention impact

EDUCATION
• Proper education section

CERTIFICATIONS
• If unavailable, generate relevant placeholders

CORE STRENGTHS
• Bullet list

ATS KEYWORDS
• Include important keywords from the job description

RULES:

- Output ONLY JSON
- No markdown
- No code fences
- optimized_resume should be 700-1200 words
- Use ATS-friendly formatting
- Add missing keywords naturally
- Make the resume recruiter-ready
- Do not explain anything

ATS SCORE:
{ats_score}

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash"
    ]

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            text = response.text

            data = extract_json(text)

            if data:
                return data

        except Exception as e:
            print(f"Gemini Error ({model}):", e)

    return fallback(ats_score)
