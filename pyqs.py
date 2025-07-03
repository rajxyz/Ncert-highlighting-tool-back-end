import json

def load_pyqs():
    with open('pyqs_data.json') as f:
        return json.load(f)

def get_pyq_matches(chapter_text):
    pyqs = load_pyqs()
    matches = []
    for q in pyqs:
        if q['keyword'].lower() in chapter_text.lower():
            matches.append(q)
    return matches
