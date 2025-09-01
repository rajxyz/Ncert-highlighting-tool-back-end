import os
import re
import inflect

# ────────────────────────────────────────────────
# Config
# ────────────────────────────────────────────────
MAX_IMAGES = 5
DEBUG_CONTEXT_CHARS = 40  # characters of left/right context shown around a match

inflector = inflect.engine()

# Try to import your storage layer (optional). If not present, we continue.
SAVE_ENABLED = False
try:
    from highlight_store import save_detected_highlight  # noqa: F401
    SAVE_ENABLED = True
except Exception:
    print(
        "[WARN] Storage layer not found (highlight_store.save_detected_highlight). "
        "Highlights will not be persisted to JSON."
    )

# ────────────────────────────────────────────────
# Regex rules
# ────────────────────────────────────────────────
RULES = {
    "definition": [
        r'\b(?:[A-Z][a-z]{2,}\s)?(?:is|are|was|refers to|means|is defined as|can be defined as)\b.{10,150}?.',
        r'\bDefinition:\s?.{10,150}?.'
    ],
    "date": [
        r'\b\d{1,2}(?:st|nd|rd|th)?\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? \d{1,2},? \d{4}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b(?:19|20)\d{2}\b'
    ],
    "units": [
        r'\b\d+(?:.\d+)?\s?(?:kg|g|mg|cm|m|km|mm|s|ms|Hz|J|W|V|A|Ω|Ohm|ohm|°C|°F|%)\b'
    ],
    "capitalized_terms": [
        r'\b(?:[A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b'
    ],
    "example": [
        r'(?:For example|e.g.|such as)\s.{5,100}?[.,]',
        r'\bExample:\s.{5,150}?.'
    ],
    "steps": [
        r'\b(?:Step\s?\d+|First|Second|Then|Next|Finally|In conclusion)[,:]?\s.{5,150}?.'
    ],
    "cause_effect": [
        r'\b(?:Because|Due to|Since|As a result|Therefore|Thus|Hence|Consequently)\b.{5,150}?.'
    ],
    "theories": [
        r'\b(?:Law|Theory|Principle|Rule) of [A-Z][a-z]+(?: [A-Z][a-z]+)?\b',
        r"\b[A-Z][a-z]+['’]s (?:Law|Theory|Principle|Rule)\b"
    ],
    "acronyms": [
        r'\b[A-Z]{2,6}(?:\s[A-Z]{2,6})?\b'
    ],
    "list_items": [
        r'(?:^|\n)\s*\d{1,2}[.)-]\s.{5,150}?(?:.|\n)',
        r'(?:^|\n)\s*[-\u2022]\s.{5,150}?(?:.|\n)'
    ],
    "foreign_words": [
        r'\b\w+(?:us|um|ae|es|is|on|ous|i)\b'
    ],
    "name": [
        r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b'
    ],
    "place": [
        r'\b(?:[A-Z][a-z]+(?:\s[A-Z][a-z]+))\b'
    ],
    "formula": [
        r'\b[A-Za-z]\s?=\s?.{1,80}?(?:;|.|\n)',
        r'\b(?:F=ma|E=mc^?2|V=IR|P=VI)\b'
    ],
}

CATEGORY_ALIASES = {
    "definitions": "definition",
    "definition": "definition",
    "date": "date",
    "dates": "date",
    "unit": "units",
    "units": "units",
    "example": "example",
    "examples": "example",
    "step": "steps",
    "steps": "steps",
    "rule": "theories",
    "rules": "theories",
    "theory": "theories",
    "theories": "theories",
    "abbreviation": "acronyms",
    "abbreviations": "acronyms",
    "acronym": "acronyms",
    "acronyms": "acronyms",
    "list": "list_items",
    "list_items": "list_items",
    "name": "name",
    "names": "name",
    "place": "place",
    "places": "place",
    "capitalized_terms": "capitalized_terms",
    "cause_effect": "cause_effect",
    "formula": "formula",
    "formulas": "formula",
}

# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────
def is_junk(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if t.isdigit() and len(t) == 4:
        return False
    if len(t) < 5 or len(t.split()) < 2:
        return True
    if re.fullmatch(r'[\W_]+', t):
        return True

    junk_phrases = {"of the", "has been", "was one", "is the", "that it", "been called", "his nearly"}  
    junk_words = {"and", "the", "of", "in", "on", "who", "has", "was", "one", "all", "called", "for"}  

    if t.lower() in junk_words or t.lower() in junk_phrases:  
        return True  
    return False

def normalize_category(cat: str) -> str:
    if not cat:
        return ""
    base = cat.strip().lower()
    singular = inflector.singular_noun(base) or base
    norm = CATEGORY_ALIASES.get(singular, singular)
    print(f"[DEBUG] normalize_category: '{cat}' → '{norm}'")
    return norm

def _list_chapter_pages(folder_path: str):
    pages_to_scan = []
    images = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    for idx, img in enumerate(images[:MAX_IMAGES]):
        txt_file = os.path.splitext(img)[0] + ".txt"
        txt_path = os.path.join(folder_path, txt_file)
        if os.path.exists(txt_path):
            pages_to_scan.append((idx + 1, txt_path))
        else:
            print(f"[WARN] Text missing for image: {img}")
    return pages_to_scan

def _context_snippet(text: str, start: int, end: int) -> str:
    left = max(0, start - DEBUG_CONTEXT_CHARS)
    right = min(len(text), end + DEBUG_CONTEXT_CHARS)
    prefix = text[left:start].replace("\n", " ")
    middle = text[start:end].replace("\n", " ")
    suffix = text[end:right].replace("\n", " ")
    return f"...{prefix} «{middle}» {suffix}..."

# ────────────────────────────────────────────────
# Core: regex-based highlighter
# ────────────────────────────────────────────────
def highlight_by_keywords(book: str, chapter: str, categories=None, page=None):
    print(f"[DEBUG] Initializing highlight_by_keywords")
    print(f"[INFO] Book: {book}, Chapter: {chapter}, Page: {page}")
    print(f"[INFO] Incoming categories: {categories}")

    folder_path = os.path.join("static", "books", book.strip(), chapter.strip())  
    if not os.path.isdir(folder_path):  
        print(f"[ERROR] Directory not found: {folder_path}")  
        return []  

    # Determine which rules to apply  
    active_rules = {}  
    if categories and isinstance(categories, list) and len(categories) > 0:  
        normalized = [normalize_category(c) for c in categories]  
        active_rules = {k: RULES[k] for k in normalized if k in RULES}  
        print(f"[DEBUG] Active rules applied: {list(active_rules.keys())}")  
        missing = [k for k in normalized if k not in RULES]  
        if missing:  
            print(f"[WARN] No rules for categories: {missing}")  
        if not active_rules:  
            print(f"[WARN] No active rules available. Returning empty result.")  
            return []  
    else:  
        print("[INFO] No categories provided, using ALL rules.")  
        active_rules = RULES  

    # Determine pages to scan  
    pages_to_scan = []  
    if page:  
        txt_file = f"{page}.txt"  
        txt_path = os.path.join(folder_path, txt_file)  
        if os.path.exists(txt_path):  
            pages_to_scan.append((int(page), txt_path))  
        else:  
            print(f"[ERROR] Specified page {page} not found in chapter")  
            return []  
    else:  
        try:  
            pages_to_scan = _list_chapter_pages(folder_path)  
        except Exception as e:  
            print(f"[ERROR] Could not list files in: {folder_path} → {e}")  
            return []  

    highlights = []  
    seen_texts = set()  

    for page_number, txt_path in pages_to_scan:  
        print(f"[SCAN] Page {page_number}: {os.path.basename(txt_path)}")  
        try:  
            with open(txt_path, "r", encoding="utf-8") as f:  
                page_text = f.read()  
        except Exception as e:  
            print(f"[ERROR] Could not read {txt_path}: {e}")  
            continue  

        for category, patterns in active_rules.items():  
            for pattern_index, pattern in enumerate(patterns):  
                try:  
                    matches = list(re.finditer(pattern, page_text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL))  
                except re.error as rex:  
                    print(f"[ERROR] Invalid regex for {category} (pattern {pattern_index}): {rex}")  
                    continue  

                print(f"[MATCH] {category.upper()} → Pattern {pattern_index} matched {len(matches)} time(s)")  

                for match_index, match in enumerate(matches):  
                    raw_text = match.group()  
                    matched_text = raw_text.strip(" .,\n\t\r")  

                    if is_junk(matched_text):  
                        print(f"[SKIP] Junk text: {matched_text}")  
                        continue  

                    match_key = f"{matched_text}|{category}|{page_number}"  
                    if match_key in seen_texts:  
                        print(f"[SKIP] Duplicate: {matched_text}")  
                        continue  
                    seen_texts.add(match_key)  

                    start_idx, end_idx = match.start(), match.end()  
                    highlights.append({  
                        "text": matched_text,  
                        "start": start_idx,  
                        "end": end_idx,  
                        "category": category,  
                        "page_number": int(page_number),  
                        "match_id": f"{category}_{pattern_index}_{match_index}",  
                        "rule_name": pattern,  
                        "source": "regex"  
                    })  

                    ctx = _context_snippet(page_text, start_idx, end_idx)  
                    print(f"[OK] Match: {matched_text} (Page: {page_number}, idx={start_idx}-{end_idx})")  
                    print(f"[CTX] {ctx}")  

    print(f"[RESULT] Total highlights: {len(highlights)}")  
    return highlights

# ────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────
def detect_highlights(book: str, chapter: str, categories=None, page=None, persist: bool = False):
    print(f"[INFO] Running detect_highlights: Book={book}, Chapter={chapter}, Page={page}")

    if categories is None:  
        cat_list = []  
    elif isinstance(categories, list):  
        cat_list = categories  
    else:  
        cat_list = [categories]  

    if not isinstance(cat_list, list):  
        print(f"[WARN] 'categories' not a list: got {type(categories)} → coercing to list.")  
        cat_list = [str(categories)]  

    result = highlight_by_keywords(book, chapter, categories=cat_list, page=page)  
    print(f"[INFO] Highlights returned: {len(result)}")  

    if persist and SAVE_ENABLED:  
        for h in result:  
            try:  
                normalized_cat = normalize_category(h.get("category", ""))  
                save_detected_highlight(  
                    book=book,  
                    chapter=chapter,  
                    text=h.get("text", ""),  
                    start=h.get("start", 0),  
                    end=h.get("end", 0),  
                    category=normalized_cat,   # ✅ FIXED  
                    page_number=h.get("page_number", 0),  
                    match_id=h.get("match_id"),  
                    rule_name=h.get("rule_name"),  
                    source=h.get("source"),  
                )  
            except Exception as e:  
                print(f"[WARN] Failed to persist highlight {h.get('match_id')}: {e}")  
    elif persist and not SAVE_ENABLED:  
        print("[WARN] persist=True requested but storage layer not available; skipping save.")  

    return result
























