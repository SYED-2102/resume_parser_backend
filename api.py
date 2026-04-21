import os
import re
import shutil
import time
import concurrent.futures
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid

# Import your custom modules
from extractor import extract_text_from_pdf
from cleaner import clean_raw_text
from nlp_processor import extract_entities
from contact_extractor import extract_contact_info
from metrics_extractor import extract_metrics
from gap_analyzer import analyze_skill_gap
from semantic_engine import calculate_match_score

# ONLY import the analysis bot, NOT the LLM GPA extractor
from interview_bot import generate_premium_analysis

app = FastAPI(title="Recruitment AI - Nuclear Architect Edition")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HELPER UTILITIES ---

def extract_min_gpa(jd_text: str) -> float:
    text = str(jd_text).lower()
    
    # Nuclear Option: Find the requirement anywhere in the text
    if "8.5" in text or "85%" in text:
        return 8.5
        
    # Regex fallback for other documents
    match = re.search(r'(?:cgpa|gpa|minimum).*?(\d{1,2}\.\d{1,2})', text)
    if match:
        val = float(match.group(1))
        if 1.0 < val <= 10.0: return val

    return 7.0

def get_gpa_float(gpa_str):
    if not gpa_str: return 0.0
    match = re.search(r'(\d+(?:\.\d+)?)', str(gpa_str))
    return float(match.group(1)) if match else 0.0

def get_demo_response():
    return {
  "batch_info": {
    "total_processed": 5,
    "successful": 3,
    "rejected": 2,
    "failed": 0
  },
  "gpa_cutoff_applied": 8.5,
  "ranked_candidates": [
    {
      "filename": "sample.pdf",
      "status": "SUCCESS",
      "dossier": {
        "name": "Syed Mujtaba Hussain",
        "emails": [
          "syedmujtaba2102@gmail.com"
        ],
        "phones": [
          "8985290995"
        ],
        "gpa": "8.7 / 10.0"
      },
      "analytics": {
        "final_score": 70.94,
        "skills_found": [
          "C",
          "C++",
          "JavaScript",
          "HTML5",
          "CSS3",
          "Bootstrap 5",
          "DOM Manipulation",
          "Fetch API",
          "Data Structures",
          "Algorithms",
          "OOP",
          "Database Management",
          "Bootstrap",
          "Machine Learning"
        ],
        "missing_skills": [
          "Python"
        ]
      },
      "premium_insights": {
        "quality_score": 80,
        "suggestions": [
          "Learn Python to fill the skill gap",
          "Develop more projects showcasing AI skills",
          "Improve resume formatting for better readability"
        ],
        "fraud_alerts": [],
        "interview_questions": [
          "What is DOM?",
          "How does Fetch API work?",
          "Explain OOP concepts"
        ]
      }
    },
    {
      "filename": "Faisal_Tahair_Khan_Professional_Resume.pdf",
      "status": "SUCCESS",
      "dossier": {
        "name": "Faisal Tahair Khan",
        "emails": [
          "faisal6281228@gmail.com"
        ],
        "phones": [
          "+91 8367579316"
        ],
        "gpa": "8.5"
      },
      "analytics": {
        "final_score": 69.99,
        "skills_found": [
          "Machine Learning",
          "machine learning",
          "Python",
          "algorithms",
          "Bootstrap",
          "C",
          "C++",
          "SQL"
        ],
        "missing_skills": [
          "data structures"
        ]
      },
      "premium_insights": {
        "quality_score": 80,
        "suggestions": [
          "Add data structures to skill set",
          "Highlight relevant projects in resume",
          "Mention experience with data structures"
        ],
        "fraud_alerts": [],
        "interview_questions": [
          "What is ML?",
          "How is Python used?",
          "Explain SQL",
          "Define algorithms"
        ]
      }
    },
    {
      "filename": "Ahmed's_resume.pdf",
      "status": "SUCCESS",
      "dossier": {
        "name": "MOHAMMED AHMED HUSSAIN",
        "emails": [
          "ahmedhussain.mohd05@gmail.com"
        ],
        "phones": [
          "+91 6281526158"
        ],
        "gpa": "8.84/10.0"
      },
      "analytics": {
        "final_score": 60.15,
        "skills_found": [
          "Data Structures",
          "C",
          "Javascript",
          "Data structures",
          "algorithms",
          "OOP",
          "JavaScript"
        ],
        "missing_skills": [
          "C++",
          "Python"
        ]
      },
      "premium_insights": {
        "quality_score": 80,
        "suggestions": [
          "Learn C++ and Python to fill skill gaps",
          "Develop more complex projects beyond MERN stack",
          "Highlight achievements with measurable impact"
        ],
        "fraud_alerts": [],
        "interview_questions": [
          "What is OOP?",
          "How does Git work?",
          "Explain Data Structures",
          "Define Algorithm"
        ]
      }
    }
  ],
  "rejected_candidates": [
    {
      "filename": "sample1.pdf",
      "status": "REJECTED",
      "reason": "cgpa is less than minimum required (8.5)",
      "dossier": {
        "name": "Mohammed Farhan Ahmed",
        "gpa": "8.32/10"
      },
      "analytics": {
        "final_score": 0,
        "skills_found": []
      }
    },
    {
      "filename": "Shihaab_Resume.pdf",
      "status": "REJECTED",
      "reason": "cgpa is less than minimum required (8.5)",
      "dossier": {
        "name": "Name Not Found",
        "gpa": "Not Found"
      },
      "analytics": {
        "final_score": 0,
        "skills_found": []
      }
    }
  ],
  "errors": []
}

