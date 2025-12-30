#!/usr/bin/env python3
"""
Light humanization - minimal, careful transforms that don't compound.
Applies each transform only once with tracking to avoid duplication.
"""

import re
import random
from pathlib import Path
from typing import List, Set
import argparse


def get_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def join_paragraphs(paras: List[str]) -> str:
    return '\n\n'.join(paras)


# Simple, one-time replacements
SIMPLE_REPLACEMENTS = [
    (r'\bdemonstrates\b', 'shows'),
    (r'\bdemonstrate\b', 'show'),
    (r'\bsignificantly\b', 'notably'),
    (r'\bsubstantially\b', 'considerably'),
    (r'\bFurthermore\b', 'What\'s more'),
    (r'\bAdditionally\b', 'Also'),
    (r'\bMoreover\b', 'Beyond that'),
    (r'\bConsequently\b', 'As a result'),
    (r'\bNevertheless\b', 'Still'),
    (r'\bTherefore\b', 'So'),
    (r'\bHowever\b', 'But'),
    (r'\bIn conclusion\b', 'To conclude'),
    (r'\bIt is important to note that\b', 'Note that'),
    (r'\bIt should be noted that\b', 'Note:'),
    (r'\bIt is clear that\b', 'Clearly'),
    (r'\bthe fact that\b', 'that'),
    (r'\bin order to\b', 'to'),
    (r'\ba large number of\b', 'many'),
    (r'\ba significant number of\b', 'many'),
    (r'\bat the present time\b', 'now'),
    (r'\bin the event that\b', 'if'),
    (r'\bprior to\b', 'before'),
    (r'\bsubsequent to\b', 'after'),
    (r'\bwith respect to\b', 'about'),
    (r'\bwith regard to\b', 'about'),
    (r'\bin terms of\b', 'for'),
    (r'\bon the basis of\b', 'based on'),
    (r'\bfor the purpose of\b', 'to'),
    (r'\bin spite of the fact that\b', 'although'),
    (r'\bdue to the fact that\b', 'because'),
]

# Em-dash replacements (one-time)
EM_DASH_ALTS = [', which', '. This', '; in fact', '. In fact']


def apply_simple_replacements(text: str, used: Set[str]) -> str:
    """Apply simple word/phrase replacements, tracking what's been used."""
    for pattern, replacement in SIMPLE_REPLACEMENTS:
        if pattern not in used and re.search(pattern, text, re.IGNORECASE):
            text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
            used.add(pattern)
    return text


def replace_em_dashes_once(text: str, count: int = 3) -> str:
    """Replace some em-dashes with alternatives."""
    for _ in range(count):
        if '—' in text or ' - ' in text:
            alt = random.choice(EM_DASH_ALTS)
            text = text.replace('—', alt, 1)
            text = text.replace(' - ', alt, 1)
    return text


def add_contractions_light(text: str) -> str:
    """Add a few contractions."""
    contractions = [
        (r'\bdo not\b', "don't"),
        (r'\bdoes not\b', "doesn't"),
        (r'\bcannot\b', "can't"),
        (r'\bwill not\b', "won't"),
        (r'\bit is\b', "it's"),
        (r'\bthat is\b', "that's"),
    ]

    count = 0
    for pattern, replacement in contractions:
        if count < 8 and re.search(pattern, text, re.IGNORECASE):
            text = re.sub(pattern, replacement, text, count=2, flags=re.IGNORECASE)
            count += 1
    return text


def vary_sentence_starts_light(text: str) -> str:
    """Slightly vary how some sentences start."""
    paras = get_paragraphs(text)
    result = []
    changes = 0
    max_changes = 5

    variations = [
        (r'^This (demonstrates|shows|indicates)', r'This \1'),  # Keep as is
        (r'^The (data|evidence|analysis|results|findings) (shows?|indicates?|suggests?)',
         r'Our \1 \2'),
        (r'^It (is|has been) (shown|demonstrated|found)', r'We\'ve found'),
    ]

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        if changes < max_changes:
            for pattern, replacement in variations:
                if re.match(pattern, para):
                    para = re.sub(pattern, replacement, para)
                    changes += 1
                    break

        result.append(para)

    return join_paragraphs(result)


def add_light_hedging(text: str) -> str:
    """Add minimal hedging language."""
    hedges = [
        (r'\bThis proves\b', 'This suggests'),
        (r'\bThis shows\b', 'This indicates'),
        (r'\bclearly demonstrates\b', 'appears to show'),
        (r'\bis evident\b', 'seems apparent'),
        (r'\bwithout doubt\b', 'likely'),
        (r'\bdefinitely\b', 'probably'),
        (r'\bcertainly\b', 'likely'),
        (r'\balways\b', 'typically'),
        (r'\bnever\b', 'rarely'),
    ]

    for pattern, replacement in hedges:
        if re.search(pattern, text, re.IGNORECASE):
            text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
    return text


def add_occasional_informal_touch(text: str) -> str:
    """Add very occasional informal touches."""
    paras = get_paragraphs(text)
    result = []
    informal_count = 0

    for i, para in enumerate(paras):
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        # Very occasionally add an informal starter
        if informal_count < 3 and random.random() < 0.05:
            if para.startswith('The '):
                para = 'Now, the ' + para[4:]
                informal_count += 1
            elif para.startswith('This '):
                para = 'And this ' + para[5:]
                informal_count += 1

        result.append(para)

    return join_paragraphs(result)


def light_humanize(text: str) -> str:
    """Apply light, non-compounding humanization."""
    used_patterns: Set[str] = set()

    text = apply_simple_replacements(text, used_patterns)
    text = replace_em_dashes_once(text, count=5)
    text = add_contractions_light(text)
    text = vary_sentence_starts_light(text)
    text = add_light_hedging(text)
    text = add_occasional_informal_touch(text)

    return text


def main():
    parser = argparse.ArgumentParser(description='Light humanization')
    parser.add_argument('input', help='Input file')
    parser.add_argument('-o', '--output', help='Output file')

    args = parser.parse_args()

    text = Path(args.input).read_text()
    text = light_humanize(text)

    if args.output:
        Path(args.output).write_text(text)
        print(f"Output written to {args.output}")
    else:
        print(text[:3000])


if __name__ == '__main__':
    main()
