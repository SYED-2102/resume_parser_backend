from extractor import extract_text_from_pdf
from cleaner import clean_raw_text
from nlp_processor import extract_entities
from contact_extractor import extract_contact_info
from metrics_extractor import extract_metrics
from semantic_engine import calculate_match_score
from gap_analyzer import analyze_skill_gap
from interview_bot import generate_interview_questions
# 1. Download a sample PDF resume from the internet.
# 2. Rename it to 'sample.pdf' and place it in this exact folder.
resume_file = "sample.pdf"
jd_file = "jd.pdf"

import re

def get_gpa_float(gpa_str):
    """Extracts the numerical float from the GPA string."""
    match = re.search(r'(\d+(\.\d+)?)', gpa_str)
    return float(match.group(1)) if match else 0.0

print("=========================================")
print("  NEXT-GEN RECRUITMENT AI SYSTEM V1.0    ")
print("=========================================\n")

# --- 1. RESUME PARSING PIPELINE ---
print("[*] Parsing Candidate Resume...")
raw_resume = extract_text_from_pdf(resume_file)
clean_resume = clean_raw_text(raw_resume)

ai_results = extract_entities(clean_resume)
contact_results = extract_contact_info(clean_resume)
metrics_results = extract_metrics(clean_resume)
candidate_skills = ai_results.get('Skills', [])

# --- 2. JOB DESCRIPTION PARSING PIPELINE ---
print("[*] Parsing Job Description PDF...")
# Reusing your exact same architecture for the JD!
raw_jd = extract_text_from_pdf(jd_file)
clean_jd = clean_raw_text(raw_jd)

jd_ai_results = extract_entities(clean_jd)
jd_required_skills = jd_ai_results.get('Skills', [])

# --- 3. ANALYTICS & SCORING ---
print("[*] Calculating AI Placement Analytics...")

# A. HARD FILTER: Minimum GPA Cutoff
MIN_CGPA = 8.0
candidate_gpa = get_gpa_float(metrics_results.get('GPA', '0.0'))

if candidate_gpa < MIN_CGPA:
    print(f"\n[-] AUTO-REJECT: Candidate GPA ({candidate_gpa}) is below the required {MIN_CGPA}.")
    print("[-] Pipeline halted to save compute resources.")
    exit() # Terminates the script immediately. No Gemini API costs incurred.

# B. DATA EXTRACTION
exact_score, missing_tech = analyze_skill_gap(candidate_skills, jd_required_skills)
semantic_score = calculate_match_score(candidate_skills, clean_jd)

# C. CUSTOM WEIGHTED SCORING ALGORITHM
# 1. Normalize GPA to a 100-point scale (Assuming out of 10.0)
gpa_score = (candidate_gpa / 10.0) * 100

# 2. Priority Skill Check (e.g., DSA)
# If they have Data Structures and Algorithms, they get a 100 for this category.
priority_skills = ["Data Structures", "Algorithms"]
has_priority = all(skill.lower() in [s.lower() for s in candidate_skills] for skill in priority_skills)
priority_score = 100 if has_priority else 0

# 3. Apply Weights (Must equal 1.0 total)
# GPA = 30%, General Tech Match = 40%, Priority Skills = 20%, Semantic = 10%
hybrid_score = round(
    (gpa_score * 0.30) + 
    (exact_score * 0.40) + 
    (priority_score * 0.20) + 
    (semantic_score * 0.10), 
2)

# --- 4. MOCK INTERVIEW GENERATION ---
interview_output = generate_interview_questions(candidate_skills, missing_tech)

# --- FINAL SYSTEM OUTPUT ---
print("\n=========================================")
print("          CANDIDATE DOSSIER              ")
print("=========================================")
print(f"Name:    {ai_results.get('Name')}")
print(f"Email:   {contact_results['Emails']}")
print(f"Phone:   {contact_results['Phones']}")
print(f"Status:  {metrics_results['Status']} (Class of {metrics_results['Graduation_Year']})")
print(f"GPA:     {metrics_results['GPA']}")
print("\n--- SKILL GAP ANALYSIS ---")
print(f"Candidate Stack: {candidate_skills}")
print(f"Missing Tech:    {missing_tech}")
print(f"MATCH SCORE:     {hybrid_score}%")
print("\n--- GENERATED MOCK INTERVIEW ---")
print(interview_output)
print("=========================================")