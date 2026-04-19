import re

def extract_contact_info(clean_text):
    """
    for 100% accuracy on structured data, bypasses NLP engine entirely 
    """
    #1.email extraction
    # Logic: Look for alphanumeric characters -> an @ symbol -> a domain -> a .com/.org suffix
    email_pattern=r'[a-zA-A0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found_emails = re.findall(email_pattern, clean_text)

    # 2. Phone Number Extraction
    # Logic: Looks for 10 consecutive digits, or numbers separated by dashes/spaces/parentheses
    #phone_pattern = r'(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    # Aggressive international phone number extraction
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    found_phones = re.findall(phone_pattern, clean_text)
    # Clean up the extracted phones (remove trailing spaces if any)
    cleaned_phones = [phone.strip() for phone in found_phones]

    
    # We use list(set(...)) to automatically remove any duplicate emails or phones it finds
    return {
        "Emails": list(set(found_emails)),
        "Phones": list(set(found_phones))
    }