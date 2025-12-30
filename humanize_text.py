#!/usr/bin/env python3
"""
Humanize Text: Iteratively transform text to reduce AI-like linguistic patterns.

Based on research findings from:
- Contrasting Linguistic Patterns in Human and LLM-Generated News Text
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11422446/
- Differentiating Between Human-Written and AI-Generated Texts
  https://www.mdpi.com/2078-2489/16/11/979
- Do LLMs write like humans? Variation in grammatical and rhetorical styles
  https://www.aimodels.fyi/papers/arxiv/do-llms-write-like-humans-variation-grammatical

Key findings these transformations address:
1. AI text has more uniform sentence lengths; humans have scattered distributions
2. AI uses more coordinating conjunctions, nouns, pronouns
3. AI repeats syntactic templates more than humans
4. AI uses narrower range of stance/engagement features
5. Human text has more emotional nuance and stylistic diversity
6. AI prefers certain constructions: nominalizations, 'that'-clauses, phrasal coordination
"""

import re
import random
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Dict
import statistics


@dataclass
class TextMetrics:
    """Metrics that distinguish AI from human text."""
    sentence_length_variance: float  # Higher = more human-like
    avg_sentence_length: float
    conjunction_density: float  # Lower = more human-like
    nominalization_density: float  # Lower = more human-like
    em_dash_density: float  # Lower = more human-like
    ai_word_density: float  # Lower = more human-like
    sentence_starter_variety: float  # Higher = more human-like
    contraction_density: float  # Higher = more human-like (in informal text)

    def ai_score(self) -> float:
        """Composite score - lower is more human-like."""
        # Weights based on research findings
        score = 0.0

        # Sentence length variance: humans have more variance
        # Target variance around 150-300 for natural text
        if self.sentence_length_variance < 100:
            score += 2.0 * (100 - self.sentence_length_variance) / 100

        # Conjunction density: AI uses more
        score += self.conjunction_density * 3.0

        # Nominalization density: AI uses more
        score += self.nominalization_density * 2.0

        # Em dash density: AI overuses
        score += self.em_dash_density * 5.0

        # AI-favorite words
        score += self.ai_word_density * 4.0

        # Sentence starter variety: lower variety = more AI-like
        if self.sentence_starter_variety < 0.5:
            score += (0.5 - self.sentence_starter_variety) * 2.0

        return score


# AI-favorite words and phrases (from research + empirical observation)
AI_WORDS = {
    'delve', 'delves', 'delving',
    'tapestry',
    'multifaceted',
    'nuanced', 'nuance',
    'landscape',
    'leverage', 'leveraging', 'leveraged',
    'robust',
    'navigate', 'navigating',
    'crucial', 'crucially',
    'pivotal',
    'fundamental', 'fundamentally',
    'comprehensive',
    'intricate',
    'facilitate', 'facilitates', 'facilitating',
    'utilize', 'utilizes', 'utilizing',
    'underscore', 'underscores', 'underscoring',
    'highlight', 'highlights', 'highlighting',
    'realm',
    'paradigm',
    'synergy',
    'holistic',
    'streamline',
    'optimize',
    'innovative',
    'cutting-edge',
    'state-of-the-art',
    'groundbreaking',
    'transformative',
}

AI_PHRASES = [
    r"it'?s (important|worth|crucial) to note",
    r"it bears (mentioning|noting)",
    r"this (is|represents) a (significant|fundamental|crucial)",
    r"at its core",
    r"in essence",
    r"a testament to",
    r"sheds light on",
    r"paves the way",
    r"the fact that",
    r"it is (clear|evident|apparent) that",
    r"this (highlights|underscores|demonstrates)",
    r"(furthermore|moreover|additionally),",
    r"interestingly,",
    r"notably,",
    r"(significantly|importantly),",
]

# Nominalizations that could be verbs
NOMINALIZATIONS = {
    'utilization': 'using',
    'implementation': 'implementing',
    'optimization': 'optimizing',
    'transformation': 'transforming',
    'democratization': 'democratizing',
    'verification': 'verifying',
    'examination': 'examining',
    'consideration': 'considering',
    'determination': 'determining',
    'establishment': 'establishing',
    'development': 'developing',
    'improvement': 'improving',
    'measurement': 'measuring',
    'assessment': 'assessing',
    'achievement': 'achieving',
    'advancement': 'advancing',
    'enhancement': 'enhancing',
    'expansion': 'expanding',
    'reduction': 'reducing',
    'production': 'producing',
    'distribution': 'distributing',
    'concentration': 'concentrating',
    'accumulation': 'accumulating',
}

