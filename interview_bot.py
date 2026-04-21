import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_premium_analysis(skills, missing_skills, resume_text):
    """
    Calls Groq (Llama 3.3 70B) using strict JSON Mode to generate insights.
    """
    system_prompt = "You are a JSON-only API. You must return a valid JSON object."
    
    prompt = f"""
    You are an expert technical recruiter and system architect.
    Analyze the following candidate's resume against the missing skills for the job.

    Candidate Skills Found: {skills}
    Missing Skills from JD: {missing_skills}
    Resume Text: {resume_text}

    Provide your analysis strictly in the following JSON format.
    {{
        "quality_score": "REPLACE_WITH_CALCULATED_INTEGER", 
        "suggestions": ["actionable feedback 1", "actionable feedback 2", "actionable feedback 3"],
        "fraud_alerts": [],
        "interview_questions": ["question 1", "question 2", "question 3"]
    }}

    CRITICAL RULES:
    1. Output ONLY valid JSON.
    2. The "suggestions" array MUST contain exactly 3 actionable improvements.
    3. The "interview_questions" array MUST contain exactly 3 to 5 technical questions.
    4. Every single question MUST be strictly 20 words or less. Be concise.
    5. The "quality_score" MUST NOT be copied from the template. You must dynamically calculate an integer between 1 and 100 representing the candidate's actual technical fit for the role based on the missing skills.
    6. The "quality_score" MUST be returned as a raw JSON integer, NOT a string. You must replace the placeholder text with your calculated integer between 1 and 100.
    """


    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1, 
            response_format={"type": "json_object"} 
        )
        
        raw_response = chat_completion.choices[0].message.content
        return json.loads(raw_response)
            
    except Exception as e:
        print(f"⚠️ Groq Architecture Error: {e}")
        return {
            "quality_score": 50,
            "suggestions": ["Failed to parse AI response. Check backend logs."],
            "fraud_alerts": [],
            "interview_questions": ["Standard technical interview required."]
        }

def extract_jd_metrics_via_llm(jd_text: str) -> float:
    """
    Delegates the extraction of the GPA threshold to Llama 3.3.
    It understands context and ignores PDF parsing corruption.
    """
    prompt = f"""
    You are an intelligent data extractor. 
    Read the following Job Description text. It may contain corrupted formatting (e.g., '$8.5/10$').
    Identify the minimum CGPA or GPA requirement. 

    Text: {jd_text} 

    Return ONLY a valid JSON object in this exact format. If no GPA is found, default to 7.0.
    {{
        "minimum_gpa": 8.5
    }}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a JSON-only API."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0, 
            response_format={"type": "json_object"}
        )
        
        result = json.loads(chat_completion.choices[0].message.content)
        val = float(result.get("minimum_gpa", 7.0))
        
        if 1.0 <= val <= 10.0:
            return val
        return 7.0
        
    except Exception as e:
        print(f"JD Extraction Error: {e}")
        return 7.0