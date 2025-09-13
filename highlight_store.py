import os
import json

def save_detected_highlight(book, chapter, text, category, page_number, source, start=None, end=None):
    """
    Save a detected highlight to a JSON file.
    Ensures folder and file exist. Adds book & chapter info, including start/end positions.
    """
    # Create folder if it doesn't exist
    folder = os.path.join("static", "highlights", book.strip())
    os.makedirs(folder, exist_ok=True)

    # File path for the chapter highlights
    file_path = os.path.join(folder, f"{chapter.strip()}.json")

    # Load existing highlights if file exists
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "highlights" not in data:
                    data["highlights"] = []
        except Exception as e:
            print(f"[WARN] Failed to load existing highlights: {e}")
            data = {"highlights": []}
    else:
        data = {"highlights": []}

    # Append new highlight
    data["highlights"].append({
        "book": book,
        "chapter": chapter,
        "text": text,
        "category": category,
        "page_number": page_number,
        "source": source,
        "start": start,
        "end": end
    })

    # Save back to file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[SAVE] Highlight stored: '{text}' (Page {page_number}) → {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save highlight: {e}")
