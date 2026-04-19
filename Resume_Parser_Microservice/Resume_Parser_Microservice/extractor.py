import pdfplumber

def extract_text_from_pdf(pdf_path):
    """
    Ingests a PDF file and returns the extracted raw text.
    Designed to be imported by the main backend server.
    """
    extracted_text = ""
    
    try:
        # The 'with' context manager ensures the file is safely closed after reading,
        # preventing memory leaks on the server.
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                # Some pages might be images or blank, so we check if text exists
                if text:
                    extracted_text += text + "\n"
                    
        if not extracted_text.strip():
            return "ERROR: No readable text found. The PDF might be image-based."
            
        return extracted_text.strip()
        
    except FileNotFoundError:
        return f"ERROR: The file at {pdf_path} was not found."
    except Exception as e:
        return f"CRITICAL ERROR: {str(e)}"