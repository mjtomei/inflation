#!/usr/bin/env python3
"""
Perplexity-based humanization.

AI detectors often look at perplexity - how "surprising" the text is.
AI text tends to be low perplexity (very predictable).
Human text has higher perplexity (more surprising word choices).

This script tries to increase perplexity by:
1. Using less common synonyms
2. Unusual but grammatical constructions
3. Varying sentence rhythm dramatically
"""

import re
import random
from pathlib import Path
from typing import List
import argparse

# Uncommon but valid synonyms (higher perplexity)
UNCOMMON_SYNONYMS = {
    'significant': ['appreciable', 'consequential', 'non-trivial', 'marked'],
    'important': ['salient', 'germane', 'material', 'pivotal'],
    'show': ['evince', 'manifest', 'betray', 'bespeak'],
    'shows': ['evinces', 'manifests', 'betrays', 'bespeaks'],
    'demonstrate': ['evince', 'instantiate', 'exemplify', 'attest'],
    'large': ['sizeable', 'appreciable', 'pronounced', 'non-negligible'],
    'small': ['modest', 'marginal', 'negligible', 'slight'],
    'increase': ['uptick', 'escalation', 'surge', 'climb'],
    'decrease': ['downtick', 'contraction', 'dip', 'slide'],
    'change': ['shift', 'alteration', 'modification', 'adjustment'],
    'problem': ['wrinkle', 'snag', 'complication', 'hitch'],
    'result': ['upshot', 'consequence', 'aftermath', 'sequela'],
    'because': ['inasmuch as', 'given that', 'seeing as', 'owing to'],
    'however': ['that said', 'be that as it may', 'even so', 'still'],
    'therefore': ['accordingly', 'hence', 'thus', 'ergo'],
    'also': ['likewise', 'moreover', 'too', 'as well'],
    'very': ['exceedingly', 'remarkably', 'decidedly', 'uncommonly'],
    'good': ['sound', 'solid', 'creditable', 'serviceable'],
    'bad': ['problematic', 'suboptimal', 'wanting', 'deficient'],
    'new': ['novel', 'fresh', 'emergent', 'nascent'],
    'old': ['longstanding', 'established', 'entrenched', 'venerable'],
    'many': ['numerous', 'myriad', 'manifold', 'sundry'],
    'few': ['scant', 'sparse', 'meager', 'limited'],
    'often': ['frequently', 'regularly', 'routinely', 'habitually'],
    'always': ['invariably', 'unfailingly', 'without exception', 'consistently'],
    'never': ['at no point', 'under no circumstances', 'not once'],
    'think': ['reckon', 'surmise', 'suspect', 'gather'],
    'believe': ['hold', 'maintain', 'contend', 'posit'],
    'suggest': ['intimate', 'hint', 'imply', 'insinuate'],
    'find': ['discern', 'ascertain', 'uncover', 'detect'],
    'use': ['employ', 'utilize', 'leverage', 'harness'],
    'make': ['render', 'fashion', 'forge', 'craft'],
    'get': ['obtain', 'procure', 'secure', 'acquire'],
    'help': ['aid', 'assist', 'facilitate', 'abet'],
    'try': ['endeavor', 'attempt', 'seek', 'strive'],
    'need': ['require', 'necessitate', 'call for', 'demand'],
    'want': ['desire', 'wish', 'seek', 'covet'],
    'people': ['folks', 'individuals', 'persons', 'parties'],
    'thing': ['matter', 'affair', 'item', 'element'],
    'way': ['manner', 'fashion', 'mode', 'approach'],
    'time': ['juncture', 'point', 'moment', 'instance'],
    'year': ['annum', 'twelvemonth', 'calendar year'],
    'different': ['distinct', 'disparate', 'divergent', 'varied'],
    'same': ['identical', 'selfsame', 'equivalent', 'tantamount'],
}

# Unusual sentence starters
UNUSUAL_STARTERS = [
    "Tellingly, ",
    "Curiously, ",
    "Notably, ",
    "Strikingly, ",
    "Instructively, ",
    "Revealingly, ",
    "Symptomatically, ",
    "Pointedly, ",
    "Conspicuously, ",
    "Peculiarly, ",
]

# Parenthetical insertions (increase surprise)
PARENTHETICALS = [
    " -- and this bears emphasis -- ",
    " (a point worth dwelling on) ",
    " -- crucially -- ",
    " (to put it plainly) ",
    " -- and here's the rub -- ",
    " (lest we forget) ",
    " -- pace the skeptics -- ",
    " (for what it's worth) ",
]


def get_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def join_paragraphs(paras: List[str]) -> str:
    return '\n\n'.join(paras)


