# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from parser import read_docx, extract_resume_sections, fetch_job_text_from_url

app = FastAPI()

# Allow frontend access (CORS policy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Upload Resume Endpoint ===
@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = read_docx(file_path)
    sections = extract_resume_sections(resume_text)

    return {
        "filename": file.filename,
        "parsed_sections": sections
    }

# === Upload Job Description Endpoint ===
@app.post("/upload-job/")
async def upload_job(
    file: UploadFile = File(None),
    url: str = Form(None)
):
    job_text = ""

    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        job_text = read_docx(file_path)

    elif url:
        job_text = fetch_job_text_from_url(url)

    else:
        return {"error": "Please upload a file or provide a URL."}

    job_sections = extract_resume_sections(job_text)

    return {
        "source": file.filename if file else url,
        "parsed_sections": job_sections
    }

from pydantic import BaseModel
from typing import Dict
from matcher import calculate_match_score

class MatchRequest(BaseModel):
    resume: Dict[str, str]
    job: Dict[str, str]

@app.post("/match-score/")
def match_score(request: MatchRequest):
    score, breakdown, suggestions = calculate_match_score(request.resume, request.job)

    return {
        "match_score": f"{score}%",
        "breakdown": breakdown,
        "suggestions": suggestions
    }