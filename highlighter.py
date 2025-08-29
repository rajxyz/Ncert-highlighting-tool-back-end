import json
import os
import re

# -----------------------------
# Allowed NCERT & exam-relevant categories
# -----------------------------
ALLOWED_CATEGORIES = {
    "definition": "Key definitions from text",
    "example": "Illustrative examples mentioned in NCERT",
    "step": "Sequential steps, experiments, or procedures",
    "data": "Numeric or tabular info",
    "table": "Numeric or tabular info",
    "diagram": "Any labeled figure description",
    "label": "Any labeled figure description",
    "name": "Names of organisms, people, etc.",
    "unit": "Units of measurement"
}

# -----------------------------
# Regex Rules for each category
# -----------------------------
RULES = {
    "definition": [
        r'\b(?:[A-Z][a-z]{2,}\s)?(?:is|are|was|refers to|means|is defined as|can be defined as)\b.{10,150}?.',
        r'\bDefinition:\s?.{10,150}?.'
    ],
    "example": [
        r'(?:For example|e\.g\.|such as)\s.{5,120}?[.,]',
        r'\bExample:\s.{5,150}?.'
    ],
    "step": [
        r'\b(?:Step\s?\d+|First|Second|Third|Then|Next|Finally|In conclusion|Procedure)[,:]?\s.{10,150}?.'
    ],
    "data": [
        r'\b\d+(?:\.\d+)?\s?(?:kg|g|mg|cm|m|km|mm|µm|nm|s|ms|h|min|Hz|kHz|MHz|J|kJ|W|kW|V|A|Ω|°C|°F|mol|L|ml|%|N|Pa|atm)\b'
    ],
    "table": [
        r'\b\d+(?:\.\d+)?\s?(?:kg|g|mg|cm|m|km|mm|µm|nm|s|ms|h|min|Hz|kHz|MHz|J|kJ|W|kW|V|A|Ω|°C|°F|mol|L|ml|%|N|Pa|atm)\b'
    ],
    "diagram": [
        r'\b(?:Fig\.|Figure|Diagram|Label|Illustration).{5,100}?'
    ],
    "name": [
        r'\b([A-Z][a-z]{3,})\s([a-z]{3,})\b'
    ],
    "unit": [
        r'\b\d+(?:\.\d+)?\s?(?:kg|g|mg|cm|m|km|mm|µm|nm|s|ms|h|min|Hz|kHz|MHz|J|kJ|W|kW|V|A|Ω|°C|°F|mol|L|ml|%|N|Pa|atm)\b'
    ]
}

# -----------------------------
# Path builder for chapter
# -----------------------------
def get_chapter_file_path(book, chapter):
    folder_path = os.path.join("static", "highlights", book)
    os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, f"{chapter}.json")

# -----------------------------
# Load highlights
# -----------------------------
def load_data(book, chapter):
    path = get_chapter_file_path(book, chapter)
    print(f"📥 Loading highlights from: {path}")
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} highlights.")
            return data
        except Exception as e:
            print(f"❌ Error loading highlights: {e}")
            return []
    else:
        print("⚠️ File not found, returning empty list.")
        return []

# -----------------------------
# Save highlights to file
# -----------------------------
def save_data(book, chapter, highlights):
    path = get_chapter_file_path(book, chapter)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(highlights, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(highlights)} highlights to {path}")
    except Exception as e:
        print(f"❌ Error saving highlights: {e}")

# -----------------------------
# Junk detector function
# -----------------------------
def is_junk(text):
    junk_keywords = {
        "html", "head", "body", "div", "class", "span", "style", "script",
        "lang", "href", "meta", "link", "content", "http", "www", "doctype"
    }
    if len(text.strip()) < 3:
        return True
    if any(tag in text.lower() for tag in junk_keywords):
        return True
    if re.match(r'^[\W\d\s]+$', text.strip()):
        return True
    return False

