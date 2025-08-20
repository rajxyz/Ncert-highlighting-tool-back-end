import os
import re
import json
import inflect

# ────────────────────────────────────────────────
# Config
# ────────────────────────────────────────────────

MAX_IMAGES = 5
DEBUG_CONTEXT_CHARS = 40  # chars shown around a match

inflector = inflect.engine()

# Try optional storage layer
SAVE_ENABLED = False
try:
    from highlight_store import save_detected_highlight  # noqa: F401
    SAVE_ENABLED = True
except Exception:
    print("[WARN] Storage layer not found. Highlights will not be persisted externally.")

# ────────────────────────────────────────────────
# Regex rules for different categories
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
        r'\b\d+(?:.\d+)?\s?(?:kg|g|mg|cm|m|km|mm|s|ms|Hz|J|W|V|A|Ω|°C|°F|%)\b'
    ],
    "example": [
        r'(?:For example|e.g.|such as)\s.{5,100}?[.,]',
        r'\bExample:\s.{5,150}?.'
    ],
    # add more categories as needed...
}

CATEGORY_ALIASES = {
    "definitions": "definition",
    "definition": "definition",
    "dates": "date",
    "date": "date",
    "unit": "units",
    "units": "units",
    "name": "name",
    "names": "name",
    "example": "example",
    "examples": "example"
}

# ────────────────────────────────────────────────
# Helper functions
# ────────────────────────────────────────────────

def is_junk(text: str) -> bool:
    t = (text or "").strip()
    if not t or len(t.split()) < 2:
        return True
    junk_words = {"and", "the", "of", "in", "on", "who", "has", "was", "one", "all", "called", "for"}
    if t.lower() in junk_words:
        return True
    if any(tag in t.lower() for tag in ["<span", "<div", "class", "style"]):
        return True
    return False

def normalize_category(cat: str) -> str:
    if not cat:
        return ""
    base = cat.strip().lower()
    singular = inflector.singular_noun(base) or base
    norm = CATEGORY_ALIASES.get(singular, singular)
    return norm

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
        except Exception:
            return []
    return []

def save_data(book, chapter, highlights):
    path = get_chapter_file_path(book, chapter)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(highlights, f, indent=2, ensure_ascii=False)

def _context_snippet(text: str, start: int, end: int) -> str:
    left = max(0, start - DEBUG_CONTEXT_CHARS)
    right = min(len(text), end + DEBUG_CONTEXT_CHARS)
    return f"...{text[left:start].replace(chr(10),' ')} «{text[start:end]}» {text[end:right].replace(chr(10),' ')}..."

# ────────────────────────────────────────────────
# Core: regex-based highlighter
# ────────────────────────────────────────────────

def highlight_page(book, chapter, page_text, page_number, categories=None):
    """Highlight a single page and return list of highlights"""
    active_rules = RULES
    if categories:
        normalized = [normalize_category(c) for c in categories]
        active_rules = {k: RULES[k] for k in normalized if k in RULES}

    highlights = []
    seen_texts = set()

    for category, patterns in active_rules.items():
        for pattern_index, pattern in enumerate(patterns):
            try:
                matches = list(re.finditer(pattern, page_text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL))
            except re.error:
                continue
            for match_index, match in enumerate(matches):
                matched_text = match.group().strip(" .,\n\t\r")
                if is_junk(matched_text):
                    continue
                key = f"{matched_text}|{category}|{page_number}"
                if key in seen_texts:
                    continue
                seen_texts.add(key)
                start_idx, end_idx = match.start(), match.end()
                highlights.append({
                    "text": matched_text,
                    "start": start_idx,
                    "end": end_idx,
                    "category": category,
                    "page_number": page_number,
                    "match_id": f"{category}_{pattern_index}_{match_index}",
                    "rule_name": pattern,
                    "source": "regex"
                })
    return highlights

def detect_highlights(book, chapter, categories=None, page_texts=None, persist=True):
    """
    Detect highlights for a chapter.
    page_texts: dict {page_number: text}
    """
    all_highlights = []
    highlights_data = load_data(book, chapter)

    pages_to_scan = page_texts or {}
    for page_number, page_text in pages_to_scan.items():
        page_hls = highlight_page(book, chapter, page_text, page_number, categories)
        # Avoid duplicates
        for hl in page_hls:
            if hl not in highlights_data:
                highlights_data.append(hl)
                all_highlights.append(hl)

    if persist:
        save_data(book, chapter, highlights_data)
    return all_highlights

def get_highlights(book, chapter, page_number=None, category=None):
    """Fetch highlights from storage"""
    highlights = load_data(book, chapter)
    if page_number is not None:
        highlights = [h for h in highlights if h["page_number"] == int(page_number)]
    if category is not None:
        highlights = [h for h in highlights if h["category"] == category]
    return highlights












































