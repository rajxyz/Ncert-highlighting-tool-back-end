from ocr_engine import extract_text_from_image
from matcher.py import find_matches  # you may already have this

def auto_highlight(image_path):
    # 1. OCR se text nikalo
    extracted_text = extract_text_from_image(image_path)
    
    # 2. Matcher se keywords (e.g., dates, names, facts) dhoondo
    matches = find_matches(extracted_text)

    # 3. Return result
    return {
        "text": extracted_text,
        "highlights": matches
    }
