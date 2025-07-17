import re
import os
import inflect

MAX_IMAGES = 5
inflector = inflect.engine()

# Add year-only support explicitly
RULES = {
    "definition": [
        r'\b(?:[A-Z][a-z]{2,}\s)?(?:is|are|was|refers to|means|is defined as|can be defined as)\b.{10,150}?\.',
        r'\bDefinition:\s?.{10,150}?\.'
    ],
    "date": [
        r'\b\d{1,2}(?:st|nd|rd|th)?\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.? \d{1,2},? \d{4}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b(?:19|20)\d{2}\b'
    ],
    "units": [
        r'\b\d+(?:\.\d+)?\s?(?:kg|g|mg|cm|m|km|mm|s|ms|Hz|J|W|V|A|\u03A9|\u00B0C|\u00B0F|%)\b'
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
        r'(?:^|\n)\s*[-*\u2022]\s.{5,150}?(?:\.|\n)'
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
    return text.lower().strip() in junk_words or text.lower().strip() in junk_phrases

def normalize_category(cat):
    return inflector.singular_noun(cat.lower()) or cat.lower()

def highlight_by_keywords(book, chapter, categories=None, page=None):
    print(f"[DEBUG] Initializing highlight_by_keywords")
    print(f"[INFO] Book: {book}, Chapter: {chapter}, Page: {page}")
    print(f"[INFO] Incoming categories: {categories}")

    folder_path = os.path.join("static", "books", book.strip(), chapter.strip())
    if not os.path.isdir(folder_path):
        print(f"[ERROR] Directory not found: {folder_path}")
        return []

    highlights = []
    seen_texts = set()

    # Normalize categories and select rules
    if categories and isinstance(categories, list):
        if categories == ["date"]:
            print("[WARN] Only 'date' category received – possible frontend bug")
        normalized = [normalize_category(c) for c in categories]
        active_rules = {k: RULES[k] for k in normalized if k in RULES}
        print(f"[DEBUG] Active rules applied: {list(active_rules.keys())}")
    else:
        print("[INFO] No categories provided, using ALL rules")
        active_rules = RULES

    # PAGE selection logic
    pages_to_scan = []
    if page:
        txt_file = f"{page}.txt"
        txt_path = os.path.join(folder_path, txt_file)
        if os.path.exists(txt_path):
            print(f"[INFO] Scanning only page {page}")
            pages_to_scan.append((page, txt_path))
        else:
            print(f"[ERROR] Specified page {page} not found in chapter")
            return []
    else:
        try:
            images = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            for idx, img in enumerate(images[:MAX_IMAGES]):
                txt_file = os.path.splitext(img)[0] + ".txt"
                txt_path = os.path.join(folder_path, txt_file)
                if os.path.exists(txt_path):
                    pages_to_scan.append((idx + 1, txt_path))
                else:
                    print(f"[WARN] Text missing for image: {img}")
        except Exception as e:
            print(f"[ERROR] Could not list files in: {folder_path} → {e}")
            return []

    for page_number, txt_path in pages_to_scan:
        print(f"[SCAN] Page {page_number}: {os.path.basename(txt_path)}")
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                page_text = f.read()
        except Exception as e:
            print(f"[ERROR] Could not read {txt_path}: {e}")
            continue

        print(f"[INFO] Text length: {len(page_text)}")

        for category, patterns in active_rules.items():
            for pattern_index, pattern in enumerate(patterns):
                matches = list(re.finditer(pattern, page_text, flags=re.IGNORECASE | re.MULTILINE))
                print(f"[MATCH] {category.upper()} → Pattern {pattern_index} matched {len(matches)} time(s)")

                for match_index, match in enumerate(matches):
                    matched_text = match.group().strip(" .,\n")
                    if is_junk(matched_text):
                        print(f"[SKIP] Junk text: {matched_text}")
                        continue
                    match_key = f"{matched_text}|{category}|{page_number}"
                    if match_key in seen_texts:
                        print(f"[SKIP] Duplicate: {matched_text}")
                        continue
                    seen_texts.add(match_key)
                    highlights.append({
                        "text": matched_text,
                        "start": match.start(),
                        "end": match.end(),
                        "category": category,
                        "page_number": int(page_number),
                        "match_id": f"{category}_{pattern_index}_{match_index}",
                        "rule_name": pattern,
                        "source": "regex"
                    })
                    print(f"[OK] Match: {matched_text} (Page: {page_number})")

    print(f"[RESULT] Total highlights: {len(highlights)}")
    return highlights

def detect_highlights(book, chapter, categories=None, page=None):
    print(f"[INFO] Running detect_highlights: Book={book}, Chapter={chapter}, Page={page}")
    if not isinstance(categories, list):
        print(f"[WARN] 'categories' not a list: got {type(categories)}")
        categories = [categories] if categories else []

    result = highlight_by_keywords(book, chapter, categories=categories, page=page)
    print(f"[INFO] Highlights returned: {len(result)}")
    return result












































