# Replacements for AI-favorite words
AI_WORD_REPLACEMENTS = {
    'utilize': 'use',
    'utilizes': 'uses',
    'utilizing': 'using',
    'facilitate': 'help',
    'facilitates': 'helps',
    'robust': 'strong',
    'significant': 'large',
    'significantly': 'much',
    'substantial': 'large',
    'substantially': 'much',
    'demonstrated': 'showed',
    'demonstrates': 'shows',
    'demonstrate': 'show',
    'indicating': 'showing',
    'subsequently': 'then',
    'additionally': 'also',
    # Note: 'however', 'therefore', 'furthermore' kept as they're normal academic words
    # 'comprehensive', 'crucial', 'fundamental' kept as they have specific meanings
}


def get_sentences(text: str) -> List[str]:
    """Split text into sentences, handling common edge cases."""
    # Simple sentence splitter - not perfect but good enough
    # Don't split on abbreviations like "et al." or "Dr."
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in sentences if s.strip()]


def get_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs, preserving structure."""
    # Split on double newlines or markdown headers
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def join_paragraphs(paragraphs: List[str]) -> str:
    """Rejoin paragraphs with proper spacing."""
    return '\n\n'.join(paragraphs)


def calculate_metrics(text: str) -> TextMetrics:
    """Calculate linguistic metrics for the text."""
    sentences = get_sentences(text)
    words = text.lower().split()
    word_count = len(words)

    if not sentences or word_count == 0:
        return TextMetrics(0, 0, 0, 0, 0, 0, 0, 0)

    # Sentence length variance
    sent_lengths = [len(s.split()) for s in sentences]
    sent_variance = statistics.variance(sent_lengths) if len(sent_lengths) > 1 else 0
    avg_sent_length = statistics.mean(sent_lengths)

    # Conjunction density (and, but, or, yet, so, for, nor at sentence level)
    conjunctions = len(re.findall(r'\b(and|but|or|yet|so|for|nor)\b', text.lower()))
    conj_density = conjunctions / word_count

    # Nominalization density
    nom_count = sum(1 for word in words if word in NOMINALIZATIONS)
    nom_density = nom_count / word_count

    # Em dash density
    em_dashes = text.count('—') + text.count('--')
    em_density = em_dashes / (len(sentences) or 1)

    # AI word density
    ai_count = sum(1 for word in words if word in AI_WORDS)
    for phrase in AI_PHRASES:
        ai_count += len(re.findall(phrase, text.lower()))
    ai_density = ai_count / word_count

    # Sentence starter variety
    starters = []
    for sent in sentences:
        words_in_sent = sent.split()
        if words_in_sent:
            # Get first 2-3 words as starter pattern
            starter = ' '.join(words_in_sent[:min(2, len(words_in_sent))]).lower()
            starters.append(starter)
    unique_starters = len(set(starters))
    starter_variety = unique_starters / len(starters) if starters else 0

    # Contraction density
    contractions = len(re.findall(r"\b\w+'\w+\b", text))
    contraction_density = contractions / word_count

    return TextMetrics(
        sentence_length_variance=sent_variance,
        avg_sentence_length=avg_sent_length,
        conjunction_density=conj_density,
        nominalization_density=nom_density,
        em_dash_density=em_density,
        ai_word_density=ai_density,
        sentence_starter_variety=starter_variety,
        contraction_density=contraction_density,
    )


def vary_sentence_length(text: str, noise: float) -> str:
    """
    Vary sentence lengths to create more human-like distribution.

    Humans have more scattered sentence length distributions.
    This function occasionally splits long sentences.
    Applied paragraph by paragraph to preserve structure.
    """
    paragraphs = get_paragraphs(text)
    result_paragraphs = []

    for para in paragraphs:
        # Skip headers, tables, and special formatting
        if para.startswith('#') or para.startswith('|') or para.startswith('*') or para.startswith('-'):
            result_paragraphs.append(para)
            continue

        sentences = get_sentences(para)
        if len(sentences) < 1:
            result_paragraphs.append(para)
            continue

        result = []
        for sent in sentences:
            words = sent.split()

            # Only split very long sentences (>35 words) at safe points
            if len(words) > 35 and random.random() < noise * 0.2:
                # Find a safe split point: semicolon, or conjunction after comma
                # Look for "; " first
                if '; ' in sent:
                    parts = sent.split('; ', 1)
                    if len(parts[0].split()) > 8 and len(parts[1].split()) > 8:
                        result.append(parts[0] + '.')
                        result.append(parts[1][0].upper() + parts[1][1:])
                        continue

            result.append(sent)

        result_paragraphs.append(' '.join(result))

    return join_paragraphs(result_paragraphs)


def reduce_conjunctions(text: str, noise: float) -> str:
    """
    Reduce overuse of coordinating conjunctions.

    Applied very conservatively - only split when we're confident it creates valid sentences.
    """
    # Only replace "; and" with period (already a strong break)
    def replace_semi_and(match):
        rest = match.group(1)
        if random.random() < noise * 0.3:
            return '. ' + rest[0].upper() + rest[1:]
        return match.group(0)

    text = re.sub(r'; and ([a-z])', replace_semi_and, text)

    return text


def replace_nominalizations(text: str, noise: float) -> str:
    """
    Replace some nominalizations with verb forms.

    AI text uses more nominalizations. Verb forms are more direct.
    """
    for nom, verb in NOMINALIZATIONS.items():
        if random.random() < noise * 0.3:
            # Only replace "the X of" patterns
            pattern = rf'\bthe {nom} of\b'
            replacement = f'{verb}'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def replace_ai_words(text: str, noise: float) -> str:
    """Replace AI-favorite words with simpler alternatives."""
    for ai_word, replacement in AI_WORD_REPLACEMENTS.items():
        if random.random() < noise * 0.5:
            # Case-insensitive replacement preserving case
            pattern = re.compile(re.escape(ai_word), re.IGNORECASE)

            def replace_preserving_case(match):
                orig = match.group(0)
                if orig.isupper():
                    return replacement.upper()
                elif orig[0].isupper():
                    return replacement.capitalize()
                return replacement

            text = pattern.sub(replace_preserving_case, text)

    return text


def replace_em_dashes(text: str, noise: float) -> str:
    """
    Replace some em dashes with other punctuation.

    AI overuses em dashes. Replace with commas or colons only.
    Avoid creating sentence fragments by not splitting into periods.
    """
    def replace_dash(match):
        before = match.group(1)
        after = match.group(2)

        if random.random() > noise * 0.5:  # More conservative
            return match.group(0)

        # Only use comma or keep as-is (safest transformations)
        if random.random() < 0.7:
            return f'{before}, {after}'
        else:
            return match.group(0)

    # Match em dash with surrounding content
    text = re.sub(r'(\w+)—(\w+)', replace_dash, text)

    return text


def add_imperfections(text: str, noise: float) -> str:
    """
    Add small imperfections that make text more human.

    Humans make small variations that AI tends to avoid.
    This is applied conservatively to avoid breaking the text.
    """
    # Process paragraph by paragraph to preserve structure
    paragraphs = get_paragraphs(text)
    result_paragraphs = []

    for para in paragraphs:
        # Skip headers, tables, and special formatting
        if para.startswith('#') or para.startswith('|') or para.startswith('*') or para.startswith('-'):
            result_paragraphs.append(para)
            continue

        sentences = get_sentences(para)
        result = []

        for i, sent in enumerate(sentences):
            # Skip adding "But" - it's too risky and often sounds wrong
            # Human imperfections are better added through other means
            result.append(sent)

        result_paragraphs.append(' '.join(result))

    return join_paragraphs(result_paragraphs)


def vary_sentence_starters(text: str, noise: float) -> str:
    """
    Vary sentence starters to avoid repetitive patterns.

    AI tends to repeat syntactic templates. Humans vary more.
    Applied conservatively - only drops articles when grammatically safe.
    """
    paragraphs = get_paragraphs(text)
    result_paragraphs = []

    for para in paragraphs:
        # Skip headers, tables, and special formatting
        if para.startswith('#') or para.startswith('|') or para.startswith('*') or para.startswith('-'):
            result_paragraphs.append(para)
            continue

        sentences = get_sentences(para)
        recent_patterns = []
        result = []

        for sent in sentences:
            words = sent.split()
            if len(words) < 4:
                result.append(sent)
                continue

            starter = words[0].lower()

            # Only try to vary if we've used this exact starter 2+ times recently
            if recent_patterns.count(starter) >= 2 and random.random() < noise * 0.3:
                # Very conservative: only drop "The" before proper nouns or well-known terms
                if starter == 'the' and len(words) > 4:
                    # Check if second word is capitalized (proper noun) or a known term
                    if words[1][0].isupper() or words[1].lower() in ('bls', 'cpi', 'fed', 'gdp'):
                        sent = ' '.join(words[1:])

            result.append(sent)
            recent_patterns.append(starter)
            if len(recent_patterns) > 6:
                recent_patterns.pop(0)

        result_paragraphs.append(' '.join(result))

    return join_paragraphs(result_paragraphs)


def humanize_iteration(text: str, noise: float) -> str:
    """Apply one iteration of humanization transformations."""

    # Apply transformations in order
    text = replace_ai_words(text, noise)
    text = replace_em_dashes(text, noise)
    text = reduce_conjunctions(text, noise)
    text = replace_nominalizations(text, noise)
    text = vary_sentence_length(text, noise)
    text = vary_sentence_starters(text, noise)
    text = add_imperfections(text, noise)

    return text


def humanize(
    text: str,
    max_iterations: int = 10,
    noise: float = 0.5,
    convergence_threshold: float = 0.1,
    verbose: bool = True
) -> Tuple[str, List[Dict]]:
    """
    Iteratively humanize text until convergence.

    Args:
        text: Input text to humanize
        max_iterations: Maximum number of iterations
        noise: Amount of randomness (0-1). Higher = more changes
        convergence_threshold: Stop when score change is below this
        verbose: Print progress

    Returns:
        Tuple of (humanized text, iteration history)
    """
    history = []
    current_text = text
    prev_score = None

    for i in range(max_iterations):
        metrics = calculate_metrics(current_text)
        score = metrics.ai_score()

        history.append({
            'iteration': i,
            'score': score,
            'metrics': metrics,
        })

        if verbose:
            print(f"Iteration {i}: AI score = {score:.3f}")
            print(f"  Sentence variance: {metrics.sentence_length_variance:.1f}")
            print(f"  Conjunction density: {metrics.conjunction_density:.4f}")
            print(f"  Em-dash density: {metrics.em_dash_density:.3f}")
            print(f"  AI word density: {metrics.ai_word_density:.4f}")
            print(f"  Starter variety: {metrics.sentence_starter_variety:.3f}")

        # Check convergence
        if prev_score is not None:
            change = abs(prev_score - score)
            if change < convergence_threshold:
                if verbose:
                    print(f"\nConverged after {i+1} iterations (change={change:.4f})")
                break

        prev_score = score

        # Apply humanization
        current_text = humanize_iteration(current_text, noise)

    return current_text, history


def main():
    parser = argparse.ArgumentParser(
        description='Humanize text by reducing AI-like linguistic patterns.',
        epilog='''
Based on research from:
- PMC: Contrasting Linguistic Patterns in Human and LLM-Generated News Text
- MDPI: Differentiating Between Human-Written and AI-Generated Texts
- arXiv: Do LLMs write like humans? Variation in grammatical and rhetorical styles
        '''
    )
    parser.add_argument('input', help='Input file path')
    parser.add_argument('-o', '--output', help='Output file path (default: stdout)')
    parser.add_argument('-n', '--noise', type=float, default=0.5,
                        help='Noise level 0-1 (default: 0.5)')
    parser.add_argument('-i', '--iterations', type=int, default=10,
                        help='Max iterations (default: 10)')
    parser.add_argument('-t', '--threshold', type=float, default=0.1,
                        help='Convergence threshold (default: 0.1)')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Suppress progress output')
    parser.add_argument('--metrics-only', action='store_true',
                        help='Only calculate and display metrics, no transformation')

    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text()

    if args.metrics_only:
        metrics = calculate_metrics(text)
        print(f"AI Score: {metrics.ai_score():.3f}")
        print(f"Sentence length variance: {metrics.sentence_length_variance:.1f}")
        print(f"Average sentence length: {metrics.avg_sentence_length:.1f} words")
        print(f"Conjunction density: {metrics.conjunction_density:.4f}")
        print(f"Nominalization density: {metrics.nominalization_density:.4f}")
        print(f"Em-dash density: {metrics.em_dash_density:.3f}")
        print(f"AI word density: {metrics.ai_word_density:.4f}")
        print(f"Sentence starter variety: {metrics.sentence_starter_variety:.3f}")
        print(f"Contraction density: {metrics.contraction_density:.4f}")
        return

    # Humanize
    result, history = humanize(
        text,
        max_iterations=args.iterations,
        noise=args.noise,
        convergence_threshold=args.threshold,
        verbose=not args.quiet
    )

    # Output
    if args.output:
        Path(args.output).write_text(result)
        if not args.quiet:
            print(f"\nOutput written to: {args.output}")
    else:
        print("\n" + "="*60 + "\n")
        print(result)

    # Summary
    if not args.quiet and history:
        initial = history[0]['score']
        final = history[-1]['score']
        print(f"\nSummary: AI score {initial:.3f} -> {final:.3f} ({(1-final/initial)*100:.1f}% reduction)")


if __name__ == '__main__':
    main()
