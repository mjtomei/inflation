#!/usr/bin/env python3
"""
Humanize text with AI detection feedback loop.

Iteratively transforms text to reduce AI detection score,
using the RoBERTa-based OpenAI detector as feedback.

Based on research from:
- Contrasting Linguistic Patterns in Human and LLM-Generated News Text
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11422446/
- Differentiating Between Human-Written and AI-Generated Texts
  https://www.mdpi.com/2078-2489/16/11/979
"""

import argparse
import random
import re
import sys
from pathlib import Path
from typing import Tuple, List, Dict
import importlib.util

# Import humanize_text module
spec = importlib.util.spec_from_file_location("humanize_text", "humanize_text.py")
humanize_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(humanize_module)

# Import detector
spec2 = importlib.util.spec_from_file_location("ai_detector", "ai_detector.py")
detector_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(detector_module)


def detect_ai_score(text: str) -> float:
    """Get AI detection score for text (0-1, higher = more AI-like)."""
    result = detector_module.detect_ai_text(text)
    return result['ai_score']


def humanize_with_feedback(
    text: str,
    target_score: float = 0.5,
    max_iterations: int = 10,
    noise_start: float = 0.3,
    noise_max: float = 0.8,
    verbose: bool = True
) -> Tuple[str, List[Dict]]:
    """
    Iteratively humanize text until AI detection score drops below target.

    Args:
        text: Input text
        target_score: Stop when AI score drops below this (0-1)
        max_iterations: Maximum iterations
        noise_start: Initial noise level
        noise_max: Maximum noise level
        verbose: Print progress

    Returns:
        Tuple of (humanized text, iteration history)
    """
    history = []
    current_text = text
    current_noise = noise_start

    for i in range(max_iterations):
        if verbose:
            print(f"\n{'='*50}")
            print(f"Iteration {i + 1}")
            print(f"{'='*50}")

        # Get current AI score
        ai_score = detect_ai_score(current_text)

        # Also get linguistic metrics
        metrics = humanize_module.calculate_metrics(current_text)

        history.append({
            'iteration': i,
            'ai_score': ai_score,
            'noise': current_noise,
            'metrics': metrics,
        })

        if verbose:
            print(f"AI Detection Score: {ai_score:.1%}")
            print(f"Linguistic AI Score: {metrics.ai_score():.3f}")
            print(f"Current noise level: {current_noise:.2f}")

        # Check if we've reached target
        if ai_score < target_score:
            if verbose:
                print(f"\n✓ Target score {target_score:.1%} reached!")
            break

        # Apply humanization
        if verbose:
            print(f"Applying humanization transforms...")

        current_text = humanize_module.humanize_iteration(current_text, current_noise)

        # Increase noise if not making progress
        if i > 0 and history[-1]['ai_score'] >= history[-2]['ai_score'] - 0.02:
            current_noise = min(current_noise + 0.1, noise_max)
            if verbose:
                print(f"Increasing noise to {current_noise:.2f}")

    return current_text, history


def main():
    parser = argparse.ArgumentParser(
        description='Humanize text with AI detection feedback loop.',
        epilog='''
Uses RoBERTa-based OpenAI detector for feedback.
Note: Detector was trained on GPT-2; may be less accurate on newer models.
        '''
    )
    parser.add_argument('input', help='Input file path')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-t', '--target', type=float, default=0.5,
                        help='Target AI score to reach (default: 0.5)')
    parser.add_argument('-i', '--iterations', type=int, default=10,
                        help='Max iterations (default: 10)')
    parser.add_argument('-n', '--noise', type=float, default=0.3,
                        help='Starting noise level (default: 0.3)')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Suppress progress output')
    parser.add_argument('--detect-only', action='store_true',
                        help='Only run detection, no transformation')

    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text()

    if args.detect_only:
        score = detect_ai_score(text)
        print(f"\nAI Detection Score: {score:.1%}")
        print(f"Classification: {'AI' if score > 0.5 else 'Human'}")
        return

    # Run humanization with feedback
    result, history = humanize_with_feedback(
        text,
        target_score=args.target,
        max_iterations=args.iterations,
        noise_start=args.noise,
        verbose=not args.quiet
    )

    # Output
    if args.output:
        Path(args.output).write_text(result)
        if not args.quiet:
            print(f"\nOutput written to: {args.output}")
    else:
        print("\n" + "="*60)
        print("Humanized text (first 500 chars):")
        print("="*60)
        print(result[:500] + "...")

    # Summary
    if not args.quiet and history:
        print(f"\n{'='*50}")
        print("Summary")
        print(f"{'='*50}")
        initial = history[0]['ai_score']
        final = history[-1]['ai_score']
        print(f"AI Score: {initial:.1%} -> {final:.1%}")
        print(f"Reduction: {(initial - final):.1%} ({(1-final/initial)*100:.1f}% relative)")
        print(f"Iterations: {len(history)}")


if __name__ == '__main__':
    main()
