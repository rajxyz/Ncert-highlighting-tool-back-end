import re
import os

MAX_IMAGES = 5  # Limit number of pages to scan

# Define regex rules globally
RULES = {
    "definition": [
        r'\b(?:[A-Z][a-z]{2,}\s)?(?:is|are|was|refers to|means|is defined as|can be defined as)\b.{10,150}?\.',
        r'\bDefinition:\s?.{10,150}?\.'
    ],
    "date": [
        r'\b\d{1,2}(?:st|nd|rd|th)?\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.? \d{1,2},? \d{4}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
    ],
    "units": [
        r'\b\d+(?:\.\d+)?\s?(?:kg|g|mg|cm|m|km|mm|s|ms|Hz|J|W|V|A|Ω|°C|°F|%)\b'
    ],
    "capitalized_terms": [
        r'\b(?:[A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b'
    ],
    "example": [
        r'(?:For example|e\.g\.|such as)\s.{5,100}?[.,]',
        r'\bExample:\s.{5,150}?\.'
    ],
    "steps": [
        r'\b(?:Step\s?\d+|First|Second|Then|Next|Finally|In conclusion)[,:]?\s.{5,150}?\.',
    ],
    "cause_effect": [
        r'\b(?:Because|Due to|Since|As a result|Therefore|Thus|Hence|Consequently)\b.{5,150}?\.',
    ],
    "theories": [
        r'\b(?:Law|Theory|Principle|Rule) of [A-Z][a-z]+(?: [A-Z][a-z]+)?\b',
        r"\b[A-Z][a-z]+['’]s (?:Law|Theory|Principle|Rule)\b"
    ],
    "acronyms": [
        r'\b[A-Z]{2,6}(?:\s[A-Z]{2,6})?\b'
    ],
    "list_items": [
        r'(?:^|\n)\s*\d{1,2}[.)-]\s.{5,150}?(?:\.|\n)',
        r'(?:^|\n)\s*[-*•]\s.{5,150}?(?:\.|\n)'
    ],
    "foreign_words": [
        r'\b\w+(?:us|um|ae|es|is|on|ous|i)\b'
    ]
}


def is_junk(text):
    print(f"\n🔎 Checking potential junk: '{text}'")

    if len(text) < 5:
        print("❌ Rejected (too short)")
        return True

    if len(text.split()) < 2:
        print("❌ Rejected (too few words)")
        return True

    junk_phrases = {"of the", "has been", "was one", "is the", "that it", "been called", "his nearly"}
    junk_words = {"and", "the", "of", "in", "on", "who", "has", "was", "one", "all", "called", "for"}

    text_lower = text.lower().strip()

    if text_lower in junk_words:
        print(f"❌ Rejected (exact match in junk words): '{text_lower}'")
        return True

    if text_lower in junk_phrases:
        print(f"❌ Rejected (exact match in junk phrases): '{text_lower}'")
        return True

    print("✅ Passed junk filter")
    return False


def highlight_by_keywords(book, chapter, categories=None):
    book = book.strip()
    chapter = chapter.strip()
    print(f"\n🚧 USING UPDATED HIGHLIGHTER WITH DEBUGGING")
    print(f"📘 Book: {book} | Chapter: {chapter}")
    print(f"📥 Received categories: {categories}")

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
    print(f"🖼️ Scanning image(s): {selected_images}")

    highlights = []

    if categories and isinstance(categories, list):
        normalized = [c.lower() for c in categories]
        print(f"🔁 Normalized categories: {normalized}")
        active_rules = {k: RULES[k] for k in normalized if k in RULES}
        print(f"📌 Active rules being applied: {list(active_rules.keys())}")
    else:
        print("⚠️ No categories passed — using ALL rules")
        active_rules = RULES

    for idx, img in enumerate(selected_images):
        txt_file = os.path.splitext(img)[0] + ".txt"
        txt_path = os.path.join(folder_path, txt_file)

        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                page_text = f.read()
                print(f"\n📄 Text from {txt_file} (Page {idx + 1}): {len(page_text)} characters")

                for category, patterns in active_rules.items():
                    for pattern_index, pattern in enumerate(patterns):
                        print(f"\n🔎 Checking pattern [{pattern}] for category [{category}]")
                        matches_found = False
                        for match_index, match in enumerate(re.finditer(pattern, page_text, flags=re.IGNORECASE | re.MULTILINE)):
                            matches_found = True
                            matched_text = match.group().strip(" .,\n")
                            print(f"\n🧪 Match found: '{matched_text}' under [{category}]")

                            if len(matched_text) > 300:
                                print(f"⚠️ LARGE match detected: {len(matched_text)} characters. Check your pattern or input formatting.")

                            if len(matched_text) > 2 and not is_junk(matched_text):
                                print(f"✅ Highlight added: '{matched_text}'\n")
                                highlights.append({
                                    "text": matched_text,
                                    "start": match.start(),
                                    "end": match.end(),
                                    "category": category,
                                    "page_number": idx + 1,
                                    "match_id": f"{category}_{pattern_index}_{match_index}",
                                    "rule_name": pattern,
                                    "source": "regex"
                                })
                            else:
                                print(f"⚠️ Skipped (junk or too short): '{matched_text}'")
                        if not matches_found:
                            print(f"❌ No matches found for pattern: {pattern}")
        else:
            print(f"⚠️ Missing text file for: {img}")

    print(f"\n✨ Total highlights collected: {len(highlights)}")
    return highlights


def detect_highlights(book, chapter, categories=None):
    print(f"\n🚀 Running detect_highlights for {book}/{chapter}")
    raw = highlight_by_keywords(book, chapter, categories=categories)

    if not raw:
        print("❌ No highlights detected.")
        return []

    print(f"📬 Returning {len(raw)} highlights.")
    return raw


                                    










