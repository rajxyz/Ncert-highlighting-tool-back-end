import os
import json

def save_detected_highlight(book, chapter, text, category, page_number, source):
    """
    Save a detected highlight to JSON file.
    Ensures folder and file exist. Adds book & chapter info to highlight.
    """
    text = text.strip()
    print(f"[SAVE HIGHLIGHT] Attempting to save: '{text}' (Category: {category}, Page: {page_number})")

    # Create folder if not exists
    folder = os.path.join("static", "highlights", book.strip())
    os.makedirs(folder, exist_ok=True)
    print(f"[SAVE HIGHLIGHT] Ensured folder exists: {folder}")

    # File path for the chapter highlights
    file_path = os.path.join(folder, f"{chapter.strip()}.json")

    # Load existing highlights if file exists
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[SAVE HIGHLIGHT] Loaded existing highlights: {len(data.get('highlights', []))} entries")
        except Exception as e:
            print(f"[WARN] Failed to load existing highlights: {e}")
            data = {"highlights": []}
    else:
        print(f"[SAVE HIGHLIGHT] No existing highlight file found. Creating new.")
        data = {"highlights": []}

    # Append new highlight
    data["highlights"].append({
        "book": book,
        "chapter": chapter,
        "text": text,
        "category": category,
        "page_number": page_number,
        "source": source
    })

    # Save back to file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[SAVE HIGHLIGHT] Stored highlight: '{text}' → {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save highlight: {e}")






