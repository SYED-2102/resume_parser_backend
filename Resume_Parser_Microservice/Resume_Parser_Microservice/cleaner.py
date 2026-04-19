import re

def clean_raw_text(raw_text):
    """
    Santizes raw extracted resume text for NLP processing
    """
    if raw_text.startswith("ERROR") or raw_text.startswith("CRITICAL ERROR"):
        return raw_text
    
    #1 strip non ASCII characters
    #this reges looks for anything that is not standard text and replacess it with a space
    text=re.sub(r'[^\x00-\x7F]+',' ',raw_text)
    
    # 2. Replace multiple consecutive newlines (\n\n\n) with a single newline
    text = re.sub(r'\n+', '\n', text)
    
    # 3. Replace multiple horizontal spaces/tabs with a single space (Preserves \n)
    text = re.sub(r'[ \t]+', ' ', text)

    #4 remove leading and trailing white spaces
    return text.strip()