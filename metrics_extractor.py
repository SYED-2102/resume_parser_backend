import re
from datetime import datetime

def extract_metrics(clean_text):
    """
    uses strict regex 
    """
    metrics={
        "GPA":"Not Found",
        "Graduation_Year":"Not Found",
        "Status":"Unknown"
    }

    #1 gpa extraction
    #logic :look for "GPA" or "CGPA" ,followed by optional spaces/colons,
    #then a decimal nummber 
    #gpa_pattern = r'(?:GPA|CGPA)[\s:]*([0-9](?:\.[0-9]{1,2})?(?:\s*/\s*[0-9](?:\.[0-9]{1,2})?)?)'
    gpa_pattern= r'(?:GPA|CGPA)[\s:]*(\d+(?:\.\d{1,2})?(?:\s*/\s*\d+(?:\.\d{1,2})?)?)'
    gpa_matches=re.findall(gpa_pattern,clean_text,re.IGNORECASE)

    if gpa_matches:
        #grab first match found and clean off the trailing spaces
        metrics["GPA"]=gpa_matches[0].strip()

    #2 graduation year extraction
    #look for exactly 4 digits starting with 20
    year_pattern=r'(20\d{2})' 
    year_matches=re.findall(year_pattern,clean_text)

    if year_matches:
        #convert found strings into actual integers
        years=[int(y) for y in year_matches]

        #the highest year mentioned on a resume is almost always the graduation year
        highest_year=max(years)
        metrics["Graduation_Year"]=str(highest_year)

        # 3. Calculate Academic Status
        current_year = datetime.now().year
        if highest_year > current_year:
            metrics["Status"] = "Current Student"
        else:
            metrics["Status"] = "Graduated / Alumni"
            
    return metrics