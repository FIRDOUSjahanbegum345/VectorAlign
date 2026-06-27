import os
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# =========================
# CONFIG
# =========================
GENERATED_DIR = "generated"
os.makedirs(GENERATED_DIR, exist_ok=True)


# =========================
# PDF CREATION
# =========================
def create_pdf(lines, path):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 40

    for line in lines:
        if y < 40:
            c.showPage()
            y = height - 40

        # Clean encoding issues + prevent overflow
        safe_line = str(line).encode("utf-8", "ignore").decode("utf-8")
        c.drawString(40, y, safe_line[:120])
        y -= 15

    c.save()


# =========================
# TEXT CLEANER
# =========================
def clean_resume_text(text):
    """
    Formats AI-generated resume text for readability
    """
    if not text:
        return ""

    text = text.replace("\r", "")
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    formatted_lines = []

    for line in lines:
        if any(keyword in line.lower() for keyword in [
            "skills", "projects", "education", "experience",
            "certifications", "summary", "work"
        ]):
            formatted_lines.append("\n" + line.upper())
        else:
            formatted_lines.append(line)

    return "\n".join(formatted_lines)


# =========================
# MAIN GENERATOR
# =========================
def create_optimized_resume(optimized_content, feedback, file_id):

    # ---------------- GET RESUME ----------------
    optimized_resume = feedback.get("optimized_resume", "")

    if not optimized_resume:
        optimized_resume = feedback.get("tailored_summary_suggestion", "")

    optimized_resume = clean_resume_text(optimized_resume)

    # ---------------- DOCX ----------------
    doc = Document()
    doc.add_heading("AI Resume Optimization Report", 0)

    doc.add_heading("ATS Score Analysis", level=1)
    doc.add_paragraph(feedback.get("ats_score_evaluation", "N/A"))

    doc.add_heading("PROFESSIONAL OPTIMIZED RESUME", level=1)
    doc.add_paragraph(optimized_resume)

    # Missing Keywords
    doc.add_heading("Missing Keywords", level=1)
    missing = feedback.get("missing_keywords", [])
    if missing:
        for k in missing:
            doc.add_paragraph(f"• {k}")
    else:
        doc.add_paragraph("No missing keywords detected.")

    # Structural Feedback
    doc.add_heading("Structural Feedback", level=1)
    structural = feedback.get("structural_feedback", [])
    if structural:
        for i in structural:
            doc.add_paragraph(f"• {i}")
    else:
        doc.add_paragraph("Resume structure is strong.")

    # Impact Suggestions
    doc.add_heading("Impact Improvements", level=1)
    impact = feedback.get("quantifiable_impact_suggestions", [])
    if impact:
        for i in impact:
            doc.add_paragraph(f"• {i}")
    else:
        doc.add_paragraph("No improvements required.")

    docx_path = os.path.join(GENERATED_DIR, f"optimized_{file_id}.docx")
    doc.save(docx_path)

    # ---------------- PDF ----------------
    pdf_lines = [
        "AI RESUME OPTIMIZATION REPORT",
        "",
        "ATS SCORE ANALYSIS",
        feedback.get("ats_score_evaluation", "N/A"),
        "",
        "OPTIMIZED RESUME",
        optimized_resume,
        "",
        "MISSING KEYWORDS",
        *feedback.get("missing_keywords", []),
        "",
        "STRUCTURAL FEEDBACK",
        *feedback.get("structural_feedback", []),
        "",
        "IMPACT IMPROVEMENTS",
        *feedback.get("quantifiable_impact_suggestions", []),
    ]

    pdf_path = os.path.join(GENERATED_DIR, f"optimized_{file_id}.pdf")
    create_pdf(pdf_lines, pdf_path)

    # ---------------- RESPONSE ----------------
    return {
        "docx_path": docx_path,
        "pdf_path": pdf_path,
        "optimized_resume": optimized_resume,
        "keyword_match_score": feedback.get("keyword_match_score", 0),
        "job_match_score": feedback.get("job_match_score", 0)
    }
