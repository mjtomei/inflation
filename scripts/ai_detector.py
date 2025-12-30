#!/usr/bin/env python3
"""
AI Text Detector using RoBERTa-based OpenAI detector.

This uses the roberta-base-openai-detector model from HuggingFace,
which is trained to distinguish GPT-2 generated text from human text.

Note: This detector was trained on GPT-2 outputs and may be less accurate
on newer models like GPT-4 or Claude. For research purposes only.
"""

import argparse
import sys
from pathlib import Path
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch


def chunk_text(text: str, max_length: int = 500) -> list:
    """Split text into chunks that fit the model's context window."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_length:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def detect_ai_text(text: str, model_name: str = "roberta-base-openai-detector") -> dict:
    """
    Detect if text is AI-generated.

    Returns dict with:
        - ai_score: probability text is AI-generated (0-1)
        - human_score: probability text is human-written (0-1)
        - label: "AI" or "Human"
        - chunk_scores: individual scores for each chunk
    """
    print(f"Loading model {model_name}...")

    # Load the detector
    try:
        classifier = pipeline(
            "text-classification",
            model=f"openai-community/{model_name}",
            device=0 if torch.cuda.is_available() else -1
        )
    except Exception:
        # Fallback to CPU
        classifier = pipeline(
            "text-classification",
            model=f"openai-community/{model_name}",
            device=-1
        )

    # Process in chunks
    chunks = chunk_text(text, max_length=400)
    print(f"Processing {len(chunks)} chunks...")

    chunk_scores = []
    for i, chunk in enumerate(chunks):
        if len(chunk.strip()) < 50:  # Skip very short chunks
            continue
        result = classifier(chunk)[0]
        # The model outputs "LABEL_0" for Real/Human and "LABEL_1" for Fake/AI
        if result['label'] == 'LABEL_0':  # Human/Real
            score = 1 - result['score']  # Convert to AI probability
        else:  # AI/Fake
            score = result['score']
        chunk_scores.append(score)

        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1}/{len(chunks)} chunks...")

    if not chunk_scores:
        return {
            'ai_score': 0.5,
            'human_score': 0.5,
            'label': 'Unknown',
            'chunk_scores': []
        }

    # Average across chunks
    avg_ai_score = sum(chunk_scores) / len(chunk_scores)

    return {
        'ai_score': avg_ai_score,
        'human_score': 1 - avg_ai_score,
        'label': 'AI' if avg_ai_score > 0.5 else 'Human',
        'chunk_scores': chunk_scores,
        'num_chunks': len(chunk_scores)
    }


def main():
    parser = argparse.ArgumentParser(
        description='Detect AI-generated text using RoBERTa-based detector.'
    )
    parser.add_argument('input', help='Input file path')
    parser.add_argument('--model', default='roberta-base-openai-detector',
                        help='Model name (default: roberta-base-openai-detector)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed chunk scores')

    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text()

    # Detect
    result = detect_ai_text(text, args.model)

    # Output
    print(f"\n{'='*50}")
    print(f"AI Detection Results")
    print(f"{'='*50}")
    print(f"Overall AI Score: {result['ai_score']:.1%}")
    print(f"Overall Human Score: {result['human_score']:.1%}")
    print(f"Classification: {result['label']}")
    print(f"Chunks analyzed: {result['num_chunks']}")

    if args.verbose and result['chunk_scores']:
        print(f"\nChunk scores (AI probability):")
        for i, score in enumerate(result['chunk_scores']):
            bar = '█' * int(score * 20) + '░' * (20 - int(score * 20))
            print(f"  Chunk {i+1:3d}: {score:.1%} {bar}")

    # Return score for programmatic use
    return result['ai_score']


if __name__ == '__main__':
    main()
