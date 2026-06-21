import pdfplumber
from docx import Document

def extract_resume_text(file_path: str, extension: str) -> str:
    text = ""
    if extension == "pdf":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    elif extension == "docx":
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    elif extension == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    return text
