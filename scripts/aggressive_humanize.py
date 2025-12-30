#!/usr/bin/env python3
"""
Aggressive text humanization with modern AI detection.

This version applies more disruptive transforms that may break
academic tone but are more likely to fool AI detectors.

Uses Binoculars (ICML 2024) for detection when available,
falls back to RoBERTa detector.
"""

import argparse
import random
import re
import sys
from pathlib import Path
from typing import Tuple, List, Dict
import torch

# Try to import Binoculars
try:
    from binoculars import Binoculars
    BINOCULARS_AVAILABLE = True
except ImportError:
    BINOCULARS_AVAILABLE = False
    print("Binoculars not available, will use RoBERTa detector")

from transformers import pipeline


class AIDetector:
    """Wrapper for AI detection using best available model."""

    def __init__(self, use_binoculars: bool = True):
        self.use_binoculars = use_binoculars and BINOCULARS_AVAILABLE

        if self.use_binoculars:
            print("Initializing Binoculars detector (this may take a minute)...")
            try:
                # Try with smaller models first
                self.detector = Binoculars(
                    observer_name_or_path="tiiuae/falcon-7b",
                    performer_name_or_path="tiiuae/falcon-7b-instruct",
                    device="cuda" if torch.cuda.is_available() else "cpu"
                )
                print("Binoculars initialized successfully")
            except Exception as e:
                print(f"Binoculars failed: {e}")
                print("Falling back to RoBERTa detector")
                self.use_binoculars = False

        if not self.use_binoculars:
            print("Initializing RoBERTa detector...")
            self.detector = pipeline(
                "text-classification",
                model="openai-community/roberta-base-openai-detector",
                device=0 if torch.cuda.is_available() else -1
            )

    def detect(self, text: str) -> float:
        """Return AI probability score (0-1)."""
        if self.use_binoculars:
            # Binoculars returns lower scores for AI text
            score = self.detector.compute_score(text)
            # Convert to probability (lower binoculars score = more likely AI)
            # Typical threshold is around 0.9
            ai_prob = max(0, min(1, 1 - (score / 1.5)))
            return ai_prob
        else:
            # RoBERTa detector - process in chunks
            chunks = self._chunk_text(text, 400)
            scores = []
            for chunk in chunks:
                if len(chunk.strip()) < 50:
                    continue
                result = self.detector(chunk)[0]
                if result['label'] == 'LABEL_0':
                    scores.append(1 - result['score'])
                else:
                    scores.append(result['score'])
            return sum(scores) / len(scores) if scores else 0.5

    def _chunk_text(self, text: str, max_len: int) -> List[str]:
        words = text.split()
        chunks = []
        current = []
        length = 0
        for word in words:
            if length + len(word) > max_len:
                if current:
                    chunks.append(' '.join(current))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += len(word) + 1
        if current:
            chunks.append(' '.join(current))
        return chunks


# More aggressive word replacements
AGGRESSIVE_REPLACEMENTS = {
    # Formal -> Informal
    'utilize': 'use',
    'demonstrate': 'show',
    'indicates': 'shows',
    'significant': 'big',
    'substantial': 'large',
    'approximately': 'about',
    'however': 'but',
    'therefore': 'so',
    'additionally': 'also',
    'furthermore': 'plus',
    'consequently': 'so',
    'nevertheless': 'still',
    'regarding': 'about',
    'concerning': 'about',
    'pertaining': 'about',
    'subsequent': 'later',
    'prior': 'earlier',
    'sufficient': 'enough',
    'numerous': 'many',
    'various': 'different',
    'particular': 'specific',
    'primary': 'main',
    'additional': 'more',
    'obtain': 'get',
    'require': 'need',
    'possess': 'have',
    'commence': 'start',
    'terminate': 'end',
    'sufficient': 'enough',
    'frequently': 'often',
    'occasionally': 'sometimes',
    'immediately': 'right away',
    'previously': 'before',
    'currently': 'now',
    'primarily': 'mainly',
    'essentially': 'basically',
    'specifically': 'exactly',
    'particularly': 'especially',
}

