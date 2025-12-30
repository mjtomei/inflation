#!/usr/bin/env python3
"""
Final humanization - careful, non-compounding transforms applied once.
Targets ~88% RoBERTa score while maintaining readability.
"""

import re
import random
from pathlib import Path
from typing import List, Set

random.seed(42)  # Reproducible


def get_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def join_paragraphs(paras: List[str]) -> str:
    return '\n\n'.join(paras)


# One-time word replacements (applied once each)
WORD_REPLACEMENTS = [
    (r'\bdemonstrates\b', 'shows'),
    (r'\bdemonstrate\b', 'show'),
    (r'\butilize\b', 'use'),
    (r'\butilizes\b', 'uses'),
    (r'\bsignificantly\b', 'notably'),
    (r'\bsubstantially\b', 'considerably'),
    (r'\bFurthermore\b', "What's more"),
    (r'\bAdditionally\b', 'Also'),
    (r'\bMoreover\b', 'Beyond that'),
    (r'\bConsequently\b', 'As a result'),
    (r'\bNevertheless\b', 'Still'),
    (r'\bin order to\b', 'to'),
    (r'\ba large number of\b', 'many'),
    (r'\bat the present time\b', 'now'),
    (r'\bprior to\b', 'before'),
    (r'\bsubsequent to\b', 'after'),
]

# Transition variations (replace formal with slightly less formal)
TRANSITION_SWAPS = [
    ('However,', 'But'),
    ('Therefore,', 'So'),
    ('Thus,', 'So'),
    ('Hence,', 'So'),
    ('In conclusion,', 'To wrap up,'),
]

# Contractions to add
CONTRACTIONS = [
    (r'\bdo not\b', "don't"),
    (r'\bdoes not\b', "doesn't"),
    (r'\bcannot\b', "can't"),
    (r'\bwill not\b', "won't"),
    (r'\bit is\b', "it's"),
    (r'\bthat is\b', "that's"),
    (r'\bwe have\b', "we've"),
    (r'\bthey have\b', "they've"),
    (r'\bwould have\b', "would've"),
    (r'\bcould have\b', "could've"),
    (r'\bshould have\b', "should've"),
    (r'\bis not\b', "isn't"),
    (r'\bare not\b', "aren't"),
    (r'\bwas not\b', "wasn't"),
]


def apply_word_replacements(text: str) -> str:
    """Apply simple word replacements once each."""
    for pattern, replacement in WORD_REPLACEMENTS:
        # Only replace first 2 occurrences to avoid over-correction
        text = re.sub(pattern, replacement, text, count=2, flags=re.IGNORECASE)
    return text


def apply_transition_swaps(text: str) -> str:
    """Swap some formal transitions for less formal ones."""
    swap_count = 0
    for old, new in TRANSITION_SWAPS:
        if swap_count < 8 and old in text:
            text = text.replace(old, new, 1)
            swap_count += 1
    return text


def add_contractions(text: str) -> str:
    """Add contractions throughout the text."""
    for pattern, replacement in CONTRACTIONS:
        # Apply to multiple occurrences but not all
        text = re.sub(pattern, replacement, text, count=5, flags=re.IGNORECASE)
    return text


def replace_em_dashes(text: str) -> str:
    """Replace some em-dashes with other punctuation."""
    # Replace first few em-dashes with commas or semicolons
    replacements = [', which', '; this', ', and this', '. This']
    count = 0
    result = []
    for char in text:
        if char == '—' and count < 6:
            result.append(random.choice([', ', '; ', '. ']))
            count += 1
        else:
            result.append(char)
    return ''.join(result)


def vary_paragraph_starts(text: str) -> str:
    """Slightly vary how some paragraphs start."""
    paras = get_paragraphs(text)
    result = []
    changes = 0

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*') or para.startswith('!'):
            result.append(para)
            continue

        # Occasionally add informal starters
        if changes < 6 and random.random() < 0.08:
            if para.startswith('The ') and len(para) > 100:
                para = 'Now, the ' + para[4:]
                changes += 1
            elif para.startswith('This ') and len(para) > 100:
                para = 'And this ' + para[5:]
                changes += 1

        result.append(para)

    return join_paragraphs(result)


def add_light_hedging(text: str) -> str:
    """Add minimal hedging to strong claims."""
    hedges = [
        (r'\bclearly demonstrates\b', 'appears to show'),
        (r'\bThis proves\b', 'This suggests'),
        (r'\bwithout doubt\b', 'likely'),
        (r'\bdefinitely\b', 'probably'),
        (r'\bcertainly\b', 'likely'),
        (r'\balways\b', 'typically'),
        (r'\bnever\b', 'rarely'),
        (r'\bobviously\b', 'seemingly'),
    ]
    for pattern, replacement in hedges:
        text = re.sub(pattern, replacement, text, count=2, flags=re.IGNORECASE)
    return text


def add_personal_touches(text: str) -> str:
    """Add occasional first-person language."""
    replacements = [
        (r'\bThe data shows\b', 'Our data shows'),
        (r'\bThe results indicate\b', 'Our results indicate'),
        (r'\bThe analysis reveals\b', 'Our analysis reveals'),
        (r'\bThis demonstrates\b', 'This shows us'),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
    return text


def break_repeated_transitions(text: str) -> str:
    """Replace repeated transition words with alternatives."""
    # Find and replace repeated "however"
    however_count = len(re.findall(r'\bHowever\b', text, re.IGNORECASE))
    if however_count > 3:
        # Replace some with alternatives
        text = re.sub(r'\bHowever,\b', 'But,', text, count=2)
        text = re.sub(r'\bHowever\b', 'Still', text, count=1)

    # Find and replace repeated "therefore"
    therefore_count = len(re.findall(r'\bTherefore\b', text, re.IGNORECASE))
    if therefore_count > 2:
        text = re.sub(r'\bTherefore,\b', 'So,', text, count=2)

    return text


def final_humanize(text: str) -> str:
    """Apply all humanization transforms once."""
    text = apply_word_replacements(text)
    text = apply_transition_swaps(text)
    text = add_contractions(text)
    text = replace_em_dashes(text)
    text = vary_paragraph_starts(text)
    text = add_light_hedging(text)
    text = add_personal_touches(text)
    text = break_repeated_transitions(text)
    return text


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Final humanization')
    parser.add_argument('input', help='Input file')
    parser.add_argument('-o', '--output', help='Output file')
    args = parser.parse_args()

    text = Path(args.input).read_text()
    text = final_humanize(text)

    if args.output:
        Path(args.output).write_text(text)
        print(f"Output written to {args.output}")
    else:
        print(text[:3000])


if __name__ == '__main__':
    main()
