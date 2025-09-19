import os
import json

def save_detected_highlight(book, chapter, text, category, page_number, source):
    """
    Save a detected highlight to JSON file.
    Ensures folder and file exist. Adds book & chapter info to highlight.
    Prevents duplicate highlights.
    """
    text = (text or "").strip()
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
            highlights = data.get("highlights", [])
            print(f"[SAVE HIGHLIGHT] Loaded existing highlights: {len(highlights)} entries")
        except Exception as e:
            print(f"[WARN] Failed to load existing highlights: {e}")
            data = {"highlights": []}
            highlights = data["highlights"]
    else:
        print(f"[SAVE HIGHLIGHT] No existing highlight file found. Creating new.")
        data = {"highlights": []}
        highlights = data["highlights"]

    # Check for duplicate (match on text, category, page_number, source)
    for h in highlights:
        if (
            h.get("text") == text
            and h.get("category") == category
            and h.get("page_number") == page_number
            and h.get("source") == source
        ):
            print(f"[DEBUG SKIP DUPLICATE] Highlight already exists: '{text}' (Page {page_number})")
            return  # Don't save duplicate

    # Append new highlight
    entry = {
        "book": book,
        "chapter": chapter,
        "text": text,
        "category": category,
        "page_number": page_number,
        "source": source,
    }
    highlights.append(entry)

    # Save back to file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[SAVE HIGHLIGHT] Stored highlight: '{text}' (Page {page_number}) → {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save highlight: {e}")














