import os
from docx import Document

def create_optimized_resume(optimized_content: str, feedback: str, file_id: str) -> str:
    doc = Document()
    doc.add_heading('VectorAlign AI - Resume Optimization Strategy', 0)
    
    doc.add_heading('Suggested Summary Section', level=1)
    doc.add_paragraph(optimized_content)
    
    doc.add_heading('Target Improvement Feedback Matrix', level=1)
    doc.add_paragraph(feedback)
    
    output_filename = f"optimized_{file_id}.docx"
    output_path = os.path.join("generated", output_filename)
    doc.save(output_path)
    return output_path
