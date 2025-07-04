def extract_text_from_image(image_path, lang='eng'):
    """
    Extracts text from an image using Tesseract OCR.
    
    Args:
        image_path (str): Path to the image.
        lang (str): Language code for OCR (default is 'eng').

    Returns:
        str: Extracted text from the image.
    """
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image, lang=lang)
    except Exception as e:
        print(f"❌ OCR failed for {image_path}: {e}")
        return ""
