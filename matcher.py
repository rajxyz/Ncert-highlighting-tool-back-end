from difflib import SequenceMatcher

def match_lines(text_lines, pyq_keywords):
    matches = []
    for line in text_lines:
        for keyword in pyq_keywords:
            if keyword.lower() in line.lower():
                matches.append(line)
    return matches,
