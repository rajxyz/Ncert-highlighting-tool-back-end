from PIL import Image
import pytesseract
import os
import re

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.ANTIALIAS

def clean_ocr_text(text):
    """
    Removes common HTML or code-like junk from OCR output.
    """
    junk_keywords = [
        "html", "head", "body", "div", "class", "span", "style", "script",
        "lang", "href", "meta", "link", "content", "doctype", "{", "}", "</", "<"
    ]

    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        lower_line = line.lower()

        # Skip junk lines
        if any(lower_line.startswith(j) for j in junk_keywords):
            continue
        if re.search(r'<[^>]+>', lower_line):  # Skip HTML tags
            continue
        if len(line) <= 2:
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def extract_text_from_image(image_path, lang='eng'):
    try:
        print(f"🔍 OCR START: {image_path}")

        if not os.path.exists(image_path):
            print(f"❌ File not found: {image_path}")
            return ""

        image = Image.open(image_path)

        print(f"📐 Image size: {image.size}")
        print(f"🔤 OCR language: {lang}")

        config = '--psm 6'
        text = pytesseract.image_to_string(image, lang=lang, config=config)

        # Clean junk HTML or code-like content
        cleaned_text = clean_ocr_text(text)

        preview = "\n".join(cleaned_text.strip().splitlines()[:5])
        print(f"📄 Cleaned OCR Preview:\n{preview}\n--- END PREVIEW ---")

        return cleaned_text.strip()

    except Exception as e:
        print(f"❌ OCR failed for {image_path}: {e}")
        return ""







