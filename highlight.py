import os
import re
import json
import inflect

# ────────────────────────────────────────────────
# Config
# ────────────────────────────────────────────────
MAX_IMAGES = 5
DEBUG_CONTEXT_CHARS = 40  # characters of left/right context
inflector = inflect.engine()

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
    "name": [
        r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b'
    ],
    "units": [
        r'\b\d+(?:.\d+)?\s?(?:kg|g|mg|cm|m|km|mm|s|ms|Hz|J|W|V|A|Ω|Ohm|ohm|°C|°F|%)\b'
    ],
    "example": [
        r'(?:For example|e.g.|such as)\s.{5,100}?[.,]',
        r'\bExample:\s.{5,150}?.'
    ]
}

CATEGORY_ALIASES = {
    "definitions": "definition",
    "definition": "definition",
    "date": "date",
    "dates": "date",
    "name": "name",
    "names": "name",
    "unit": "units",
    "units": "units",
    "example": "example",
    "examples": "example"
}

ALLOWED_CATEGORIES = set(RULES.keys())

# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────
def normalize_category(cat: str) -> str:
    if not cat:
        return ""
    base = cat.strip().lower()
    singular = inflector.singular_noun(base) or base
    norm = CATEGORY_ALIASES.get(singular, singular)
    return norm if norm in ALLOWED_CATEGORIES else ""

def is_junk(text: str) -> bool:
    t = (text or "").strip()
    if not t or len(t) < 3:
        return True
    junk_words = {"and", "the", "of", "in", "on", "who", "has", "was", "one", "all", "called", "for"}
    if t.lower() in junk_words:
        return True
    if re.fullmatch(r'[\W\d\s]+', t):
        return True
    return False

def _context_snippet(text: str, start: int, end: int) -> str:
    left = max(0, start - DEBUG_CONTEXT_CHARS)
    right = min(len(text), end + DEBUG_CONTEXT_CHARS)
    return f"...{text[left:start]} «{text[start:end]}» {text[end:right]}..."

def get_chapter_file_path(book, chapter):
    folder_path = os.path.join("static", "highlights", book)
    os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, f"{chapter}.json")

def load_data(book, chapter):
    path = get_chapter_file_path(book, chapter)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(book, chapter, highlights):
    path = get_chapter_file_path(book, chapter)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(highlights, f, indent=2, ensure_ascii=False)

# ────────────────────────────────────────────────
# Core highlight detection
# ────────────────────────────────────────────────
def highlight_page(book, chapter, page_number, categories=None):
    folder_path = os.path.join("static", "books", book.strip(), chapter.strip())
    txt_file = os.path.join(folder_path, f"{page_number}.txt")
    if not os.path.exists(txt_file):
        print(f"[WARN] Page {page_number} not found.")
        return []

    page_text = open(txt_file, "r", encoding="utf-8").read()
    normalized_categories = [normalize_category(c) for c in (categories or ALLOWED_CATEGORIES)]
    normalized_categories = [c for c in normalized_categories if c]

    highlights = []
    seen_texts = set()

    for category in normalized_categories:
        for pattern in RULES[category]:
            for match in re.finditer(pattern, page_text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL):
                text = match.group().strip(" \n.,")
                if is_junk(text) or text in seen_texts:
                    continue
                seen_texts.add(text)
                highlights.append({
                    "text": text,
                    "start": match.start(),
                    "end": match.end(),
                    "category": category,
                    "page_number": page_number
                })
    return highlights

# ────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────
def detect_highlights(book, chapter, categories=None, pages=None):
    """
    Detect highlights for given book/chapter.
    pages: list of page numbers. If None, detect all available pages up to MAX_IMAGES.
    """
    folder_path = os.path.join("static", "books", book.strip(), chapter.strip())
    if not os.path.isdir(folder_path):
        print(f"[ERROR] Chapter folder not found: {folder_path}")
        return []

    all_pages = sorted([int(os.path.splitext(f)[0]) for f in os.listdir(folder_path)
                        if f.lower().endswith(".txt")])
    if pages:
        pages_to_scan = [p for p in pages if p in all_pages]
    else:
        pages_to_scan = all_pages[:MAX_IMAGES]

    all_highlights = load_data(book, chapter)

    for page_number in pages_to_scan:
        page_highlights = highlight_page(book, chapter, page_number, categories)
        # Merge with existing highlights, skip duplicates
        for h in page_highlights:
            if not any(existing["text"] == h["text"] and existing["category"] == h["category"]
                       and existing["page_number"] == h["page_number"] for existing in all_highlights):
                all_highlights.append(h)
        save_data(book, chapter, all_highlights)
        print(f"[INFO] Page {page_number} → {len(page_highlights)} new highlights added.")

    return all_highlights




























































