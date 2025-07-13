import re
import os
from pdf_parser import extract_text_from_chapter

MAX_IMAGES = 5  # ✅ Limit number of images to OCR


# ✅ Extract & detect highlights from image text using regex
def highlight_by_keywords(book, chapter):
    book = book.strip()
    chapter = chapter.strip()
    print(f"🔍 Pattern-based highlighting: {book} - {chapter}")

    folder_path = os.path.join("static", "books", book, chapter)
    if not os.path.isdir(folder_path):
        print("❌ Chapter folder not found or is not a directory")
        return []

    try:
        all_images = sorted([
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])
    except Exception as e:
        print(f"❌ Error reading image files: {e}")
        return []

    selected_images = all_images[:MAX_IMAGES]
    print(f"🖼️ Using image(s): {selected_images}")

    # Extract OCR text
    text = extract_text_from_chapter(book, chapter, selected_images)
    print(f"📄 Extracted text length: {len(text)}")

    if not text.strip():
        return []

    highlights = []

    # Define regex rules
    rules = {
        "definition": [
            r'\b(?:is|are|was|means|refers to|is defined as|can be defined as)\b[^.]{10,150}\.',
        ],
        "date": [
            r'\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{2,4}\b'
        ],
        "units": [
            r'\b\d+(?:\.\d+)?\s?(?:kg|g|m|cm|km|s|ms|Hz|J|W|°C|%)\b'
        ],
        "capitalized_terms": [
            r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b'
        ],
        "example": [
            r'(?:for example|e\.g\.|such as)\s[^.]{5,100}'
        ],
        "steps": [
            r'\b(?:Step \d+|Step-\d+|First,|Then,|Next,|Finally)\b[^.]{5,100}'
        ],
        "cause_effect": [
            r'\b(?:Because|Due to|As a result|Therefore|Hence)\b[^.]{5,100}'
        ],
        "theories": [
            r'\b(?:Law|Rule|Theory|Principle) of [A-Z][a-z]+\b'
        ],
        "acronyms": [
            r'\b[A-Z]{2,}(?:\s[A-Z]{2,})?\b'
        ],
        "list_items": [
            r'(?:^|\n)\d+\.\s[^\n]+',
            r'(?:^|\n)-\s[^\n]+'
        ],
        "foreign_words": [
            r'\b[A-Za-z]+(?:us|um|ae|es|is|on)\b'
        ]
    }

    # Apply each regex and collect matches
    for category, patterns in rules.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
            print(f"🔎 {category}: {len(matches)} found")
            highlights.extend(matches)

    # Clean and deduplicate
    cleaned = list(set(h.strip(" .,\n") for h in highlights if len(h.strip()) > 2))
    print(f"✨ Total unique highlights: {len(cleaned)}")
    return cleaned


# ✅ Wrapper for API response
def detect_highlights(book, chapter):
    print(f"\n🚀 Running detect_highlights for {book}/{chapter}")
    raw = highlight_by_keywords(book, chapter)

    results = [
        {
            "text": h,
            "start": None,
            "end": None,
            "category": "auto"
        } for h in raw
    ]

    print(f"📬 Returning {len(results)} highlights.")
    return results
