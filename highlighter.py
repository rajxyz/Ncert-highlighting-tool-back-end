import os
import re
import json
import inflect

# ────────────────────────────────────────────────
# Config
# ────────────────────────────────────────────────
MAX_IMAGES = 5
DEBUG_CONTEXT_CHARS = 40  # chars around match for context

inflector = inflect.engine()

SAVE_ENABLED = False
try:
    from highlight_store import save_detected_highlight  # noqa: F401
    SAVE_ENABLED = True
except Exception:
    print("[WARN] Storage layer not found. Highlights will not be persisted to JSON.")

# ────────────────────────────────────────────────
# Regex rules
# ────────────────────────────────────────────────
RULES = {
    "date": [
        r'\b\d{1,2}(?:st|nd|rd|th)?\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? \d{1,2},? \d{4}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b(?:19|20)\d{2}\b'
    ]
}

CATEGORY_ALIASES = {
    "date": "date",
    "dates": "date",
    "pyq": "pyq",
    "pyqs": "pyq"
}

# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────
def is_junk(text: str, category: str = None) -> bool:
    t = (text or "").strip()
    junk_keywords = {
        "html", "head", "body", "div", "class", "span", "style", "script",
        "lang", "href", "meta", "link", "content", "http", "www", "doctype"
    }

    if not t:
        print(f"[DEBUG JUNK] Empty or blank text detected as junk.")
        return True

    if any(tag in t.lower() for tag in junk_keywords):
        print(f"[DEBUG JUNK] Text '{t}' contains junk keyword.")
        return True

    # Accept 4-digit years as valid in 'date' category
    if category == "date" and t.isdigit() and len(t) == 4:
        print(f"[DEBUG JUNK] Text '{t}' is a valid 4-digit year in category 'date'. Not junk.")
        return False

    if re.match(r'^[\W_]+$', t):
        print(f"[DEBUG JUNK] Text '{t}' is non-alphanumeric junk.")
        return True

    if len(t) < 3:
        print(f"[DEBUG JUNK] Text '{t}' too short, considered junk.")
        return True

    return False

def normalize_category(cat: str) -> str:
    if not cat:
        return ""
    base = cat.strip().lower()
    singular = inflector.singular_noun(base) or base
    norm = CATEGORY_ALIASES.get(singular, singular)
    return norm

def _list_chapter_pages(folder_path: str):
    pages_to_scan = []
    images = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    for idx, img in enumerate(images[:MAX_IMAGES]):
        txt_file = os.path.splitext(img)[0] + ".txt"
        txt_path = os.path.join(folder_path, txt_file)
        if os.path.exists(txt_path):
            pages_to_scan.append((idx + 1, txt_path))
    print(f"[DEBUG PAGE SCAN] Found pages to scan: {pages_to_scan}")
    return pages_to_scan

def _context_snippet(text: str, start: int, end: int) -> str:
    left = max(0, start - DEBUG_CONTEXT_CHARS)
    right = min(len(text), end + DEBUG_CONTEXT_CHARS)
    return f"...{text[left:start]} «{text[start:end]}» {text[end:right]}..."

def _load_pyq(book: str, chapter: str):
    file_path = os.path.join("static", "pyq", book.strip(), f"{chapter.strip()}.json")
    if not os.path.exists(file_path):
        print(f"[WARN] PYQ file not found: {file_path}")
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[DEBUG PYQ LOAD] Loaded {len(data.get('pyq', []))} PYQs from {file_path}")
        return data.get("pyq", [])
    except Exception as e:
        print(f"[ERROR] Failed to load PYQ JSON from {file_path}: {e}")
        return []

