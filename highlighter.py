import re
import os

MAX_IMAGES = 5  # ✅ Limit number of pages to scan

# ✅ Extract & detect highlights from pre-extracted text files
def highlight_by_keywords(book, chapter):
    book = book.strip()
    chapter = chapter.strip()
    print(f"\n🔍 Pattern-based highlighting: {book} - {chapter}")

    folder_path = os.path.join("static", "books", book, chapter)
    if not os.path.isdir(folder_path):
        print(f"❌ Chapter folder not found: {folder_path}")
        return []

    try:
        all_images = sorted([
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])
    except Exception as e:
        print(f"❌ Error reading image files: {e}")
        return []

    if not all_images:
        print(f"⚠️ No image files found in: {folder_path}")
        return []

    selected_images = all_images[:MAX_IMAGES]
    print(f"🖼️ Using image(s): {selected_images}")

    # ✅ Use corresponding .txt files instead of OCR
    text = ""
    for img in selected_images:
        txt_file = os.path.splitext(img)[0] + ".txt"
        txt_path = os.path.join(folder_path, txt_file)
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                page_text = f.read()
                print(f"📃 Text from {txt_file}: {len(page_text)} chars")
                text += page_text + "\n"
        else:
            print(f"⚠️ Missing text file for: {img}")

    total_text_length = len(text.strip())
    print(f"📄 Total extracted text length: {total_text_length}")
    if not total_text_length:
        print("❌ No text extracted. Exiting.")
        return []

    highlights = []

    # ✅ Define regex rules
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

    print("📊 Starting regex pattern matching...")
    for category, patterns in rules.items():
        total_for_category = 0
        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
                matched_text = match.group().strip(" .,\n")
                if len(matched_text) > 2:
                    highlights.append({
                        "text": matched_text,
                        "start": match.start(),
                        "end": match.end(),
                        "category": category
                    })
                    total_for_category += 1
        print(f"🔎 {category}: {total_for_category} match(es)")

    print(f"✨ Total highlights collected: {len(highlights)}")
    return highlights


# ✅ Final API-friendly wrapper
def detect_highlights(book, chapter):
    print(f"\n🚀 Running detect_highlights for {book}/{chapter}")
    raw = highlight_by_keywords(book, chapter)

    if not raw:
        print("❌ No highlights detected.")
        return []

    # Return directly as it’s already in structured format
    print(f"📬 Returning {len(raw)} highlights.")
    return raw
