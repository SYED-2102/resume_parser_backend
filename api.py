import os
import re
import shutil
import time
import concurrent.futures
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import your custom NLP and processing modules
from extractor import extract_text_from_pdf
from cleaner import clean_raw_text
from nlp_processor import extract_entities
from contact_extractor import extract_contact_info
from metrics_extractor import extract_metrics
from gap_analyzer import analyze_skill_gap
from semantic_engine import calculate_match_score
from interview_bot import generate_premium_analysis

app = FastAPI(title="Recruitment AI - Premium Tier (Staggered Parallel)")

# Critical for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_demo_response():
    """Returns a perfect, hardcoded JSON response instantly for presentations."""
    print("⚠️ WARNING: DEMO MODE ENGAGED. RETURNING MOCK DATA. ⚠️")
    import asyncio
    return {
        "batch_info": {
            "total_processed": 2,
            "successful": 2,
            "failed": 0
        },
        "job_description_skills": ["Python", "React", "Docker", "AWS"],
        "ranked_candidates": [
            {
                "filename": "Alex_Mercer_Resume.pdf",
                "status": "SUCCESS",
                "dossier": {
                    "name": "Alex Mercer",
                    "emails": ["alex.mercer@email.com"],
                    "phones": ["+1 555-0198"],
                    "gpa": "9.2 / 10.0"
                },
                "analytics": {
                    "final_score": 94.5,
                    "skills_found": ["Python", "React", "Node.js", "Docker"],
                    "missing_skills": ["AWS"]
                },
                "premium_insights": {
                    "quality_score": 92,
                    "suggestions": [
                        "Excellent metric-driven bullet points.",
                        "Add an AWS certification to cover the missing JD requirement.",
                        "Include a link to the live deployment of your capstone project."
                    ],
                    "fraud_detection": [],
                    "interview_questions": [
                        "Explain your experience containerizing React apps with Docker.",
                        "How would you approach learning AWS for our deployment pipeline?",
                        "Describe a time you optimized a Python backend for scale."
                    ]
                }
            },
            {
                "filename": "Jordan_Lee_Resume.pdf",
                "status": "SUCCESS",
                "dossier": {
                    "name": "Jordan Lee",
                    "emails": ["jordan.l@email.com"],
                    "phones": ["+1 555-0456"],
                    "gpa": "8.1 / 10.0"
                },
                "analytics": {
                    "final_score": 72.0,
                    "skills_found": ["Python", "Django", "SQL"],
                    "missing_skills": ["React", "Docker", "AWS"]
                },
                "premium_insights": {
                    "quality_score": 75,
                    "suggestions": [
                        "Your backend skills are strong, but you lack the required frontend framework.",
                        "Quantify your database optimization project.",
                        "Format your employment dates consistently."
                    ],
                    "fraud_detection": ["Employment gap detected between 2023 and 2024."],
                    "interview_questions": [
                        "You have Django experience. How quickly can you adapt to a React frontend?",
                        "Can you walk me through your SQL optimization techniques?",
                        "What was your primary focus during the gap year in 2023?"
                    ]
                }
            }
        ],
        "errors": []
    }

def get_gpa_float(gpa_str):
    """Extracts the numerical float from the GPA string."""
    match = re.search(r'(\d+(?:\.\d+)?)', gpa_str)
    return float(match.group(1)) if match else 0.0