# ────────────────────────────────────────────────
# Core highlighter
# ────────────────────────────────────────────────
def highlight_by_keywords(book: str, chapter: str, categories=None, page=None):
    folder_path = os.path.join("static", "books", book.strip(), chapter.strip())
    if not os.path.isdir(folder_path):
        print(f"[ERROR] Directory not found: {folder_path}")
        return []

    normalized = [normalize_category(c) for c in (categories or [])]
    active_rules = {k: RULES[k] for k in normalized if k in RULES}
    do_pyq = "pyq" in normalized

    if not active_rules and not do_pyq:
        print("[DEBUG] No active rules or PYQ configured for highlighting.")
        return []

    pages_to_scan = _list_chapter_pages(folder_path) if not page else [(int(page), os.path.join(folder_path, f"{page}.txt"))]

    highlights = []
    seen_texts = set()

    for page_number, txt_path in pages_to_scan:
        if not os.path.exists(txt_path):
            print(f"[DEBUG SKIP PAGE] Text file not found: {txt_path}")
            continue

        with open(txt_path, "r", encoding="utf-8") as f:
            page_text = f.read()

        # Regex matches
        for category, patterns in active_rules.items():
            for pattern in patterns:
                print(f"[DEBUG PATTERN] Applying pattern: {pattern}")
                for match in re.finditer(pattern, page_text):
                    matched_text = match.group().strip()
                    print(f"[DEBUG MATCH] Found candidate '{matched_text}' for category '{category}' on page {page_number}")

                    if is_junk(matched_text, category):
                        print(f"[DEBUG SKIP JUNK] Skipping '{matched_text}'")
                        continue

                    key = f"{matched_text}|{category}|{page_number}"
                    if key in seen_texts:
                        print(f"[DEBUG SKIP DUPLICATE] Already seen: {matched_text}")
                        continue

                    seen_texts.add(key)
                    snippet = _context_snippet(page_text, match.start(), match.end())
                    print(f"[DEBUG SNIPPET] Context: {snippet}")

                    highlights.append({
                        "text": matched_text,
                        "category": category,
                        "page_number": page_number,
                        "source": "regex",
                        "start": match.start(),
                        "end": match.end()
                    })

        # PYQ matches
        if do_pyq:
            pyq_list = _load_pyq(book, chapter)
            for q in pyq_list:
                index = page_text.lower().find(q.lower())
                print(f"[DEBUG PYQ] Searching PYQ '{q}' in page {page_number}")

                if index != -1:
                    key = f"{q}|pyq|{page_number}"
                    if key in seen_texts:
                        print(f"[DEBUG SKIP DUPLICATE PYQ] Already seen: {q}")
                        continue

                    seen_texts.add(key)
                    snippet = _context_snippet(page_text, index, index + len(q))
                    print(f"[DEBUG SNIPPET] PYQ Context: {snippet}")

                    highlights.append({
                        "text": q,
                        "category": "pyq",
                        "page_number": page_number,
                        "source": "pyq-json",
                        "start": index,
                        "end": index + len(q)
                    })
                else:
                    print(f"[DEBUG PYQ NOT FOUND] '{q}' not found in page {page_number}")

    print(f"[DEBUG FINAL RESULT] Highlights found: {highlights}")
    return highlights

# ────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────
def detect_highlights(book: str, chapter: str, categories=None, page=None, persist: bool = False):
    if isinstance(categories, str):
        categories = [categories]

    print(f"[DEBUG API CALL] Detect highlights called with book='{book}', chapter='{chapter}', categories={categories}, page={page}, persist={persist}")

    result = highlight_by_keywords(book, chapter, categories=categories, page=page)

    # Persist highlights
    if persist and SAVE_ENABLED:
        for h in result:
            if is_junk(h["text"], h["category"]):
                print(f"⚠ Skipped junk/short highlight: '{h['text']}' in category '{h['category']}'")
                continue
            try:
                save_detected_highlight(
                    book=book,
                    chapter=chapter,
                    text=h["text"],
                    category=h["category"],
                    page_number=h["page_number"],
                    source=h["source"]
                )
                print(f"[DEBUG SAVE] Highlight saved: {h}")
            except Exception as e:
                print(f"[WARN] Failed to persist highlight: {e}")

    print(f"[DEBUG API RESULT] Total highlights detected: {len(result)}")
    return result
