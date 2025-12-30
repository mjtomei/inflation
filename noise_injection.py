#!/usr/bin/env python3
"""
Noise injection approach - adds actual randomness and imperfections
that break AI probability patterns.

AI text has very low entropy - each word is highly predictable.
This script adds entropy by injecting unpredictable elements.
"""

import re
import random
from pathlib import Path
from typing import List
import argparse

# Typo patterns (swap adjacent letters)
def introduce_typo(word: str) -> str:
    """Introduce a plausible typo by swapping adjacent letters."""
    if len(word) < 4:
        return word
    # Find swappable positions (not first/last)
    pos = random.randint(1, len(word) - 3)
    return word[:pos] + word[pos+1] + word[pos] + word[pos+2:]


# British vs American spelling variations
SPELLING_VARIANTS = [
    ('analyze', 'analyse'),
    ('behavior', 'behaviour'),
    ('color', 'colour'),
    ('center', 'centre'),
    ('organization', 'organisation'),
    ('recognize', 'recognise'),
    ('realize', 'realise'),
    ('utilize', 'utilise'),
    ('favor', 'favour'),
    ('labor', 'labour'),
    ('program', 'programme'),
    ('catalog', 'catalogue'),
    ('dialog', 'dialogue'),
    ('defense', 'defence'),
    ('offense', 'offence'),
    ('license', 'licence'),
    ('practice', 'practise'),  # verb form
]


# Informal/colloquial insertions
INFORMAL_PHRASES = [
    ("In fact,", "Actually,"),
    ("It is clear that", "It's pretty clear"),
    ("significantly", "quite a bit"),
    ("Furthermore,", "What's more,"),
    ("Additionally,", "Plus,"),
    ("It should be noted that", "Worth noting:"),
    ("This demonstrates that", "This shows"),
    ("As a result,", "So,"),
    ("In conclusion,", "Bottom line,"),
    ("Consequently,", "As a result,"),
]


# Random filler phrases humans use
FILLER_INSERTIONS = [
    "so to speak",
    "as it were",
    "in a sense",
    "if you will",
    "one might say",
    "broadly speaking",
    "in practical terms",
    "at least in part",
    "to some extent",
    "more or less",
]


# Sentence fragments and incomplete thoughts
HUMAN_FRAGMENTS = [
    "Interesting.",
    "Worth considering.",
    "A point often missed.",
    "Not always, but often.",
    "More on this below.",
    "Something to keep in mind.",
    "An important caveat here.",
    "Context matters.",
    "Timing is key.",
    "The data speaks.",
]


# Contractions that break formal patterns
CONTRACTIONS = [
    (r"\bdo not\b", "don't"),
    (r"\bdoes not\b", "doesn't"),
    (r"\bwill not\b", "won't"),
    (r"\bcannot\b", "can't"),
    (r"\bshould not\b", "shouldn't"),
    (r"\bwould not\b", "wouldn't"),
    (r"\bcould not\b", "couldn't"),
    (r"\bis not\b", "isn't"),
    (r"\bare not\b", "aren't"),
    (r"\bwas not\b", "wasn't"),
    (r"\bwere not\b", "weren't"),
    (r"\bhas not\b", "hasn't"),
    (r"\bhave not\b", "haven't"),
    (r"\bhad not\b", "hadn't"),
    (r"\bit is\b", "it's"),
    (r"\bthat is\b", "that's"),
    (r"\bwhat is\b", "what's"),
    (r"\bthere is\b", "there's"),
    (r"\bhere is\b", "here's"),
]


def get_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def join_paragraphs(paras: List[str]) -> str:
    return '\n\n'.join(paras)


def inject_typos(text: str, intensity: float) -> str:
    """Introduce occasional typos."""
    words = text.split()
    new_words = []

    # Only target certain common words that typos are believable for
    typo_targets = ['the', 'and', 'that', 'this', 'with', 'from', 'their',
                   'which', 'would', 'there', 'about', 'could', 'should',
                   'these', 'other', 'were', 'been', 'more', 'when']

    typo_count = 0
    max_typos = int(len(words) * intensity * 0.003)  # Very few typos

    for word in words:
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if (clean_word in typo_targets and
            random.random() < intensity * 0.02 and
            typo_count < max_typos):
            # Introduce typo
            typo = introduce_typo(clean_word)
            # Preserve punctuation and case
            if word[0].isupper():
                typo = typo.capitalize()
            # Preserve trailing punctuation
            trailing = ''
            if word and not word[-1].isalnum():
                trailing = word[-1]
                word = word[:-1]
            new_words.append(typo + trailing)
            typo_count += 1
        else:
            new_words.append(word)

    return ' '.join(new_words)


def vary_spelling(text: str, intensity: float) -> str:
    """Mix British/American spellings."""
    for us, uk in SPELLING_VARIANTS:
        if random.random() < intensity * 0.4:
            # Randomly pick which variant to use
            if random.random() < 0.5:
                text = re.sub(r'\b' + us + r'\b', uk, text, flags=re.IGNORECASE)
            else:
                text = re.sub(r'\b' + uk + r'\b', us, text, flags=re.IGNORECASE)
    return text


def inject_informal_phrases(text: str, intensity: float) -> str:
    """Replace formal phrases with informal alternatives."""
    for formal, informal in INFORMAL_PHRASES:
        if random.random() < intensity * 0.3:
            text = text.replace(formal, informal, 1)
    return text