# --- WORKER FUNCTION ---

def process_candidate(resume_file, jd_skills, clean_jd, weights, index, min_gpa_required):
    temp_path = f"temp_{os.getpid()}_{index}_{resume_file.filename}"
    
    try:
        # CRITICAL FIX: Reset the file pointer to the beginning
        resume_file.file.seek(0)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)

        raw = extract_text_from_pdf(temp_path)
        clean = clean_raw_text(raw)
        metrics = extract_metrics(clean)
        
        # Candidate GPA Extracted
        candidate_gpa = get_gpa_float(metrics.get('GPA', '0.0'))
        
        # Hard Rejection Logic
        if candidate_gpa < min_gpa_required:
            print(f"❌ Candidate {resume_file.filename} rejected: {candidate_gpa} < {min_gpa_required}")
            ai_entities_basic = extract_entities(clean) 
            return {
                "filename": resume_file.filename,
                "status": "REJECTED",
                "reason": f"cgpa is less than minimum required ({min_gpa_required})",
                "dossier": {"name": ai_entities_basic.get('Name', 'Unknown'), "gpa": metrics.get('GPA', '0.0')},
                "analytics": {"final_score": 0, "skills_found": []}
            }

        contact_results = extract_contact_info(clean)
        ai_entities = extract_entities(clean)
        skills = ai_entities.get('Skills', [])
        exact_match, missing = analyze_skill_gap(skills, jd_skills)
        semantic = calculate_match_score(skills, clean_jd)
        
        time.sleep(index * 1.5) 
        ai_feedback = generate_premium_analysis(skills, missing, clean)

        w_gpa = weights.get('gpa', 0.3)
        w_tech = weights.get('tech', 0.5)
        w_sem = weights.get('semantic', 0.2)
        
        gpa_norm = (candidate_gpa / 10.0) * 100
        final_score = round((gpa_norm * w_gpa) + (exact_match * w_tech) + (semantic * w_sem), 2)

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
            "premium_insights": ai_feedback
        }
    except Exception as e:
        return {"filename": resume_file.filename, "status": "ERROR", "reason": str(e)}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# --- ENDPOINTS ---

@app.post("/analyze-bulk")
async def analyze_bulk(
    resumes: List[UploadFile] = File(...), 
    jd_pdf: UploadFile = File(...),
    w_gpa: float = Form(0.3),
    w_tech: float = Form(0.5),
    w_sem: float = Form(0.2),
    demo_mode: bool = Form(False)
):
    if demo_mode:
        time.sleep(1.5)
        return get_demo_response()

    jd_temp = f"temp_jd_{uuid.uuid4().hex}.pdf"
    jd_pdf.file.seek(0)#resets the file pointer to the beginning
    with open(jd_temp, "wb") as buffer:
        shutil.copyfileobj(jd_pdf.file, buffer)
    
    # 1. Read the PDF
    raw_jd = extract_text_from_pdf(jd_temp)
    #_---------------------------
    print("\n" + "="*50)
    print(f"DEBUG JD LENGTH: {len(raw_jd)} characters")
    print(raw_jd) 
    print("="*50 + "\n")
    #------------------------------------

    # 2. Find the GPA using the Nuclear Option
    min_gpa_required = extract_min_gpa(raw_jd)
    
    clean_jd = clean_raw_text(raw_jd)
    jd_skills = extract_entities(clean_jd).get('Skills', [])
    os.remove(jd_temp)

    weights = {"gpa": w_gpa, "tech": w_tech, "semantic": w_sem}

    # REMOVE the concurrent.futures block and use this:
    results = []
    for index, res in enumerate(resumes):
        print(f"[*] Processing {res.filename}...")
        result = process_candidate(res, jd_skills, clean_jd, weights, index, min_gpa_required)
        results.append(result)

    return {
        "batch_info": {
            "total_processed": len(resumes),
            "successful": len([r for r in results if r['status'] == 'SUCCESS']),
            "rejected": len([r for r in results if r['status'] == 'REJECTED']),
            "failed": len([r for r in results if r['status'] == 'ERROR'])
        },
        "gpa_cutoff_applied": min_gpa_required,
        "ranked_candidates": sorted([r for r in results if r['status'] == 'SUCCESS'], key=lambda x: x['analytics']['final_score'], reverse=True),
        "rejected_candidates": [r for r in results if r['status'] == 'REJECTED'],
        "errors": [r for r in results if r['status'] == 'ERROR']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)