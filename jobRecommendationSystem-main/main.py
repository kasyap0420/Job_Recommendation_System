from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import mysql.connector
import fitz  # PyMuPDF for PDF parsing
import os
import requests
import google.generativeai as genai

app = FastAPI()

# Database connection setup (update with your credentials)
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pass123",
        database="healthcare"
    )

# Pydantic model for user data
class UserData(BaseModel):
    id: int
    name: str
    skill: str
    resume: Optional[str] = None
    certificates: Optional[str] = None

@app.post("/save")
def save_user(
    id: int = Form(...),
    name: str = Form(...),
    skill: str = Form(...),
    resume: Optional[str] = Form(None),
    certificates: Optional[str] = Form(None)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (id, name, skill, resume, certificates) VALUES (%s, %s, %s, %s, %s)",
            (id, name, skill, resume, certificates)
        )
        conn.commit()
        return {"message": "User data saved successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/parsing")
def parse_resume(id: int = Form(...), file: UploadFile = File(...)):
    # Save uploaded PDF
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    # Parse PDF
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF parsing failed: {e}")
    # Save parsed resume text to DB
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET resume=%s WHERE id=%s",
            (text, id)
        )
        conn.commit()
        return {"message": "Resume parsed and saved successfully", "resume_text": text[:200]}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

GOOGLE_API_KEY="AIzaSyBCB6RADF3dIDMcRHDq4ePv3AfoLnuekCs"

@app.post("/suggestjob/{user_id}")
async def job_suggestion(user_id: int):
    if not GOOGLE_API_KEY:
        return JSONResponse(content={"error": "Google API key not provided"}, status_code=status.HTTP_400_BAD_REQUEST)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT skill, resume, certificates FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return JSONResponse(content={"error": "User not found"}, status_code=status.HTTP_404_NOT_FOUND)
        if not user["resume"]:
            return JSONResponse(content={"error": "Resume not uploaded"}, status_code=status.HTTP_400_BAD_REQUEST)
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Generate me only one job recommendation from this resume uploaded. No extra text only job title: {user['resume']}"
        response = await model.generate_content_async(prompt)
        job_title = response.text.strip()
        return JSONResponse(content={"job_title": job_title, "user_id": user_id})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)