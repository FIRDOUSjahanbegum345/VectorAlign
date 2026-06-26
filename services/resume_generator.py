import os
from docx import Document


def create_optimized_resume(optimized_content: str, feedback: dict, file_id: str) -> str:
    doc = Document()

    doc.add_heading("AI Optimized Resume - VectorAlign", 0)

    # -------- SUMMARY --------
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph(feedback.get("tailored_summary_suggestion", ""))

    # -------- SKILLS --------
    doc.add_heading("Missing / Suggested Skills", level=1)
    for skill in feedback.get("missing_keywords", []):
        doc.add_paragraph(f"• {skill}")

    # -------- STRUCTURAL FEEDBACK --------
    doc.add_heading("Improvement Areas", level=1)
    for item in feedback.get("structural_feedback", []):
        doc.add_paragraph(f"• {item}")

    # -------- IMPACT SUGGESTIONS --------
    doc.add_heading("Quantifiable Improvements", level=1)
    for item in feedback.get("quantifiable_impact_suggestions", []):
        doc.add_paragraph(f"• {item}")

    # -------- FULL OPTIMIZED RESUME --------
    doc.add_heading("Full Optimized Resume", level=1)
    doc.add_paragraph(feedback.get("optimized_resume", ""))

    output_filename = f"optimized_{file_id}.docx"
    output_path = os.path.join("generated", output_filename)

    doc.save(output_path)

    return output_path
