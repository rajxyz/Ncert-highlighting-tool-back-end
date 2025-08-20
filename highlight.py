import json
import os
import re
from inflect import engine as inflect_engine

# ────────────────────────────────────────────────
# Inflect engine for singularization
# ────────────────────────────────────────────────
inflector = inflect_engine()

# ────────────────────────────────────────────────
# Path builder for chapter JSON
# ────────────────────────────────────────────────
def get_chapter_file_path(book, chapter):
    folder_path = os.path.join("static", "highlights", book)
    os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, f"{chapter}.json")

# ────────────────────────────────────────────────
# Load existing highlights
# ────────────────────────────────────────────────
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

# ────────────────────────────────────────────────
# Save highlights list to JSON
# ────────────────────────────────────────────────
def save_data(book, chapter, highlights):
    path = get_chapter_file_path(book, chapter)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(highlights, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(highlights)} highlights to {path}")
    except Exception as e:
        print(f"❌ Error saving highlights: {e}")

# ────────────────────────────────────────────────
# Normalize category: lowercase + singular
# ────────────────────────────────────────────────
def normalize_category(cat):
    cat = (cat or "unknown").strip().lower()
    singular = inflector.singular_noun(cat) or cat
    return singular

# ────────────────────────────────────────────────
# Junk detector
# ────────────────────────────────────────────────
def is_junk(text):
    junk_keywords = {
        "html", "head", "body", "div", "class", "span", "style", "script",
        "lang", "href", "meta", "link", "content", "http", "www", "doctype"
    }
    t = text.strip()
    if len(t) < 2:  # accept very short words if meaningful
        return True
    if any(tag in t.lower() for tag in junk_keywords):
        return True
    if re.match(r'^[\W\d\s]+$', t):
        return True
    return False

# ────────────────────────────────────────────────
# Save one detected highlight
# ────────────────────────────────────────────────
def save_detected_highlight(book, chapter, text, start, end, category, page_number, match_id=None, rule_name=None, source=None):
    category = normalize_category(category)
    print(f"\n🖍️ Saving highlight → Book: {book}, Chapter: {chapter}, Page: {page_number}, Category: {category}")
    
    highlights = load_data(book, chapter)

    # Skip junk
    if is_junk(text):
        print(f"🚫 Skipped junk highlight: '{text}'")
        return

    entry = {
        "text": text.strip(),
        "start": int(start),
        "end": int(end),
        "category": category,
        "page_number": int(page_number),
    }

    if match_id: entry["match_id"] = match_id
    if rule_name: entry["rule_name"] = rule_name
    if source: entry["source"] = source

    # Avoid duplicates
    key = (entry["text"], entry["category"], entry["page_number"])
    if any((h["text"], h["category"], h["page_number"]) == key for h in highlights):
        print(f"ℹ️ Highlight already exists: '{text}'")
        return

    highlights.append(entry)
    save_data(book, chapter, highlights)
    print(f"✅ Highlight added: '{text}'")

# ────────────────────────────────────────────────
# Remove a highlight
# ────────────────────────────────────────────────
def remove_highlight(book, chapter, text, start, end, category, page_number):
    category = normalize_category(category)
    print(f"\n🧽 Removing highlight → Book: {book}, Chapter: {chapter}, Page: {page_number}, Category: {category}")
    
    highlights = load_data(book, chapter)
    new_highlights = [h for h in highlights if not (
        h["text"] == text.strip() and
        h["start"] == int(start) and
        h["end"] == int(end) and
        h["category"] == category and
        h["page_number"] == int(page_number)
    )]

    if len(new_highlights) < len(highlights):
        save_data(book, chapter, new_highlights)
        print("✅ Highlight removed.")
    else:
        print("⚠️ Highlight not found, skipping.")

# ────────────────────────────────────────────────
# Get all highlights (optional filters)
# ────────────────────────────────────────────────
def get_highlights(book, chapter, page_number=None, category=None):
    highlights = load_data(book, chapter)

    if page_number is not None:
        page_number = int(page_number)
        highlights = [h for h in highlights if h["page_number"] == page_number]

    if category is not None:
        category = normalize_category(category)
        highlights = [h for h in highlights if h["category"] == category]

    return highlights













































