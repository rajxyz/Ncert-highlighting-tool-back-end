
import re
import json
from matcher import find_matches
from pdf_parser import extract_text_from_chapter
from pyqs import get_pyq_keywords

def extract_highlights(text):
    highlights = []

    # Definitions (simple heuristic based)
    def_patterns = [
        r'\b(is|are|was|means|refers to|is defined as)\b[^.]{10,100}\.',
        r'\bcan be defined as\b[^.]{10,100}\.',
    ]

    for pattern in def_patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        highlights.extend(matches)

    # Dates
    date_pattern = r'\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{2,4}\b'
    highlights.extend(re.findall(date_pattern, text))

    # Numbers (Units, Measurements, Years)
    num_pattern = r'\b\d+(?:\.\d+)?\s?(?:kg|g|m|cm|km|s|ms|Hz|J|W|Â°C|%)\b'
    highlights.extend(re.findall(num_pattern, text))

    # Terminologies (Capitalized technical words)
    term_pattern = r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b'
    highlights.extend(re.findall(term_pattern, text))

    # Examples
    ex_pattern = r'(?:for example|e\.g\.|such as)\s[^.]{5,100}'
    highlights.extend(re.findall(ex_pattern, text, flags=re.IGNORECASE))

    # Processes/Steps
    step_pattern = r'\b(Step \d+|Step-\d+|First,|Then,|Next,|Finally)\b[^.]{5,100}'
    highlights.extend(re.findall(step_pattern, text, flags=re.IGNORECASE))

    # Cause-Effect
    cause_pattern = r'\b(Because|Due to|As a result|Therefore|Hence)\b[^.]{5,100}'
    highlights.extend(re.findall(cause_pattern, text, flags=re.IGNORECASE))

    # Rules/Theories
    theory_pattern = r'\b(?:Law|Rule|Theory|Principle) of [A-Z][a-z]+\b'
    highlights.extend(re.findall(theory_pattern, text))

    # Abbreviations & Acronyms
    acronym_pattern = r'\b[A-Z]{2,}\b'
    highlights.extend(re.findall(acronym_pattern, text))

    # Lists
    list_pattern = r'\n?\d+\.\s[^\n]+|\n?-\s[^\n]+'
    highlights.extend(re.findall(list_pattern, text))

    # Foreign words (simple heuristic: italic-style placeholder)
    foreign_pattern = r'\b[A-Za-z]+(?:us|um|ae|es|is|on)\b'
    highlights.extend(re.findall(foreign_pattern, text))

    # Add previous year question keywords
    highlights.extend(get_pyq_keywords(text))

    # Deduplicate and clean
    cleaned = list(set(map(lambda x: x.strip().strip(','), highlights)))
    return cleaned

def auto_highlight_chapter(book, chapter):
    print(f"Auto-highlighting for: {book} - {chapter}")
    text = extract_text_from_chapter(book, chapter)
    print(f"Extracted text length: {len(text)}")

    highlighted = extract_highlights(text)
    print(f"Highlights found: {len(highlighted)}")

    return highlighted
