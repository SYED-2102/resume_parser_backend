import pypdfium2 as pdfium

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Handles PDF extraction using a context manager to avoid 
    Windows file-locking (PermissionError) and null-pointer crashes.
    """
    text = ""
    try:
        # The 'with' block ensures the file handle is closed automatically
        with pdfium.PdfDocument(pdf_path) as pdf:
            for i in range(len(pdf)):
                page = pdf.get_page(i)
                text_page = page.get_textpage()
                text += text_page.get_text_range() + "\n"
    except Exception as e:
        print(f"🚨 Extraction Error: {e}")
    
    return text