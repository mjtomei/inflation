#!/usr/bin/env python3
"""
Combined humanization approach - merges aggressive transforms with perplexity manipulation.
Also adds more fundamental sentence restructuring.
"""

import re
import random
from pathlib import Path
from typing import List
import argparse

# Import from other modules
from aggressive_humanize import (
    aggressive_word_replace, replace_em_dashes_aggressive,
    add_contractions, vary_sentence_structure, add_hedges_and_uncertainty,
    add_filler_words, break_parallel_structure
)
from perplexity_humanize import (
    replace_with_uncommon, add_unusual_starters,
    invert_sentence_structure, add_hedging_variety
)


def get_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def join_paragraphs(paras: List[str]) -> str:
    return '\n\n'.join(paras)


# Additional restructuring patterns
CLAUSE_SWAPS = [
    # Move "because X" to front as "Since X,"
    (r'([^.]+)\s+because\s+([^.]+)\.', r'Since \2, \1.'),
    # Move "although X" clauses
    (r'([^.]+),?\s+although\s+([^.]+)\.', r'Although \2, \1.'),
    # Move "while X" clauses
    (r'([^.]+),?\s+while\s+([^.]+)\.', r'While \2, \1.'),
]

# Active/passive voice patterns
VOICE_SWAPS = [
    (r'(\w+) is measured by (\w+)', r'\2 measures \1'),
    (r'(\w+) are measured by (\w+)', r'\2 measure \1'),
    (r'(\w+) is calculated using (\w+)', r'\2 calculates \1'),
    (r'(\w+) is determined by (\w+)', r'\2 determines \1'),
    (r'(\w+) was found to be', r'\1 turned out'),
    (r'it can be seen that', r'we see that'),
    (r'it should be noted that', r'note that'),
    (r'it is important to', r'importantly,'),
]

# Sentence combining/splitting patterns
COMBINE_PATTERNS = [
    # Two short sentences about same subject -> one with semicolon
    (r'(\w+) (is|are) (\w+)\. (\1) (also )?(\w+)', r'\1 \2 \3; \4 \6'),
]

# Human-like sentence fragments
FRAGMENTS = [
    "Not entirely.",
    "Worth noting.",
    "A key point.",
    "Debatable, perhaps.",
    "More on this later.",
    "Fair enough.",
    "To a degree.",
]

# Rhetorical questions (humans use these more)
RHETORICAL_QUESTIONS = [
    "Why does this matter?",
    "What explains this?",
    "How significant is this?",
    "But is this accurate?",
]


def swap_clause_order(text: str, intensity: float) -> str:
    """Swap clause order for variety."""
    for pattern, replacement in CLAUSE_SWAPS:
        if random.random() < intensity * 0.15:
            text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
    return text


def swap_voice(text: str, intensity: float) -> str:
    """Swap between active and passive voice."""
    for pattern, replacement in VOICE_SWAPS:
        if random.random() < intensity * 0.2:
            text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
    return text


def add_rhetorical_elements(text: str, intensity: float) -> str:
    """Add rhetorical questions and fragments."""
    paras = get_paragraphs(text)
    result = []

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', para)
        new_sentences = []

        for i, sent in enumerate(sentences):
            new_sentences.append(sent)

            # Occasionally add a rhetorical question after a statement
            if i > 0 and random.random() < intensity * 0.05:
                new_sentences.append(random.choice(RHETORICAL_QUESTIONS))

            # Occasionally add a fragment
            if random.random() < intensity * 0.03:
                new_sentences.append(random.choice(FRAGMENTS))

        result.append(' '.join(new_sentences))

    return join_paragraphs(result)


def vary_paragraph_starts(text: str, intensity: float) -> str:
    """Vary how paragraphs start - AI tends to be formulaic."""
    paras = get_paragraphs(text)
    result = []

    informal_starts = [
        ("The ", "Now, the "),
        ("This ", "So this "),
        ("These ", "All these "),
        ("In ", "Looking at "),
        ("For ", "As for "),
        ("However", "Still"),
        ("Therefore", "So"),
        ("Additionally", "Plus"),
        ("Furthermore", "What's more"),
        ("Moreover", "On top of that"),
    ]

    for i, para in enumerate(paras):
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        # Vary some paragraph starts
        if i > 0 and random.random() < intensity * 0.25:
            for old, new in informal_starts:
                if para.startswith(old):
                    para = new + para[len(old):]
                    break

        result.append(para)

    return join_paragraphs(result)


