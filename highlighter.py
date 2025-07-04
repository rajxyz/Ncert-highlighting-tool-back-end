import os
from ocr_engine import extract_text_from_image
from matcher import match_lines
import json

# Load highlightable keywords (e.g., dates, definitions, facts, etc.)
with open("highlights_data.json", "r", encoding="utf-8") as f:
    highlight_keywords = json.load(f)  # Expects dict: { "11th": { "Chapter 1": ["keyword1", "keyword2", ...] }, ... }

def get_highlight_lines(book, chapter):
    folder_path = os.path.join("static", "books", book, chapter)
    print(f"📂 Scanning folder for OCR: {folder_path}")
    
    if not os.path.exists(folder_path):
        return []

    lines = []

    # Read and OCR each image file in the folder
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, file_name)
            print(f"🖼️ OCR processing: {image_path}")
            try:
                text = extract_text_from_image(image_path)
                lines.extend(text.splitlines())
            except Exception as e:
                print(f"❌ OCR failed on {file_name}: {e}")

    # Remove empty or whitespace-only lines
    lines = [line.strip() for line in lines if line.strip()]

    # Get chapter-specific keywords
    chapter_keywords = highlight_keywords.get(book, {}).get(chapter, [])
    print(f"🧠 Matching {len(lines)} lines against {len(chapter_keywords)} keywords...")

    # Find matching lines
    matches = match_lines(lines, chapter_keywords)
    print(f"✅ Found {len(matches)} highlighted lines.")
    
    return matches
