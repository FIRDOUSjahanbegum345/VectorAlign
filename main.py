import os
import uuid
import bcrypt

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.parser import extract_resume_text
from services.scorer import calculate_ats_score
from services.ai_feedback import generate_feedback
from services.resume_generator import create_optimized_resume
from services.database import init_db, SessionLocal, User, Scan

# ---------------- INIT DB ----------------
init_db()

app = FastAPI(title="VectorAlign AI - Core Optimization Engine", version="3.0.0")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://vectoralign-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
GENERATED_DIR = "generated"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# ---------------- AUTH MODEL ----------------
class UserAuth(BaseModel):
    username: str
    password: str

# ---------------- DB Dependency ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- SIGNUP ----------------
@app.post("/auth/signup")
async def signup(user: UserAuth, db: Session = Depends(get_db)):
    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    new_user = User(username=user.username, password=hashed_pw)
    try:
        db.add(new_user)
        db.commit()
        return {"status": "success"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")

# ---------------- LOGIN ----------------
@app.post("/auth/login")
async def login(user: UserAuth, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not bcrypt.checkpw(user.password.encode(), db_user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"status": "success", "username": db_user.username}

# ---------------- RESUME ANALYZE ----------------
@app.post("/resume/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    file_id = str(uuid.uuid4())
    extension = resume.filename.split(".")[-1].lower()

    if extension not in ["pdf", "docx", "txt"]:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{extension}")
    with open(file_path, "wb") as f:
        f.write(await resume.read())

    try:
        # ---------------- PIPELINE ----------------
        resume_text = extract_resume_text(file_path, extension)
        ats_score = calculate_ats_score(resume_text, job_description)
        feedback_matrix = generate_feedback(resume_text, job_description, ats_score)

        # ---------------- GENERATE DOCX + PDF ----------------
        files = create_optimized_resume(
            optimized_content=feedback_matrix.get("optimized_resume", ""),
            feedback=feedback_matrix,
            file_id=file_id
        )

        # ---------------- DB SAVE ----------------
        new_scan = Scan(user_id=user_id, ats_score=ats_score)
        db.add(new_scan)
        db.commit()

        total_scans = db.query(Scan).filter(Scan.user_id == user_id).count()

        # ---------------- RESPONSE ----------------
        return {
            "file_id": file_id,
            "ats_score": ats_score,
            "total_scans": total_scans,
            "mean_vector_match": round(ats_score * 3, 2),
            "system_peak_match": round(ats_score * 4, 2),
            "feedback": feedback_matrix,
            "download_url": f"/resume/download/{file_id}",
            "download_docx": files["docx_path"],
            "download_pdf": files["pdf_path"],
            "keyword_match_score": feedback_matrix.get("keyword_match_score", 0),
            "job_match_score": feedback_matrix.get("job_match_score", 0)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- TOTAL SCANS (GLOBAL) ----------------
@app.get("/scans/total")
async def get_total_scans(db: Session = Depends(get_db)):
    total = db.query(Scan).count()
    return {"total": total}

# ---------------- TOTAL SCANS (PER USER) ----------------
@app.get("/scans/total/{user_id}")
async def get_user_total_scans(user_id: str, db: Session = Depends(get_db)):
    total = db.query(Scan).filter(Scan.user_id == user_id).count()
    return {"user_id": user_id, "total": total}

# ---------------- DOWNLOAD DOCX ----------------
@app.get("/resume/download/{file_id}")
async def download_resume(file_id: str):
    file_path = os.path.join(GENERATED_DIR, f"optimized_{file_id}.docx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path,
        filename="VectorAlign_Optimized_Resume.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# ---------------- DOWNLOAD PDF ----------------
@app.get("/resume/download/pdf/{file_id}")
async def download_pdf(file_id: str):
    file_path = os.path.join(GENERATED_DIR, f"optimized_{file_id}.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path,
        filename="VectorAlign_Optimized_Resume.pdf",
        media_type="application/pdf"
    )

# ---------------- HEALTH CHECK ----------------
@app.get("/")
def home():
    return {
        "message": "VectorAlign AI Backend Running (SQLAlchemy version)",
        "version": "3.0.0"
    }

# ---------------- RUN ----------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