def add_personal_touches(text: str, intensity: float) -> str:
    """Add first-person and personal language."""
    replacements = [
        (r'\bOne can see that\b', 'We can see that'),
        (r'\bIt is clear that\b', 'Clearly'),
        (r'\bThe data shows\b', 'Our data shows'),
        (r'\bThe results indicate\b', 'Our results indicate'),
        (r'\bThe analysis reveals\b', 'Our analysis reveals'),
        (r'\bThe evidence suggests\b', 'The evidence we gathered suggests'),
        (r'\bThis indicates\b', 'This tells us'),
        (r'\bThis suggests\b', 'This hints'),
        (r'\bThis demonstrates\b', 'This shows us'),
    ]

    for pattern, replacement in replacements:
        if random.random() < intensity * 0.3:
            text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)

    return text


def break_monotony(text: str, intensity: float) -> str:
    """Break monotonous patterns that AI tends to create."""
    # Replace repeated transition words
    transitions = ['however', 'therefore', 'moreover', 'furthermore', 'additionally']

    for trans in transitions:
        pattern = rf'\b{trans}\b'
        matches = list(re.finditer(pattern, text, re.IGNORECASE))

        if len(matches) > 2:
            # Replace some occurrences with alternatives
            alts = {
                'however': ['but', 'yet', 'still', 'though'],
                'therefore': ['so', 'thus', 'hence', 'accordingly'],
                'moreover': ['also', 'plus', 'besides', 'and'],
                'furthermore': ['and', 'also', 'in addition', 'as well'],
                'additionally': ['also', 'plus', 'and', 'as well'],
            }

            for match in matches[1:]:  # Keep first one
                if random.random() < intensity * 0.5:
                    alt = random.choice(alts.get(trans.lower(), ['also']))
                    start, end = match.span()
                    # Preserve case
                    if text[start].isupper():
                        alt = alt.capitalize()
                    text = text[:start] + alt + text[end:]

    return text


def combined_humanize(text: str, intensity: float = 0.5) -> str:
    """Apply all humanization transforms."""
    # Aggressive transforms
    text = aggressive_word_replace(text, intensity * 0.7)
    text = replace_em_dashes_aggressive(text, intensity)
    text = add_contractions(text, intensity * 0.8)
    text = vary_sentence_structure(text, intensity * 0.6)
    text = add_hedges_and_uncertainty(text, intensity * 0.5)
    text = break_parallel_structure(text, intensity * 0.5)

    # Perplexity transforms
    text = replace_with_uncommon(text, intensity * 0.5)
    text = add_unusual_starters(text, intensity * 0.4)
    text = invert_sentence_structure(text, intensity * 0.5)
    text = add_hedging_variety(text, intensity * 0.4)

    # New structural transforms
    text = swap_clause_order(text, intensity * 0.6)
    text = swap_voice(text, intensity * 0.5)
    text = add_rhetorical_elements(text, intensity * 0.4)
    text = vary_paragraph_starts(text, intensity * 0.6)
    text = add_personal_touches(text, intensity * 0.5)
    text = break_monotony(text, intensity * 0.7)

    return text


def main():
    parser = argparse.ArgumentParser(description='Combined humanization')
    parser.add_argument('input', help='Input file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-i', '--intensity', type=float, default=0.5)
    parser.add_argument('-n', '--iterations', type=int, default=1)

    args = parser.parse_args()

    text = Path(args.input).read_text()

    for i in range(args.iterations):
        text = combined_humanize(text, args.intensity)
        print(f"Iteration {i+1} complete")

    if args.output:
        Path(args.output).write_text(text)
        print(f"Output written to {args.output}")
    else:
        print(text[:2000])


if __name__ == '__main__':
    main()
