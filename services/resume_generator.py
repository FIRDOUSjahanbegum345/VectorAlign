import os
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_pdf(lines, path):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 40

    for line in lines:
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line[:120])
        y -= 15

    c.save()


def create_optimized_resume(optimized_content, feedback, file_id):

    os.makedirs("generated", exist_ok=True)

    # ---------------- DOCX ----------------
    doc = Document()
    doc.add_heading("AI Resume Optimization Report", 0)

    doc.add_heading("ATS Summary", level=1)
    doc.add_paragraph(feedback.get("ats_score_evaluation", ""))

    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph(feedback.get("tailored_summary_suggestion", ""))

    doc.add_heading("Missing Keywords", level=1)
    for k in feedback.get("missing_keywords", []):
        doc.add_paragraph(f"• {k}")

    doc.add_heading("Improvement Areas", level=1)
    for i in feedback.get("structural_feedback", []):
        doc.add_paragraph(f"• {i}")

    doc.add_heading("Impact Improvements", level=1)
    for i in feedback.get("quantifiable_impact_suggestions", []):
        doc.add_paragraph(f"• {i}")

    doc.add_heading("FULL OPTIMIZED RESUME", level=1)
    doc.add_paragraph(feedback.get("optimized_resume", ""))

    docx_path = f"generated/optimized_{file_id}.docx"
    doc.save(docx_path)

    # ---------------- PDF ----------------
    pdf_lines = [
        "AI RESUME OPTIMIZATION REPORT",
        "",
        "ATS SUMMARY",
        feedback.get("ats_score_evaluation", ""),
        "",
        "SUMMARY",
        feedback.get("tailored_summary_suggestion", ""),
        "",
        "SKILLS GAP",
        *feedback.get("missing_keywords", []),
        "",
        "IMPROVEMENTS",
        *feedback.get("structural_feedback", []),
        "",
        "IMPACT",
        *feedback.get("quantifiable_impact_suggestions", []),
        "",
        "FULL RESUME",
        feedback.get("optimized_resume", "")
    ]

    pdf_path = f"generated/optimized_{file_id}.pdf"
    create_pdf(pdf_lines, pdf_path)

    return {
        "docx_path": docx_path,
        "pdf_path": pdf_path,
        "keyword_match_score": feedback.get("keyword_match_score", 0),
        "job_match_score": feedback.get("job_match_score", 0)
    }