def process_candidate(resume_file, jd_skills, clean_jd, weights, index):
    """
    Worker function executed in parallel for each resume.
    Includes a stagger to respect free-tier API rate limits.
    """
    # Create a unique temp file for thread safety
    temp_path = f"temp_{os.getpid()}_{index}_{resume_file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)

        # 1. Fast Local Processing (Tier 1)
        raw = extract_text_from_pdf(temp_path)
        clean = clean_raw_text(raw)
        
        if "ERROR" in clean:
            return {"filename": resume_file.filename, "status": "ERROR", "reason": "Unreadable PDF text"}

        metrics = extract_metrics(clean)
        gpa = get_gpa_float(metrics.get('GPA', '0.0'))
        contact_results = extract_contact_info(clean)
        ai_entities = extract_entities(clean)
        skills = ai_entities.get('Skills', [])
        
        # 2. Local Analytics
        exact_match, missing = analyze_skill_gap(skills, jd_skills)
        semantic = calculate_match_score(skills, clean_jd)
        
        # --- RATE LIMIT PROTECTION ---
        # Stagger the API calls by 2.5 seconds per thread.
        # This tricks the API into seeing sequential requests while the rest of the code runs in parallel.
        time.sleep(index * 2.5)
        
        # 3. Deep AI Analysis via Gemini (Tier 2)
        ai_feedback = generate_premium_analysis(skills, missing, clean)

        # 4. Apply Custom Dynamic Weights for Final Scoring
        w_gpa = weights.get('gpa', 0.3)
        w_tech = weights.get('tech', 0.5)
        w_sem = weights.get('semantic', 0.2)
        
        gpa_normalized = (gpa / 10.0) * 100
        final_score = round((gpa_normalized * w_gpa) + (exact_match * w_tech) + (semantic * w_sem), 2)

        return {
            "filename": resume_file.filename,
            "status": "SUCCESS",
            "dossier": {
                "name": ai_entities.get('Name'),
                "emails": contact_results.get('Emails', []),
                "phones": contact_results.get('Phones', []),
                "gpa": metrics.get('GPA')
            },
            "analytics": {
                "final_score": final_score,
                "skills_found": skills,
                "missing_skills": missing
            },
            "premium_insights": {
                "quality_score": ai_feedback.get('quality_score', 0),
                "suggestions": ai_feedback.get('improvements', []),
                "fraud_detection": ai_feedback.get('fraud_alerts', []),
                "interview_questions": ai_feedback.get('interview_questions', [])
            }
        }
    except Exception as e:
        return {"filename": resume_file.filename, "status": "ERROR", "reason": str(e)}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/analyze-bulk")
async def analyze_bulk(
    resumes: List[UploadFile] = File(...), 
    jd_pdf: UploadFile = File(...),
    w_gpa: float = Form(0.3),
    w_tech: float = Form(0.5),
    w_sem: float = Form(0.2),
    demo_mode: bool = Form(False)
):
    """
    Main endpoint accepting multiple PDFs and sorting them by rank.
    """
    # --- DEMO MODE INTERCEPT ---
    if demo_mode:
        import time
        time.sleep(2) # Fake a 2-second loading time so it doesn't look completely fake
        return get_demo_response()
    # ---------------------------
    
    if len(resumes) > 10:
        raise HTTPException(status_code=400, detail="Max 10 resumes per batch to prevent rate limits.")

    # Process Job Description Once
    jd_temp = "temp_jd.pdf"
    with open(jd_temp, "wb") as buffer:
        shutil.copyfileobj(jd_pdf.file, buffer)
    
    raw_jd = extract_text_from_pdf(jd_temp)
    clean_jd = clean_raw_text(raw_jd)
    jd_skills = extract_entities(clean_jd).get('Skills', [])
    os.remove(jd_temp)
    
    weights = {"gpa": w_gpa, "tech": w_tech, "semantic": w_sem}

    # Parallel Execution with Indexing for the Stagger Delay
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(resumes)) as executor:
        futures = [
            executor.submit(process_candidate, res, jd_skills, clean_jd, weights, index) 
            for index, res in enumerate(resumes)
        ]
        results = [f.result() for f in futures]

    # Ranking System: Filter successes and sort by final score descending
    successful_candidates = [r for r in results if r.get("status") == "SUCCESS"]
    errors = [r for r in results if r.get("status") == "ERROR"]
    
    sorted_candidates = sorted(successful_candidates, key=lambda x: x['analytics']['final_score'], reverse=True)

    return {
        "batch_info": {
            "total_processed": len(resumes),
            "successful": len(successful_candidates),
            "failed": len(errors)
        },
        "job_description_skills": jd_skills,
        "ranked_candidates": sorted_candidates,
        "errors": errors
    }

if __name__ == "__main__":
    print("Starting Premium Microservice on Port 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)