import fitz

def extract_text(pdf_path, max_chars=2000):
    """
    Extracts up to `max_chars` characters from a PDF.

    Args:
        pdf_path (str): Path to the PDF file.
        max_chars (int): Max number of characters to return.

    Returns:
        str: Extracted text (plain string).
        
    Raises:
        FileNotFoundError: If file is missing.
        RuntimeError: If PDF cannot be parsed.
    """

    doc = fitz.open(pdf_path)
    
    text = ""

    for page in doc:
        text += page.get_text()
        if len(text) >= max_chars:
            break
    doc.close()

    return text[:max_chars]