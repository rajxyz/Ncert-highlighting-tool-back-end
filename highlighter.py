import json
import os
import re

# 🔧 Path builder for chapter
def get_chapter_file_path(book, chapter):
    folder_path = os.path.join("static", "highlights", book)
    os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, f"{chapter}.json")


# 📥 Load highlights
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


# 💾 Save highlights to file
def save_data(book, chapter, highlights):
    path = get_chapter_file_path(book, chapter)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(highlights, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(highlights)} highlights to {path}")
    except Exception as e:
        print(f"❌ Error saving highlights: {e}")


# ✅ Category Normalization
CATEGORY_ALIASES = {
    "name": {"name", "names", "Name", "Names"},
    "date": {"date", "dates", "Date", "Dates"},
    "definition": {"definition", "definitions", "Definition", "Definitions"},
    "term": {"term", "terms", "Term", "Terms"},
    "example": {"example", "examples", "Example", "Examples"},
    "terminology": {"terminology", "Terminology"},
    "important": {"important", "Important"},
}

def normalize_category(category):
    for base, variants in CATEGORY_ALIASES.items():
        if category in variants:
            return base  # always return normalized lowercase form
    return None


# 🖍️ Save one detected highlight (with metadata)
def save_detected_highlight(book, chapter, text, start, end, category, page_number, match_id=None, rule_name=None, source=None):
    print(f"\n🖍️ Saving highlight → Book: {book}, Chapter: {chapter}, Page: {page_number}, Category: {category}")
    highlights = load_data(book, chapter)

    # 🚫 Skip junk or HTML-like highlights
    if is_junk(text):
        print(f"🚫 Skipped junk highlight: '{text}'")
        return

    # ✅ Normalize category
    normalized_category = normalize_category(category.strip())
    if not normalized_category:
        print(f"⚠️ Invalid category '{category}', skipping highlight.")
        return

    entry = {
        "text": text.strip(),
        "start": int(start),
        "end": int(end),
        "category": normalized_category,
        "page_number": int(page_number),
    }

    if match_id is not None:
        entry["match_id"] = match_id
    if rule_name is not None:
        entry["rule_name"] = rule_name
    if source is not None:
        entry["source"] = source

    if entry not in highlights:
        highlights.append(entry)
        save_data(book, chapter, highlights)
        print(f"✅ Highlight added: '{text}' [{normalized_category}]")
    else:
        print(f"ℹ️ Highlight already exists: '{text}'")


# 🧽 Remove a highlight
def remove_highlight(book, chapter, text, start, end, category, page_number):
    print(f"\n🧽 Removing highlight → Book: {book}, Chapter: {chapter}, Page: {page_number}, Category: {category}")
    highlights = load_data(book, chapter)

    normalized_category = normalize_category(category.strip())
    if not normalized_category:
        print(f"⚠️ Invalid category '{category}', skipping removal.")
        return

    target = {
        "text": text.strip(),
        "start": int(start),
        "end": int(end),
        "category": normalized_category,
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


# 📌 Get all highlights (with optional filters)
def get_highlights(book, chapter, page_number=None, category=None):
    print(f"\n📌 Fetching highlights → Book: {book}, Chapter: {chapter}, Page: {page_number}, Category: {category}")
    highlights = load_data(book, chapter)

    if page_number is not None:
        page_number = int(page_number)
        highlights = [h for h in highlights if h.get("page_number") == page_number]
        print(f"📄 Filtered by page → {len(highlights)} items")

    if category is not None:
        normalized_category = normalize_category(category.strip())
        if normalized_category:
            highlights = [h for h in highlights if h.get("category") == normalized_category]
            print(f"🏷️ Filtered by category → {len(highlights)} items")
        else:
            print(f"⚠️ Invalid category filter '{category}'")

    return highlights


# 🚫 Junk detector function
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
