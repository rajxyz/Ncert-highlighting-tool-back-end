import json
import os

DATA_FILE = 'highlights_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_highlight(book, chapter, line):
    data = load_data()
    data.setdefault(book, {}).setdefault(chapter, []).append(line)
    save_data(data)

def remove_highlight(book, chapter, line):
    data = load_data()
    if book in data and chapter in data[book]:
        if line in data[book][chapter]:
            data[book][chapter].remove(line)
            save_data(data)