# Phrases to inject for human feel
HUMAN_INTERJECTIONS = [
    "Look,",
    "Here's the thing:",
    "To be honest,",
    "In practice,",
    "The reality is",
    "What this means is",
    "Put simply,",
    "In other words,",
    "The bottom line:",
    "Worth noting:",
    "Interestingly enough,",
    "As it turns out,",
]

# Sentence starters that feel more human
HUMAN_STARTERS = [
    "And ",
    "But ",
    "So ",
    "Now ",
    "Yet ",
    "Still, ",
    "True, ",
    "Sure, ",
    "Granted, ",
    "That said, ",
]


def get_paragraphs(text: str) -> List[str]:
    """Split into paragraphs."""
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def join_paragraphs(paras: List[str]) -> str:
    """Join paragraphs."""
    return '\n\n'.join(paras)


def aggressive_word_replace(text: str, intensity: float) -> str:
    """Replace formal words with informal equivalents."""
    for formal, informal in AGGRESSIVE_REPLACEMENTS.items():
        if random.random() < intensity:
            # Case-preserving replacement
            pattern = re.compile(re.escape(formal), re.IGNORECASE)
            def replacer(m):
                orig = m.group(0)
                if orig.isupper():
                    return informal.upper()
                elif orig[0].isupper():
                    return informal.capitalize()
                return informal
            text = pattern.sub(replacer, text)
    return text


def inject_interjections(text: str, intensity: float) -> str:
    """Add human-sounding interjections at paragraph starts."""
    paras = get_paragraphs(text)
    result = []

    for i, para in enumerate(paras):
        # Skip headers and special formatting
        if para.startswith('#') or para.startswith('|') or para.startswith('*') or para.startswith('-'):
            result.append(para)
            continue

        # Occasionally add interjection at paragraph start
        if i > 2 and random.random() < intensity * 0.15:
            interjection = random.choice(HUMAN_INTERJECTIONS)
            # Lowercase the first word of the paragraph
            words = para.split()
            if words and words[0][0].isupper() and words[0] not in ('I', 'CPI', 'BLS', 'GDP', 'Fed', 'AI'):
                words[0] = words[0][0].lower() + words[0][1:]
            para = interjection + ' ' + ' '.join(words)

        result.append(para)

    return join_paragraphs(result)


def vary_sentence_structure(text: str, intensity: float) -> str:
    """More aggressive sentence structure variation."""
    paras = get_paragraphs(text)
    result = []

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', para)
        new_sentences = []

        for i, sent in enumerate(sentences):
            words = sent.split()
            if len(words) < 5:
                new_sentences.append(sent)
                continue

            # Occasionally start with conjunction
            if i > 0 and random.random() < intensity * 0.1:
                starter = random.choice(HUMAN_STARTERS)
                if words[0] not in ('The', 'This', 'These', 'Those', 'It', 'They', 'We'):
                    sent = starter + sent[0].lower() + sent[1:]

            # Occasionally split long sentences more aggressively
            if len(words) > 25 and random.random() < intensity * 0.3:
                # Find a good split point
                for j in range(12, len(words) - 8):
                    if words[j].lower() in ('and', 'but', 'which', 'that', 'because', 'since', 'while'):
                        first = ' '.join(words[:j])
                        second = ' '.join(words[j:])
                        if not first.endswith('.'):
                            first += '.'
                        second = second[0].upper() + second[1:]
                        new_sentences.append(first)
                        sent = second
                        break

            # Occasionally add parenthetical asides
            if len(words) > 15 and random.random() < intensity * 0.08:
                insert_pos = random.randint(5, len(words) - 5)
                asides = [
                    "(and this matters)",
                    "(surprisingly)",
                    "(at least in theory)",
                    "(for what it's worth)",
                    "(importantly)",
                    "(to be clear)",
                ]
                words.insert(insert_pos, random.choice(asides))
                sent = ' '.join(words)

            new_sentences.append(sent)

        result.append(' '.join(new_sentences))

    return join_paragraphs(result)


