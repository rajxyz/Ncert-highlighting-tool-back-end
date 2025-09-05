import os
import json

# ────────────────────────────────────────────────
# File path helper
# ────────────────────────────────────────────────
def _get_highlight_file(book, chapter):
    folder_path = os.path.join("static", "highlights", book)
    os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, f"{chapter}.json")


# ────────────────────────────────────────────────
# Save highlight
# ────────────────────────────────────────────────
def save_detected_highlight(book, chapter, text, start=None, end=None,
                            category=None, page_number=0, match_id=None,
                            rule_name=None, source=None):
    """
    Save a new highlight entry into JSON file.
    """
    file_path = _get_highlight_file(book, chapter)

    highlights = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                highlights = json.load(f)
            except json.JSONDecodeError:
                highlights = []

    new_entry = {
        "text": text,
        "start": start,
        "end": end,
        "category": category,
        "page_number": page_number
