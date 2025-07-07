import json
import os

DATA_FILE = 'highlights_data.json'

def load_data():
    print("📥 Loading data from file...")
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Data loaded successfully: {len(data)} books found")
                return data
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return {}
    print("⚠️ No data file found, returning empty structure.")
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            print("💾 Data saved successfully.")
    except Exception as e:
        print(f"❌ Error saving data: {e}")

def save_highlight(book, chapter, text, category):
    print(f"\n🖍️ Saving highlight → Book: {book}, Chapter: {chapter}, Category: {category}, Text: {text}")

    data = load_data()
    data.setdefault(book, {}).setdefault(chapter, [])

    entry = {"text": text, "category": category}

    if entry not in data[book][chapter]:
        data[book][chapter].append(entry)
        print(f"✅ Highlight added: {entry}")
        save_data(data)
    else:
        print(f"ℹ️ Highlight already exists, skipping: {entry}")

def remove_highlight(book, chapter, text, category):
    print(f"\n🧽 Removing highlight → Book: {book}, Chapter: {chapter}, Category: {category}, Text: {text}")

    data = load_data()
    entry = {"text": text, "category": category}

    if book in data and chapter in data[book]:
        if entry in data[book][chapter]:
            data[book][chapter].remove(entry)
            print("✅ Highlight removed.")
            save_data(data)
        else:
            print("⚠️ Highlight entry not found in chapter list.")
    else:
        print("⚠️ Book or chapter not found in existing data.")

def get_highlights(book, chapter):
    print(f"\n📌 Fetching highlights → Book: {book}, Chapter: {chapter}")
    data = load_data()
    highlights = data.get(book, {}).get(chapter, [])
    print(f"📦 Found {len(highlights)} highlights.")
    return highlights
