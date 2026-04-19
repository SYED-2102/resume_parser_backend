import os
import json
# from google import genai  # Corrected Import
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key securely
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
print("Gemini API Key:", API_KEY)

# Initialize the new SDK client correctly
# client = genai.Client(api_key=API_KEY)
genai.configure(api_key=API_KEY)

def generate_premium_analysis(candidate_skills, missing_skills, resume_text):
    """
    Handles Quality Analysis, Suggestions, Fraud Detection, and Interview Questions.
    Returns a strict JSON object.
    """
    model_id = "gemini-2.5-flash" 
    
    prompt = f"""
    Analyze this resume for a Senior Recruiter:
    Text: {resume_text[:4000]} 
    Extracted Skills: {candidate_skills}
    Missing from Job Description: {missing_skills}

    Return ONLY a JSON object with exactly these keys. Do not use markdown.
    {{
        "quality_score": 85, 
        "improvements": ["Add GitHub links", "Quantify project metrics", "Include Docker"],
        "fraud_alerts": ["Gap in employment dates", "Keyword stuffing detected"], 
        "interview_questions": ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
    }}
    
    Note: For 'fraud_alerts', leave the array empty if no red flags are found.
    """

    try:
        # response = client.models.generate_content(model=model_id, contents=prompt)
        model = genai.GenerativeModel(model_id)
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Safe fallback if the AI hallucinations break the JSON parse
        return {
            "quality_score": 50,
            "improvements": ["Failed to generate AI suggestions. Check API."],
            "fraud_alerts": ["AI check failed."],
            "interview_questions": ["Standard technical interview required."]
        }