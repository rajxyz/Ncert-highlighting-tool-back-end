import re
import os
from pdf_parser import extract_text_from_chapter
from pyqs import get_pyq_matches

MAX_IMAGES = 5  # ✅ Limit number of images to OCR

# ✅ DEFAULT keyword-based pattern highlighter
def highlight_by_keywords(book, chapter):
    print(f"🔍 Pattern-based highlighting: {book} - {chapter}")

    # ✅ Limit images before extracting text
    folder_path = f"static/books/{book}/{chapter}"
    if not os.path.exists(folder_path):
        print("❌ Chapter folder not found")
        return []

    all_images = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])
    selected_images = all_images[:MAX_IMAGES]

    print(f"🖼️ Limiting to {len(selected_images)} image(s): {selected_images}")

    # ✅ Extract text only from selected images
    text = extract_text_from_chapter(book, chapter, selected_images)
    print(f"📄 Extracted text length: {len(text)}")

    highlights = []

    # Definitions
    def_patterns = [
        r'\b(is|are|was|means|refers to|is defined as)\b[^.]{10,100}\.',
        r'\bcan be defined as\b[^.]{10,100}\.',
    ]
    for pattern in def_patterns:
        highlights.extend(re.findall(pattern, text, flags=re.IGNORECASE))

    # Dates
    date_pattern = r'\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{2,4}\b'
    highlights.extend(re.findall(date_pattern, text))

    # Numbers + Units
    num_pattern = r'\b\d+(?:\.\d+)?\s?(?:kg|g|m|cm|km|s|ms|Hz|J|W|°C|%)\b'
    highlights.extend(re.findall(num_pattern, text))

    # Terminologies (Capitalized)
    term_pattern = r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b'
    highlights.extend(re.findall(term_pattern, text))

    # Examples
    ex_pattern = r'(?:for example|e\.g\.|such as)\s[^.]{5,100}'
    highlights.extend(re.findall(ex_pattern, text, flags=re.IGNORECASE))

    # Steps
    step_pattern = r'\b(Step \d+|Step-\d+|First,|Then,|Next,|Finally)\b[^.]{5,100}'
    highlights.extend(re.findall(step_pattern, text, flags=re.IGNORECASE))

    # Cause-Effect
    cause_pattern = r'\b(Because|Due to|As a result|Therefore|Hence)\b[^.]{5,100}'
    highlights.extend(re.findall(cause_pattern, text, flags=re.IGNORECASE))

    # Theories/Laws
    theory_pattern = r'\b(?:Law|Rule|Theory|Principle) of [A-Z][a-z]+\b'
    highlights.extend(re.findall(theory_pattern, text))

    # Acronyms
    acronym_pattern = r'\b[A-Z]{2,}\b'
    highlights.extend(re.findall(acronym_pattern, text))

    # Lists
    list_pattern = r'\n?\d+\.\s[^\n]+|\n?-\s[^\n]+'
    highlights.extend(re.findall(list_pattern, text))

    # Foreign-looking scientific terms
    foreign_pattern = r'\b[A-Za-z]+(?:us|um|ae|es|is|on)\b'
    highlights.extend(re.findall(foreign_pattern, text))

    cleaned = list(set(map(lambda x: x.strip().strip(','), highlights)))
    print(f"✨ Found {len(cleaned)} keyword-based highlights.")
    return cleaned
