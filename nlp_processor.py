import spacy
from spacy.pipeline import EntityRuler

#load the base english model
nlp=spacy.load("en_core_web_sm")

#1 initialize the EntityRuler and add it to the spaCy pipeline BEFORE the default NER
#this ensures our hardcoded rules override the AI's guesses
ruler=nlp.add_pipe("entity_ruler",before="ner")

#2 build the hardcoded knowledge base
#in a real enterprise app, this would be a database of 10,000+ skills
#we are starting with a core subset to prove the architecture
tech_skills = ["C", "C++", "JavaScript", "HTML5", "CSS3", "Bootstrap", "Bootstrap 5", 
               "DOM Manipulation", "Fetch API", "Data Structures", "Algorithms", 
               "OOP", "Database Management", "Machine Learning", "Python", "SQL"]
# 3. Create the pattern matching rules
patterns=[]
for skill in tech_skills:
    # We split the skill string by spaces.
    # "Machine Learning" becomes -> [{"LOWER": "machine"}, {"LOWER": "learning"}]
    tokenized_pattern = [{"LOWER": word.lower()} for word in skill.split()]
    patterns.append({"label": "SKILL", "pattern": tokenized_pattern})
ruler.add_patterns(patterns)

def extract_entities(clean_text):
    """
    Passes text through the custom-tuned NLP engine and uses defensive heuristics for names.
    """
    doc = nlp(clean_text)
    
    # Split by the now-preserved line breaks
    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
    
    candidate_name = "Name Not Found"
    
    # Iterate through the first 5 lines to find the actual name
    for line in lines[:5]:
        # Ignore PDF metadata or generic headers
        if "PAGE" not in line.upper() and "RESUME" not in line.upper() and len(line) > 2:
            candidate_name = line
            break  # The moment we find a valid line, lock it in and stop looping
    
    extracted_data = {
        "Name": candidate_name, 
        "Organizations": [],
        "Skills": []
    }
    
    #Iterate through all the entities the AI found
    for ent in doc.ents:

        if ent.label_=="SKILL" :
            if ent.text not in extracted_data["Skills"]:
            #we grab the first person name we see , assuming its the resume owner 
                extracted_data["Skills"].append(ent.text)

        #ORG is spaCy's tag for companies schools etc
        elif ent.label_=="ORG":
                # Add to our list, but avoid duplicates
            if ent.text not in extracted_data["Organizations"]:
                extracted_data["Organizations"].append(ent.text)
                
    return extracted_data