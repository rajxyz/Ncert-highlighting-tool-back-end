import json
import os

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


# 🖍️ Save one detected highlight (assumes start–end is already given)
def save_detected_highlight(book, chapter, text, start, end, category):
    print(f"\n🖍️ Saving highlight → Book: {book}, Chapter: {chapter}, Category: {category}")
    highlights = load_data(book, chapter)

    entry = {
        "text": text.strip(),
        "start": int(start),
        "end": int(end),
        "category": category.strip()
    }

    if entry not in highlights:
        highlights.append(entry)
        save_data(book, chapter, highlights)
        print(f"✅ Highlight added: '{text}'")
    else:
        print(f"ℹ️ Highlight already exists: '{text}'")


# 🧽 Remove a highlight
def remove_highlight(book, chapter, text, start, end, category):
    print(f"\n🧽 Removing highlight → Book: {book}, Chapter: {chapter}, Category: {category}")
    highlights = load_data(book, chapter)

    entry = {
        "text": text.strip(),
        "start": int(start),
        "end": int(end),
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