def add_contractions(text: str, intensity: float) -> str:
    """Add contractions to make text more conversational."""
    contractions = [
        (r"\bdo not\b", "don't"),
        (r"\bdoes not\b", "doesn't"),
        (r"\bcannot\b", "can't"),
        (r"\bwill not\b", "won't"),
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
        (r"\bwe are\b", "we're"),
        (r"\bthey are\b", "they're"),
        (r"\bwe have\b", "we've"),
        (r"\bthey have\b", "they've"),
        (r"\bI have\b", "I've"),
        (r"\bI am\b", "I'm"),
        (r"\bI would\b", "I'd"),
        (r"\bI will\b", "I'll"),
    ]

    for pattern, replacement in contractions:
        if random.random() < intensity * 0.5:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def add_hedges_and_uncertainty(text: str, intensity: float) -> str:
    """Add hedging language that humans use."""
    hedges = [
        (r"\bwill\b", "might"),
        (r"\bshows that\b", "suggests that"),
        (r"\bproves\b", "indicates"),
        (r"\bclearly\b", "arguably"),
        (r"\bdefinitely\b", "probably"),
        (r"\bcertainly\b", "likely"),
        (r"\bobviously\b", "apparently"),
    ]

    for pattern, replacement in hedges:
        if random.random() < intensity * 0.2:
            text = re.sub(pattern, replacement, text, count=1)

    return text


def replace_em_dashes_aggressive(text: str, intensity: float) -> str:
    """More aggressive em-dash replacement."""
    # Replace em dashes with various punctuation
    def replacer(match):
        before = match.group(1)
        after = match.group(2)

        if random.random() > intensity:
            return match.group(0)

        choice = random.random()
        if choice < 0.4:
            return f"{before}, {after}"
        elif choice < 0.6:
            return f"{before}. {after[0].upper()}{after[1:]}" if after else f"{before}."
        elif choice < 0.8:
            return f"{before} ({after})"
        else:
            return f"{before} - {after}"  # Regular dash

    text = re.sub(r'(\w+)—(\w+)', replacer, text)
    return text


def add_filler_words(text: str, intensity: float) -> str:
    """Add filler words that humans naturally use."""
    fillers = [
        (r'\. ([A-Z])', lambda m: f'. {random.choice(["Well, ", "So, ", "Now, ", "OK, ", "Right, ", "Look, ", ""])}{m.group(1)}'),
    ]

    for pattern, replacer in fillers:
        if random.random() < intensity * 0.1:
            text = re.sub(pattern, replacer, text, count=3)

    return text


def add_minor_imperfections(text: str, intensity: float) -> str:
    """Add small imperfections humans make."""
    paras = get_paragraphs(text)
    result = []

    for para in paras:
        if para.startswith('#') or para.startswith('|') or para.startswith('*'):
            result.append(para)
            continue

        # Occasionally repeat a word (humans do this)
        if random.random() < intensity * 0.05:
            words = para.split()
            if len(words) > 20:
                idx = random.randint(10, len(words) - 5)
                words.insert(idx, words[idx])
                para = ' '.join(words)

        # Occasionally use "..." for trailing thoughts
        if random.random() < intensity * 0.03:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            if len(sentences) > 2:
                idx = random.randint(0, len(sentences) - 2)
                if sentences[idx].endswith('.'):
                    sentences[idx] = sentences[idx][:-1] + '...'
                para = ' '.join(sentences)

        result.append(para)

    return join_paragraphs(result)


def break_parallel_structure(text: str, intensity: float) -> str:
    """Break up parallel sentence structures that AI tends to produce."""
    # Find patterns like "First, X. Second, Y. Third, Z."
    patterns = [
        (r'First,([^.]+)\. Second,([^.]+)\. Third,([^.]+)\.',
         lambda m: f"Let's start with{m.group(1)}. Then there's{m.group(2)}. And finally{m.group(3)}."),
        (r'(\d)\) ([^.]+)\. (\d)\) ([^.]+)\.',
         lambda m: f"{m.group(2)}. Also, {m.group(4)}."),
    ]

    for pattern, replacer in patterns:
        if random.random() < intensity * 0.3:
            text = re.sub(pattern, replacer, text, count=1)

    return text