def replace_with_uncommon(text: str, intensity: float) -> str:
    """Replace common words with less common synonyms."""
    for common, uncommons in UNCOMMON_SYNONYMS.items():
        if random.random() < intensity * 0.3:
            pattern = re.compile(r'\b' + common + r'\b', re.IGNORECASE)
            def replacer(m):
                replacement = random.choice(uncommons)
                if m.group(0)[0].isupper():
                    return replacement.capitalize()
                return replacement
            text = pattern.sub(replacer, text, count=2)
    return text


def add_unusual_starters(text: str, intensity: float) -> str:
    """Add unusual sentence starters to increase surprise."""
    paras = get_paragraphs(text)
    result = []

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', para)
        new_sentences = []

        for i, sent in enumerate(sentences):
            # Add unusual starter occasionally
            if i > 0 and random.random() < intensity * 0.08:
                starter = random.choice(UNUSUAL_STARTERS)
                sent = starter + sent[0].lower() + sent[1:]
            new_sentences.append(sent)

        result.append(' '.join(new_sentences))

    return join_paragraphs(result)


def add_parentheticals(text: str, intensity: float) -> str:
    """Add parenthetical asides to increase surprise."""
    paras = get_paragraphs(text)
    result = []

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        # Find spots to insert parentheticals (after commas in long sentences)
        if random.random() < intensity * 0.15:
            words = para.split()
            if len(words) > 30:
                # Find a comma
                for i, word in enumerate(words):
                    if word.endswith(',') and 10 < i < len(words) - 10:
                        if random.random() < 0.3:
                            paren = random.choice(PARENTHETICALS)
                            words[i] = words[i][:-1] + paren
                            break
                para = ' '.join(words)

        result.append(para)

    return join_paragraphs(result)


def vary_sentence_length_extreme(text: str, intensity: float) -> str:
    """Create more extreme sentence length variation."""
    paras = get_paragraphs(text)
    result = []

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', para)
        new_sentences = []

        for sent in sentences:
            words = sent.split()

            # Sometimes create very short sentences
            if len(words) > 20 and random.random() < intensity * 0.1:
                # Find a good break point
                for j in range(8, 15):
                    if j < len(words) and words[j].lower() in ('and', 'but', 'which', 'that', 'because'):
                        first = ' '.join(words[:j])
                        if not first.endswith('.'):
                            first += '.'
                        second = ' '.join(words[j:])
                        second = second[0].upper() + second[1:]
                        new_sentences.append(first)
                        # Add a very short follow-up
                        new_sentences.append("Consider this.")
                        sent = second
                        break

            new_sentences.append(sent)

        result.append(' '.join(new_sentences))

    return join_paragraphs(result)


def invert_sentence_structure(text: str, intensity: float) -> str:
    """Invert some sentence structures for variety."""
    inversions = [
        # Move adverbial phrases to front
        (r'(\w+) (\w+) (significantly|substantially|considerably)',
         r'\3, \1 \2'),
        # Passive to active-ish
        (r'it is (\w+) that',
         r'\1ly,'),
        (r'there is (\w+) evidence that',
         r'evidence \1ly suggests that'),
    ]

    for pattern, replacement in inversions:
        if random.random() < intensity * 0.2:
            text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)

    return text


def add_hedging_variety(text: str, intensity: float) -> str:
    """Add varied hedging language."""
    hedges = [
        (r'\bis\b', 'appears to be'),
        (r'\bare\b', 'seem to be'),
        (r'shows that', 'would suggest that'),
        (r'proves that', 'lends credence to the notion that'),
        (r'clearly', 'arguably'),
        (r'obviously', 'ostensibly'),
    ]

    for pattern, replacement in hedges:
        if random.random() < intensity * 0.1:
            text = re.sub(pattern, replacement, text, count=1)

    return text


def perplexity_humanize(text: str, intensity: float = 0.5) -> str:
    """Apply perplexity-increasing transforms."""
    text = replace_with_uncommon(text, intensity)
    text = add_unusual_starters(text, intensity)
    text = add_parentheticals(text, intensity)
    text = vary_sentence_length_extreme(text, intensity)
    text = invert_sentence_structure(text, intensity)
    text = add_hedging_variety(text, intensity)
    return text


def main():
    parser = argparse.ArgumentParser(description='Perplexity-based humanization')
    parser.add_argument('input', help='Input file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-i', '--intensity', type=float, default=0.5)
    parser.add_argument('-n', '--iterations', type=int, default=1)

    args = parser.parse_args()

    text = Path(args.input).read_text()

    for i in range(args.iterations):
        text = perplexity_humanize(text, args.intensity)
        print(f"Iteration {i+1} complete")

    if args.output:
        Path(args.output).write_text(text)
        print(f"Output written to {args.output}")
    else:
        print(text[:2000])


if __name__ == '__main__':
    main()
