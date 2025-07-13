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


# 🖍️ Save a single highlight using text (auto detect start/end)
def save_highlight(book, chapter, full_text, highlighted_text, category):
    print(f"\n🖍️ Saving highlight → Book: {book}, Chapter: {chapter}, Category: {category}")
    highlights = load_data(book, chapter)

    # Use regex to find all case-insensitive matches
    pattern = re.compile(re.escape(highlighted_text), re.IGNORECASE)
    matches = list(pattern.finditer(full_text))

    if not matches:
        print("⚠️ Highlighted text not found in full_text.")
        return

    # Use first match
    match = matches[0]
    start_index = match.start()
    end_index = match.end()

    entry = {
        "text": highlighted_text.strip(),
        "start": start_index,
        "end": end_index,
        "category": category.strip()
    }

    if entry not in highlights:
        highlights.append(entry)
        save_data(book, chapter, highlights)
        print("✅ Highlight added.")
    else:
        print("ℹ️ Highlight already exists, skipping.")


# 🧽 Remove a highlight
def remove_highlight(book, chapter, text, start, end, category):
    print(f"\n🧽 Removing highlight → Book: {book}, Chapter: {chapter}, Category: {category}")
    highlights = load_data(book, chapter)

    entry = {
        "text": text.strip(),
        "start": start,
        "end": end,
        "category": category.strip()
    }

    if entry in highlights:
        highlights.remove(entry)
        save_data(book, chapter, highlights)
        print("✅ Highlight removed.")
    else:
        print("⚠️ Highlight not found, skipping.")


# 📌 Get all highlights
def get_highlights(book, chapter):
    print(f"\n📌 Fetching highlights → Book: {book}, Chapter: {chapter}")
    highlights = load_data(book, chapter)
    print(f"📦 Found {len(highlights)} highlights.")
    return highlights
