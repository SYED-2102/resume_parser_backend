def analyze_skill_gap(resume_skills,jd_skills):
    """
    uses python set  theory to calculate exact missing technologies
    and output a deterministic hard-match percentage.
    """
    #convert both lists to lowercase sets to ensure ccase insensitive math
    resume_set=set([s.lower() for s in resume_skills])
    jd_set=set([s.lower() for s in jd_skills])

    #set subtraction: JD skills minus resume Skills=Missing Skills
    missing_skills_lower=jd_set-resume_set

    #calculate the deterministic match percentage
    if len(jd_set)==0:
        return 100.0,[] # If the JD requires no specific tech, it's a 100% match
    
    exact_match_score=((len(jd_set)-len(missing_skills_lower))/len(jd_set))*100

    #map the lowercase missing skills back to their orighinal formating for the UI
    missing_formatted=[skill for skill in jd_skills if skill.lower()in missing_skills_lower]

    return round(exact_match_score,2),missing_formatted