# -----------------------------
# Save one detected highlight
# -----------------------------
def save_detected_highlight(book, chapter, text, start, end, category, page_number, match_id=None, rule_name=None, source=None):
    print(f"\n🖍️ Saving highlight → Book: {book}, Chapter: {chapter}, Page: {page_number}, Category: {category}")
    if is_junk(text):
        print(f"🚫 Skipped junk highlight: '{text}'")
        return
    highlights = load_data(book, chapter)
    category = category.strip().lower() if category else "definition"
    if category not in ALLOWED_CATEGORIES:
        print(f"⚠️ Category '{category}' not allowed, defaulting to 'definition'")
        category = "definition"
    entry = {
        "text": text.strip(),
        "start": int(start),
        "end": int(end),
        "category": category,
        "page_number": int(page_number)
    }
    if match_id: entry["match_id"] = match_id
    if rule_name: entry["rule_name"] = rule_name
    if source: entry["source"] = source
    if entry not in highlights:
        highlights.append(entry)
        save_data(book, chapter, highlights)
        print(f"✅ Highlight added: '{text}'")
    else:
        print(f"ℹ️ Highlight already exists: '{text}'")

# -----------------------------
# Remove a highlight
# -----------------------------
def remove_highlight(book, chapter, text, start, end, category, page_number):
    print(f"\n🧽 Removing highlight → Book: {book}, Chapter: {chapter}, Page: {page_number}, Category: {category}")
    highlights = load_data(book, chapter)
    target = {
        "text": text.strip(),
        "start": int(start),
        "end": int(end),
        "category": category.strip().lower(),
        "page_number": int(page_number)
    }
    new_highlights = [h for h in highlights if not (
        h.get("text") == target["text"] and
        h.get("start") == target["start"] and
        h.get("end") == target["end"] and
        h.get("category") == target["category"] and
        h.get("page_number") == target["page_number"]
    )]
    if len(new_highlights) < len(highlights):
        save_data(book, chapter, new_highlights)
        print("✅ Highlight removed.")
    else:
        print("⚠️ Highlight not found, skipping.")

# -----------------------------
# Get all highlights
# -----------------------------
def get_highlights(book, chapter, page_number=None, category=None):
    print(f"\n📌 Fetching highlights → Book: {book}, Chapter: {chapter}, Page: {page_number}, Category: {category}")
    highlights = load_data(book, chapter)
    if page_number is not None:
        page_number = int(page_number)
        highlights = [h for h in highlights if h.get("page_number") == page_number]
        print(f"📄 Filtered by page → {len(highlights)} items")
    if category is not None:
        category = category.strip().lower()
        highlights = [h for h in highlights if h.get("category") == category]
        print(f"🏷️ Filtered by category → {len(highlights)} items")
    page_list = [h.get("page_number") for h in highlights]
    print(f"📝 Current highlight page numbers: {page_list}")
    return highlights

# -----------------------------
# Detect highlights from text using regex rules
# -----------------------------
def detect_highlights(book, chapter, categories=None, page=None):
    highlights = []
    try:
        path = f'static/books/{book}/{chapter}.txt'
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"❌ Could not load chapter text: {e}")
        return highlights

    if categories is None:
        categories = list(RULES.keys())

    for category in categories:
        patterns = RULES.get(category, [])
        for rule in patterns:
            for match in re.finditer(rule, text, flags=re.DOTALL):
                match_text = match.group().strip()
                start = match.start()
                end = match.end()
                highlight = {
                    "text": match_text,
                    "start": start,
                    "end": end,
                    "category": category,
                    "page_number": page or 0,
                    "match_id": f"{category}_{start}_{end}",
                    "rule_name": rule,
                    "source": "rule"
                }
                highlights.append(highlight)
                print(f"🧠 Detected [{category}]: {match_text} | Page: {page or 0}")

    print(f"✅ Total {len(highlights)} highlights detected")
    return highlights



























            
