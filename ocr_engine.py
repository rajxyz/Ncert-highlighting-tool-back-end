from PIL import Image
import pytesseract
import os

# ✅ Handle Pillow 10.0+ deprecation of Image.ANTIALIAS
try:
    RESAMPLE = Image.Resampling.LANCZOS  # PIL >= 10.0
except AttributeError:
    RESAMPLE = Image.ANTIALIAS  # PIL < 10.0

def extract_text_from_image(image_path, lang='eng'):
    """
    Extracts text from an image using Tesseract OCR with enhanced logging and error handling.
    
    Args:
        image_path (str): Path to the image.
        lang (str): Language code for OCR (default is 'eng').

    Returns:
        str: Extracted text from the image.
    """
    try:
        print(f"🔍 OCR START: {image_path}")

        # Check if file exists
        if not os.path.exists(image_path):
            print(f"❌ File not found: {image_path}")
            return ""

        image = Image.open(image_path)

        # Optional: Resize image if needed (uncomment below if required)
        # image = image.resize((image.width * 2, image.height * 2), RESAMPLE)

        print(f"📐 Image size: {image.size}")
        print(f"🔤 OCR language: {lang}")

        # Tesseract configuration (can be tuned)
        config = '--psm 6'  # Assume a single uniform block of text
        text = pytesseract.image_to_string(image, lang=lang, config=config)

        # Log preview of extracted text
        preview = "\n".join(text.strip().splitlines()[:5])
        print(f"📄 OCR Preview:\n{preview}\n--- END PREVIEW ---")

        return text.strip()

    except Exception as e:
        print(f"❌ OCR failed for {image_path}: {e}")
        return ""
