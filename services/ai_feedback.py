import os
import json

# 🔥 If you're using OpenAI
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


ATS_PROMPT = """
You are an expert ATS resume writer and senior technical recruiter.

You MUST convert the input into a structured ATS-optimized resume.

ABSOLUTE RULES:
- DO NOT write paragraphs
- DO NOT summarize
- ONLY return valid JSON
- MUST use bullet points (•)
- MUST be recruiter-ready
- MUST include ATS keywords from job description
- MUST quantify achievements where possible

OUTPUT FORMAT (STRICT JSON ONLY):

{
  "ats_score": 0-100,
  "feedback": {
    "ats_score_evaluation": "",
    "missing_keywords": [],
    "structural_feedback": [],
    "quantifiable_impact_suggestions": [],
    "tailored_summary_suggestion": ""
  },
  "optimized_resume": {
    "professional_summary": [],
    "technical_skills": [],
    "work_experience": [],
    "projects": [],
    "education": []
  }
}

INPUT RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON. No extra text.
"""


def generate_ai_feedback(resume_text: str, job_description: str):

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # you can change model
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict ATS resume parser that outputs only JSON."
                },
                {
                    "role": "user",
                    "content": ATS_PROMPT.format(
                        resume_text=resume_text,
                        job_description=job_description
                    )
                }
            ],
            temperature=0.2
        )

        raw_output = response.choices[0].message.content

        # 🧠 Convert to JSON safely
        try:
            parsed_output = json.loads(raw_output)
        except:
            # fallback cleanup if model adds text
            cleaned = raw_output.strip().replace("```json", "").replace("```", "")
            parsed_output = json.loads(cleaned)

        return parsed_output

    except Exception as e:
        return {
            "ats_score": 0,
            "feedback": {
                "ats_score_evaluation": f"Error generating feedback: {str(e)}",
                "missing_keywords": [],
                "structural_feedback": [],
                "quantifiable_impact_suggestions": [],
                "tailored_summary_suggestion": ""
            },
            "optimized_resume": {
                "professional_summary": [],
                "technical_skills": [],
                "work_experience": [],
                "projects": [],
                "education": []
            }
        }
