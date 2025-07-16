import re
import os
import inflect

MAX_IMAGES = 5
inflector = inflect.engine()

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
    if len(text) < 5 or len(text.split()) < 2:
        return True

    junk_phrases = {"of the", "has been", "was one", "is the", "that it", "been called", "his nearly"}
    junk_words = {"and", "the", "of", "in", "on", "who", "has", "was", "one", "all", "called", "for"}

    text_lower = text.lower().strip()
    return text_lower in junk_words or text_lower in junk_phrases

def highlight_by_keywords(book, chapter, categories=None, page=None):
    folder_path = os.path.join("static", "books", book.strip(), chapter.strip())
    if not os.path.isdir(folder_path):
        return []

    highlights = []
    seen_texts = set()

    if categories and isinstance(categories, list):
        normalized = [
            inflector.singular_noun(c.lower()) or c.lower()
            for c in categories
        ]
        active_rules = {k: RULES[k] for k in normalized if k in RULES}
    else:
        active_rules = RULES

    def process_page_text(text, page_number):
        for category, patterns in active_rules.items():
            for pattern_index, pattern in enumerate(patterns):
                for match_index, match in enumerate(re.finditer(pattern, text, flags=re.IGNORECASE | re.MULTILINE)):
                    matched_text = match.group().strip(" .,\n")

                    if len(matched_text) > 300 or is_junk(matched_text):
                        continue

                    match_key = f"{matched_text}|{category}|{page_number}"
                    if match_key in seen_texts:
                        continue

                    seen_texts.add(match_key)
                    highlights.append({
                        "text": matched_text,
                        "start": match.start(),
                        "end": match.end(),
                        "category": category,
                        "page_number": page_number,
                        "match_id": f"{category}_{pattern_index}_{match_index}",
                        "rule_name": pattern,
                        "source": "regex"
                    })

    if page:
        txt_path = os.path.join(folder_path, f"{page}.txt")
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                process_page_text(f.read(), int(page))
    else:
        image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        selected_images = image_files[:MAX_IMAGES]

        for idx, img in enumerate(selected_images):
            txt_file = os.path.splitext(img)[0] + ".txt"
            txt_path = os.path.join(folder_path, txt_file)
            if os.path.exists(txt_path):
                with open(txt_path, "r", encoding="utf-8") as f:
                    process_page_text(f.read(), idx + 1)

    return highlights

def detect_highlights(book, chapter, categories=None, page=None):
    return highlight_by_keywords(book, chapter, categories, page)













