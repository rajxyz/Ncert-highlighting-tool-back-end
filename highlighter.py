import re
import os
import inflect

MAX_IMAGES = 5
inflector = inflect.engine()

# === REGEX RULES ===
RULES = {
    "definition": [...],  # keep existing
    "date": [
        r'\b\d{1,2}(?:st|nd|rd|th)?\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.? \d{1,2},? \d{4}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b(19|20)\d{2}\b'
    ],
    "units": [...],
    "capitalized_terms": [...],
    "example": [...],
    "steps": [...],
    "cause_effect": [...],
    "theories": [...],
    "acronyms": [...],
    "list_items": [...],
    "foreign_words": [...],

    # ✅ Add basic rules for name, place, event
    "name": [
        r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b'
    ],
    "place": [
        r'\b(?:Delhi|Mumbai|India|Asia|Europe|Africa|USA|UK|Japan)\b'
    ],
    "event": [
        r'\b(?:Independence|Revolution|War|Treaty|Protest|Movement|Partition)\b'
    ]
}

# === HELPERS ===
def is_junk(text):
    if len(text) < 4: return True
    if len(text.split()) < 2 and not text.isdigit(): return True
    junk_words = {"and", "the", "of", "in", "on", "who", "has", "was", "one"}
    junk_phrases = {"of the", "has been", "was one", "been called"}
    return text.lower().strip() in junk_words or text.lower().strip() in junk_phrases

def normalize_category(cat):
    return inflector.singular_noun(cat.lower()) or cat.lower()

# === MAIN HIGHLIGHT FUNCTION ===
def highlight_by_keywords(book, chapter, categories=None, page=None):
    print(f"[INFO] USING UPDATED HIGHLIGHTER WITH FULL DEBUGGING")
    print(f"[INFO] Book: {book} | Chapter: {chapter} | Page: {page}")
    print(f"[INFO] Received categories: {categories} (type: {type(categories)})")

    folder_path = os.path.join("static", "books", book.strip(), chapter.strip())
    if not os.path.isdir(folder_path):
        print(f"[ERROR] Chapter folder not found: {folder_path}")
        return []

    highlights = []
    seen_texts = set()

    # === CATEGORY FILTERING ===
    if categories and isinstance(categories, list):
        normalized = [normalize_category(c) for c in categories]
        print(f"[DEBUG] Normalized categories: {normalized}")
        active_rules = {k: RULES[k] for k in normalized if k in RULES}
        if not active_rules:
            print(f"[WARN] No matching regex rules found for: {normalized}")
        print(f"[DEBUG] Active rules: {list(active_rules.keys())}")
    else:
        print("[WARN] No categories passed — using ALL rules")
        active_rules = RULES

    pages_to_scan = []

    # === PAGE SELECTION ===
    if page:
        txt_file = f"page{page}.txt" if not str(page).endswith(".txt") else page
        txt_path = os.path.join(folder_path, txt_file)
        if os.path.exists(txt_path):
            pages_to_scan.append((page, txt_path))
            print(f"[DEBUG] Only scanning page {page}")
        else:
            print(f"[WARN] Text file not found for page {page}: {txt_file}")
    else:
        try:
            all_images = sorted([
                f for f in os.listdir(folder_path)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ])[:MAX_IMAGES]
            print(f"[INFO] Scanning image(s): {all_images}")
            for idx, img in enumerate(all_images):
                txt_file = os.path.splitext(img)[0] + ".txt"
                txt_path = os.path.join(folder_path, txt_file)
                if os.path.exists(txt_path):
                    pages_to_scan.append((idx + 1, txt_path))
                else:
                    print(f"[WARN] Missing OCR text for: {img}")
        except Exception as e:
            print(f"[ERROR] Reading folder failed: {e}")
            return []

    # === ACTUAL MATCHING ===
    for page_number, txt_path in pages_to_scan:
        print(f"[INFO] Scanning Page {page_number}: {os.path.basename(txt_path)}")
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                page_text = f.read()
        except Exception as e:
            print(f"[ERROR] Failed to read {txt_path}: {e}")
            continue

        print(f"[INFO] Text length: {len(page_text)} characters")

        for category, patterns in active_rules.items():
            for i, pattern in enumerate(patterns):
                print(f"[MATCH] Pattern: {pattern} | Category: {category}")
                matches = list(re.finditer(pattern, page_text, flags=re.IGNORECASE | re.MULTILINE))
                print(f"[MATCH] Total found: {len(matches)}")

                for j, match in enumerate(matches):
                    match_text = match.group().strip(" .,\n")
                    print(f"[MATCH] #{j}: {match_text}")

                    # 🔍 Fix: Avoid skipping 4-digit years in date context
                    if is_junk(match_text) and category != "date":
                        print(f"[SKIP] Junk: {match_text}")
                        continue

                    match_key = f"{match_text}|{category}|{page_number}"
                    if match_key in seen_texts:
                        print("[SKIP] Duplicate match")
                        continue

                    seen_texts.add(match_key)
                    highlight = {
                        "text": match_text,
                        "start": match.start(),
                        "end": match.end(),
                        "category": category,
                        "page_number": int(page_number),
                        "match_id": f"{category}_{i}_{j}",
                        "rule_name": pattern,
                        "source": "regex"
                    }
                    highlights.append(highlight)
                    print(f"[OK] Highlight saved: {match_text}")

    print(f"[INFO] Total highlights collected: {len(highlights)}")
    return highlights

# === WRAPPER FUNCTION ===
def detect_highlights(book, chapter, categories=None, page=None):
    print(f"[INFO] Running detect_highlights for {book}/{chapter} - Page: {page}")
    if not isinstance(categories, list):
        print(f"[WARN] Expected 'categories' to be list, got {type(categories)}. Converting...")
        categories = [categories] if categories else []

    raw = highlight_by_keywords(book, chapter, categories=categories, page=page)

    if not raw:
        print("[ERROR] No highlights detected")
        return []

    print(f"[INFO] Returning {len(raw)} highlights")
    return raw



















