def vary_punctuation(text: str, intensity: float) -> str:
    """Vary punctuation patterns."""
    # Sometimes use semicolons instead of periods
    if random.random() < intensity * 0.2:
        text = re.sub(r'\. ([a-z])', lambda m: f'; {m.group(1)}', text, count=2)

    # Sometimes use dashes instead of commas
    if random.random() < intensity * 0.15:
        text = re.sub(r', (\w+ \w+),', lambda m: f' - {m.group(1)} -', text, count=2)

    return text


def aggressive_humanize(text: str, intensity: float = 0.5) -> str:
    """Apply all aggressive humanization transforms."""
    text = aggressive_word_replace(text, intensity)
    text = replace_em_dashes_aggressive(text, intensity)
    text = add_contractions(text, intensity)
    text = vary_sentence_structure(text, intensity)
    text = inject_interjections(text, intensity)
    text = add_hedges_and_uncertainty(text, intensity)
    text = add_filler_words(text, intensity)
    text = add_minor_imperfections(text, intensity)
    text = break_parallel_structure(text, intensity)
    text = vary_punctuation(text, intensity)
    return text


def humanize_with_feedback(
    text: str,
    detector: AIDetector,
    target_score: float = 0.5,
    max_iterations: int = 10,
    intensity_start: float = 0.3,
    intensity_max: float = 0.9,
    verbose: bool = True
) -> Tuple[str, List[Dict]]:
    """Iteratively humanize with detection feedback."""
    history = []
    current_text = text
    intensity = intensity_start

    for i in range(max_iterations):
        if verbose:
            print(f"\n{'='*50}")
            print(f"Iteration {i + 1}")
            print(f"{'='*50}")

        # Detect
        if verbose:
            print("Running AI detection...")
        ai_score = detector.detect(current_text)

        history.append({
            'iteration': i,
            'ai_score': ai_score,
            'intensity': intensity,
        })

        if verbose:
            print(f"AI Score: {ai_score:.1%}")
            print(f"Intensity: {intensity:.2f}")

        if ai_score < target_score:
            if verbose:
                print(f"\n✓ Target {target_score:.1%} reached!")
            break

        # Apply transforms
        if verbose:
            print("Applying aggressive humanization...")
        current_text = aggressive_humanize(current_text, intensity)

        # Increase intensity if not making progress
        if i > 0 and history[-1]['ai_score'] >= history[-2]['ai_score'] - 0.03:
            intensity = min(intensity + 0.15, intensity_max)
            if verbose:
                print(f"Increasing intensity to {intensity:.2f}")

    return current_text, history


def main():
    parser = argparse.ArgumentParser(
        description='Aggressively humanize text with AI detection feedback.'
    )
    parser.add_argument('input', help='Input file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-t', '--target', type=float, default=0.5,
                        help='Target AI score (default: 0.5)')
    parser.add_argument('-i', '--iterations', type=int, default=10,
                        help='Max iterations (default: 10)')
    parser.add_argument('--intensity', type=float, default=0.3,
                        help='Starting intensity (default: 0.3)')
    parser.add_argument('--no-binoculars', action='store_true',
                        help='Use RoBERTa instead of Binoculars')
    parser.add_argument('-q', '--quiet', action='store_true')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text()

    # Initialize detector
    detector = AIDetector(use_binoculars=not args.no_binoculars)

    # Run
    result, history = humanize_with_feedback(
        text,
        detector,
        target_score=args.target,
        max_iterations=args.iterations,
        intensity_start=args.intensity,
        verbose=not args.quiet
    )

    # Output
    if args.output:
        Path(args.output).write_text(result)
        print(f"\nOutput written to: {args.output}")

    # Summary
    if history:
        print(f"\n{'='*50}")
        print("Summary")
        print(f"{'='*50}")
        initial = history[0]['ai_score']
        final = history[-1]['ai_score']
        print(f"AI Score: {initial:.1%} → {final:.1%}")
        if initial > 0:
            print(f"Reduction: {(initial - final):.1%} ({(1-final/initial)*100:.1f}% relative)")


if __name__ == '__main__':
    main()