def add_filler_phrases(text: str, intensity: float) -> str:
    """Add filler phrases that humans naturally use."""
    paras = get_paragraphs(text)
    result = []

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        # Find spots after commas to insert fillers
        if random.random() < intensity * 0.15:
            sentences = para.split('. ')
            new_sentences = []
            for sent in sentences:
                if ',' in sent and random.random() < 0.2:
                    # Insert filler after a comma
                    comma_pos = sent.find(',')
                    if comma_pos > 10:
                        filler = random.choice(FILLER_INSERTIONS)
                        sent = sent[:comma_pos+1] + ' ' + filler + ',' + sent[comma_pos+1:]
                new_sentences.append(sent)
            para = '. '.join(new_sentences)

        result.append(para)

    return join_paragraphs(result)


def inject_fragments(text: str, intensity: float) -> str:
    """Add human-like sentence fragments."""
    paras = get_paragraphs(text)
    result = []

    fragment_count = 0
    max_fragments = 5  # Limit total fragments

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        if random.random() < intensity * 0.08 and fragment_count < max_fragments:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            if len(sentences) > 2:
                # Insert a fragment after a random sentence
                insert_pos = random.randint(1, len(sentences) - 1)
                fragment = random.choice(HUMAN_FRAGMENTS)
                sentences.insert(insert_pos, fragment)
                fragment_count += 1
            para = ' '.join(sentences)

        result.append(para)

    return join_paragraphs(result)


def aggressive_contractions(text: str, intensity: float) -> str:
    """Convert formal phrases to contractions."""
    for pattern, contraction in CONTRACTIONS:
        if random.random() < intensity * 0.6:
            text = re.sub(pattern, contraction, text, flags=re.IGNORECASE)
    return text


def vary_punctuation_style(text: str, intensity: float) -> str:
    """Vary punctuation patterns."""
    # Oxford comma variation
    if random.random() < intensity * 0.3:
        # Sometimes remove Oxford comma
        text = re.sub(r',\s+and\s+(\w+)([.!?])', r' and \1\2', text, count=2)

    # Semicolon to period conversion
    if random.random() < intensity * 0.2:
        text = re.sub(r';\s+', '. ', text, count=2)

    # Add ellipsis occasionally
    if random.random() < intensity * 0.1:
        # Find a pause point and add ellipsis
        text = re.sub(r'(\w+),\s+(and|but)\s+', r'\1... \2 ', text, count=1)

    return text


def break_sentence_uniformity(text: str, intensity: float) -> str:
    """Break up uniform sentence patterns."""
    paras = get_paragraphs(text)
    result = []

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', para)

        # Look for sentences of similar length and break one
        if len(sentences) >= 3 and random.random() < intensity * 0.2:
            lens = [len(s.split()) for s in sentences]
            # Find similar lengths
            for i in range(len(lens) - 1):
                if abs(lens[i] - lens[i+1]) < 3 and lens[i] > 15:
                    # Break the second sentence
                    words = sentences[i+1].split()
                    mid = len(words) // 2
                    # Find a good break point
                    for j in range(mid - 3, mid + 3):
                        if j < len(words) and words[j].lower() in ['and', 'but', 'which', 'that', 'because', 'since']:
                            first = ' '.join(words[:j]) + '.'
                            second = words[j].capitalize() + ' ' + ' '.join(words[j+1:])
                            sentences[i+1] = first + ' ' + second
                            break
                    break

        result.append(' '.join(sentences))

    return join_paragraphs(result)


def add_mid_sentence_breaks(text: str, intensity: float) -> str:
    """Add parenthetical breaks mid-sentence."""
    breaks = [
        " - and this is key - ",
        " - perhaps surprisingly - ",
        " - in my view - ",
        " - and here's why - ",
        " - to be fair - ",
        " - importantly - ",
    ]

    paras = get_paragraphs(text)
    result = []
    break_count = 0

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        if random.random() < intensity * 0.15 and break_count < 3:
            # Find a good spot for a break (after a noun or verb)
            words = para.split()
            if len(words) > 25:
                for i in range(10, min(20, len(words))):
                    if words[i].endswith(','):
                        # Insert break after comma
                        break_text = random.choice(breaks)
                        words[i] = words[i][:-1] + break_text
                        break_count += 1
                        break
                para = ' '.join(words)

        result.append(para)

    return join_paragraphs(result)


def noise_humanize(text: str, intensity: float = 0.5) -> str:
    """Apply noise-based humanization."""
    # Apply transforms
    text = vary_spelling(text, intensity)
    text = inject_informal_phrases(text, intensity)
    text = aggressive_contractions(text, intensity)
    text = add_filler_phrases(text, intensity)
    text = inject_fragments(text, intensity)
    text = vary_punctuation_style(text, intensity)
    text = break_sentence_uniformity(text, intensity)
    text = add_mid_sentence_breaks(text, intensity)

    # Typos last (and sparingly)
    if intensity > 0.6:
        text = inject_typos(text, intensity * 0.3)

    return text


def main():
    parser = argparse.ArgumentParser(description='Noise-based humanization')
    parser.add_argument('input', help='Input file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-i', '--intensity', type=float, default=0.5)
    parser.add_argument('-n', '--iterations', type=int, default=1)

    args = parser.parse_args()

    text = Path(args.input).read_text()

    for i in range(args.iterations):
        text = noise_humanize(text, args.intensity)
        print(f"Iteration {i+1} complete")

    if args.output:
        Path(args.output).write_text(text)
        print(f"Output written to {args.output}")
    else:
        print(text[:2000])


if __name__ == '__main__':
    main()
