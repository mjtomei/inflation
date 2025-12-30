#!/usr/bin/env python3
"""
Iterative Document Review System

A system for continuously improving documents through AI and human review,
with autonomous decision-making on which changes improve document integrity.

Usage:
    python review_loop.py <document.md> [--purpose "..."] [--audience "..."]

The system will:
1. Load the document and any existing context
2. Generate or load reviews
3. Evaluate each recommendation for integrity impact
4. Apply beneficial changes
5. Queue edge cases for optional human input
6. Continue iterating until convergence or user stops

Files created:
    - <document>_context.json: Purpose, audience, constraints
    - <document>_reviews/: Directory for review files
    - <document>_pending_questions.md: Edge cases awaiting human input
    - <document>_changelog.md: History of changes made
    - <document>_current.md: Working copy of the document
"""

import json
import os
import sys
import re
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum

class IntegrityImpact(Enum):
    INCREASES = "increases"      # Recommendation improves accuracy/rigor
    DECREASES = "decreases"      # Recommendation would harm the document
    NEUTRAL = "neutral"          # Stylistic, no integrity impact
    UNCERTAIN = "uncertain"      # Requires human judgment
    CONFLICTS = "conflicts"      # Contradicts another recommendation

@dataclass
class Recommendation:
    id: str
    source: str                  # Review file or "human"
    category: str                # "factual", "structural", "stylistic", "methodological"
    description: str
    specific_change: str         # What exactly to change
    location: str                # Where in document (section, line, quote)
    rationale: str               # Why this change
    impact: Optional[IntegrityImpact] = None
    impact_reasoning: Optional[str] = None
    applied: bool = False
    rejected: bool = False
    rejection_reason: Optional[str] = None

@dataclass
class DocumentContext:
    document_path: str
    purpose: str
    audience: str
    constraints: list = field(default_factory=list)
    non_negotiables: list = field(default_factory=list)  # Things that must not change
    iteration: int = 0
    document_hash: str = ""

@dataclass
class PendingQuestion:
    recommendation_id: str
    question: str
    options: list
    context: str
    timestamp: str
    answered: bool = False
    answer: Optional[str] = None

def load_or_create_context(doc_path: str, purpose: str = None, audience: str = None) -> DocumentContext:
    """Load existing context or create new one."""
    context_path = Path(doc_path).with_suffix('.context.json')

    if context_path.exists() and not purpose:
        with open(context_path) as f:
            data = json.load(f)
            return DocumentContext(**data)

    # Create new context
    with open(doc_path) as f:
        content = f.read()
    doc_hash = hashlib.md5(content.encode()).hexdigest()[:12]

    context = DocumentContext(
        document_path=doc_path,
        purpose=purpose or "Academic working paper",
        audience=audience or "Academic researchers and informed public",
        document_hash=doc_hash
    )

    save_context(context)
    return context

def save_context(context: DocumentContext):
    """Save context to JSON file."""
    context_path = Path(context.document_path).with_suffix('.context.json')
    with open(context_path, 'w') as f:
        json.dump(asdict(context), f, indent=2)

def get_reviews_dir(doc_path: str) -> Path:
    """Get or create reviews directory."""
    reviews_dir = Path(doc_path).with_suffix('.reviews')
    reviews_dir.mkdir(exist_ok=True)
    return reviews_dir

def load_reviews(doc_path: str) -> list:
    """Load all review files from reviews directory."""
    reviews_dir = get_reviews_dir(doc_path)
    reviews = []

    for review_file in reviews_dir.glob('*.md'):
        with open(review_file) as f:
            reviews.append({
                'source': review_file.name,
                'content': f.read(),
                'path': str(review_file)
            })

    return reviews

def load_pending_questions(doc_path: str) -> list:
    """Load pending questions that need human input."""
    questions_path = Path(doc_path).with_suffix('.pending_questions.json')
    if questions_path.exists():
        with open(questions_path) as f:
            data = json.load(f)
            return [PendingQuestion(**q) for q in data]
    return []

def save_pending_questions(doc_path: str, questions: list):
    """Save pending questions."""
    questions_path = Path(doc_path).with_suffix('.pending_questions.json')
    with open(questions_path, 'w') as f:
        json.dump([asdict(q) for q in questions], f, indent=2)

    # Also write human-readable version
    readable_path = Path(doc_path).with_suffix('.pending_questions.md')
    with open(readable_path, 'w') as f:
        f.write("# Pending Questions for Human Review\n\n")
        f.write("Edit this file to answer questions, then save.\n")
        f.write("Format: Add your answer after 'ANSWER:' on each question.\n\n")
        f.write("---\n\n")

        for q in questions:
            if not q.answered:
                f.write(f"## Question: {q.recommendation_id}\n\n")
                f.write(f"**Question:** {q.question}\n\n")
                f.write(f"**Context:** {q.context}\n\n")
                f.write(f"**Options:**\n")
                for i, opt in enumerate(q.options, 1):
                    f.write(f"{i}. {opt}\n")
                f.write(f"\n**ANSWER:** \n\n")
                f.write("---\n\n")

def check_for_human_answers(doc_path: str, questions: list) -> list:
    """Check if human has answered any pending questions."""
    readable_path = Path(doc_path).with_suffix('.pending_questions.md')
    if not readable_path.exists():
        return questions

    with open(readable_path) as f:
        content = f.read()

    # Parse answers from the markdown file
    answer_pattern = r'## Question: (\S+).*?\*\*ANSWER:\*\*\s*(.+?)(?=---|$)'
    matches = re.findall(answer_pattern, content, re.DOTALL)

    answers = {m[0]: m[1].strip() for m in matches if m[1].strip()}

    for q in questions:
        if q.recommendation_id in answers and answers[q.recommendation_id]:
            q.answered = True
            q.answer = answers[q.recommendation_id]

    return questions

def append_to_changelog(doc_path: str, entry: str):
    """Append entry to changelog."""
    changelog_path = Path(doc_path).with_suffix('.changelog.md')

    with open(changelog_path, 'a') as f:
        f.write(f"\n## {datetime.now().isoformat()}\n\n")
        f.write(entry)
        f.write("\n")

def get_working_copy_path(doc_path: str) -> Path:
    """Get path to working copy of document."""
    return Path(doc_path).with_suffix('.working.md')

def initialize_working_copy(doc_path: str):
    """Create working copy if it doesn't exist."""
    working_path = get_working_copy_path(doc_path)
    if not working_path.exists():
        with open(doc_path) as f:
            content = f.read()
        with open(working_path, 'w') as f:
            f.write(content)
    return working_path

def generate_review_prompt(context: DocumentContext, document_content: str, review_type: str) -> str:
    """Generate a prompt for Claude to create a specific type of review."""

    prompts = {
        "factual": f"""Review this document for FACTUAL ACCURACY only.

Document Purpose: {context.purpose}
Target Audience: {context.audience}

Focus on:
- Claims that may be incorrect or misleading
- Statistics or numbers that need verification
- Citations that may be misrepresented
- Logical errors or non-sequiturs

For each issue found, provide:
1. Location (quote the relevant text)
2. The problem
3. Suggested correction
4. Confidence level (high/medium/low)

Document:
---
{document_content}
---

Provide your review in a structured format.""",

        "structural": f"""Review this document for STRUCTURE AND ARGUMENTATION only.

Document Purpose: {context.purpose}
Target Audience: {context.audience}

Focus on:
- Logical flow of arguments
- Missing steps in reasoning
- Sections that should be reordered
- Redundancies that could be eliminated
- Gaps in the argument

For each issue found, provide:
1. Location (section/paragraph)
2. The structural problem
3. Suggested reorganization
4. Why this improves the document

Document:
---
{document_content}
---

Provide your review in a structured format.""",

        "stylistic": f"""Review this document for WRITING STYLE only.

Document Purpose: {context.purpose}
Target Audience: {context.audience}

Focus on:
- Clarity of expression
- Appropriate tone for audience
- Jargon that may confuse readers
- Sentences that are too long or convoluted
- Passive voice overuse
- Repetitive phrasing

For each issue found, provide:
1. Location (quote the text)
2. The stylistic problem
3. Suggested rewrite
4. Why this is better for the audience

Document:
---
{document_content}
---

Provide your review in a structured format.""",

        "methodological": f"""Review this document for METHODOLOGICAL RIGOR only.

Document Purpose: {context.purpose}
Target Audience: {context.audience}

Focus on:
- Appropriateness of methods used
- Limitations that should be acknowledged
- Alternative interpretations not considered
- Generalizability of claims
- Potential biases in approach

For each issue found, provide:
1. Location (section/claim)
2. The methodological concern
3. Suggested addition or revision
4. How this strengthens the document

Document:
---
{document_content}
---

Provide your review in a structured format.""",

        "integrity_check": f"""You are evaluating whether a set of recommendations would INCREASE or DECREASE the integrity of this document.

Document Purpose: {context.purpose}
Target Audience: {context.audience}
Constraints: {json.dumps(context.constraints)}
Non-negotiables (must not change): {json.dumps(context.non_negotiables)}

For each recommendation, assess:
1. Does this make the document MORE accurate/rigorous? → INCREASES
2. Does this make the document LESS accurate/rigorous? → DECREASES
3. Is this purely stylistic with no accuracy impact? → NEUTRAL
4. Does this require human judgment on values/priorities? → UNCERTAIN
5. Does this contradict another recommendation? → CONFLICTS

Be conservative: when in doubt, mark as UNCERTAIN rather than applying changes that might harm the document.

Document:
---
{document_content}
---"""
    }

    return prompts.get(review_type, prompts["factual"])

def create_evaluation_prompt(context: DocumentContext, document_content: str, recommendations: list) -> str:
    """Create prompt for evaluating recommendations."""

    rec_text = "\n\n".join([
        f"### Recommendation {r['id']}\n"
        f"Source: {r['source']}\n"
        f"Category: {r['category']}\n"
        f"Description: {r['description']}\n"
        f"Specific Change: {r['specific_change']}\n"
        f"Location: {r['location']}\n"
        f"Rationale: {r['rationale']}"
        for r in recommendations
    ])

    return f"""Evaluate these recommendations for their impact on document integrity.

## Document Context
Purpose: {context.purpose}
Audience: {context.audience}
Constraints: {json.dumps(context.constraints)}
Non-negotiables: {json.dumps(context.non_negotiables)}

## Document Content
{document_content[:5000]}... [truncated]

## Recommendations to Evaluate
{rec_text}

## Your Task
For EACH recommendation, provide:

```json
{{
  "id": "<recommendation_id>",
  "impact": "INCREASES|DECREASES|NEUTRAL|UNCERTAIN|CONFLICTS",
  "reasoning": "<why this assessment>",
  "confidence": "high|medium|low",
  "question_for_human": "<if UNCERTAIN, what question would help resolve it?>"
}}
```

Output a JSON array of evaluations."""

def print_status(context: DocumentContext, reviews: list, pending: list, applied: int, rejected: int):
    """Print current status."""
    print("\n" + "="*60)
    print(f"DOCUMENT REVIEW SYSTEM - Iteration {context.iteration}")
    print("="*60)
    print(f"Document: {context.document_path}")
    print(f"Purpose: {context.purpose}")
    print(f"Audience: {context.audience}")
    print(f"Reviews loaded: {len(reviews)}")
    print(f"Pending questions: {len([q for q in pending if not q.answered])}")
    print(f"Changes applied: {applied}")
    print(f"Changes rejected: {rejected}")
    print("="*60 + "\n")

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Iterative Document Review System')
    parser.add_argument('document', help='Path to the document to review')
    parser.add_argument('--purpose', help='Purpose of the document')
    parser.add_argument('--audience', help='Target audience')
    parser.add_argument('--add-constraint', action='append', dest='constraints',
                        help='Add a constraint (can be repeated)')
    parser.add_argument('--add-non-negotiable', action='append', dest='non_negotiables',
                        help='Add something that must not change (can be repeated)')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Run in interactive mode (pause for input)')
    parser.add_argument('--generate-reviews', '-g', action='store_true',
                        help='Generate AI reviews before starting')
    parser.add_argument('--single-pass', '-s', action='store_true',
                        help='Run only one iteration')

    args = parser.parse_args()

    if not os.path.exists(args.document):
        print(f"Error: Document not found: {args.document}")
        sys.exit(1)

    # Load or create context
    context = load_or_create_context(args.document, args.purpose, args.audience)

    # Add any new constraints
    if args.constraints:
        context.constraints.extend(args.constraints)
    if args.non_negotiables:
        context.non_negotiables.extend(args.non_negotiables)

    save_context(context)

    # Initialize working copy
    working_path = initialize_working_copy(args.document)

    # Initialize changelog
    changelog_path = Path(args.document).with_suffix('.changelog.md')
    if not changelog_path.exists():
        with open(changelog_path, 'w') as f:
            f.write(f"# Changelog for {args.document}\n\n")
            f.write(f"Started: {datetime.now().isoformat()}\n")
            f.write(f"Purpose: {context.purpose}\n")
            f.write(f"Audience: {context.audience}\n\n")

    # Create reviews directory and add instructions
    reviews_dir = get_reviews_dir(args.document)
    instructions_path = reviews_dir / "README.md"
    if not instructions_path.exists():
        with open(instructions_path, 'w') as f:
            f.write("""# Reviews Directory

Place review files here in Markdown format.

## Format for Reviews

Each review file should contain recommendations in this format:

```
## Recommendation: <short_id>

**Category:** factual|structural|stylistic|methodological

**Location:** <quote or section reference>

**Problem:** <description of the issue>

**Suggested Change:** <specific text or structural change>

**Rationale:** <why this improves the document>
```

## Review Types

- **factual**: Corrections to facts, statistics, citations
- **structural**: Changes to organization and flow
- **stylistic**: Writing style improvements
- **methodological**: Improvements to rigor and methodology

## Adding Human Reviews

Simply create a new .md file in this directory with your recommendations.
The system will pick it up on the next iteration.
""")

    # Load existing reviews
    reviews = load_reviews(args.document)

    # Load pending questions and check for answers
    pending_questions = load_pending_questions(args.document)
    pending_questions = check_for_human_answers(args.document, pending_questions)
    save_pending_questions(args.document, pending_questions)

    # Print status
    print_status(context, reviews, pending_questions, 0, 0)

    print("""
REVIEW LOOP SYSTEM INITIALIZED

This system works with Claude Code to iteratively improve your document.

To use this system:
1. Add review files to: {reviews_dir}
2. Answer pending questions in: {questions_file}
3. Run iterations with: python review_loop.py {doc}

The system will:
- Parse recommendations from review files
- Evaluate each for integrity impact
- Apply beneficial changes automatically
- Queue uncertain cases for your input
- Log all changes to the changelog

To generate AI reviews, run Claude Code and ask it to:
"Please review {doc} and save your review to {reviews_dir}/ai_review_<type>.md"

Review types: factual, structural, stylistic, methodological
""".format(
        reviews_dir=reviews_dir,
        questions_file=Path(args.document).with_suffix('.pending_questions.md'),
        doc=args.document
    ))

    if args.generate_reviews:
        print("\nTo generate reviews, use Claude Code with prompts like:")
        print(f'  "Review {args.document} for factual accuracy and save to {reviews_dir}/factual_review.md"')
        print(f'  "Review {args.document} for structural issues and save to {reviews_dir}/structural_review.md"')

    if reviews:
        print(f"\nFound {len(reviews)} existing reviews:")
        for r in reviews:
            print(f"  - {r['source']}")
    else:
        print("\nNo reviews found yet. Add review files to get started.")

    # Save state for Claude Code to work with
    state = {
        "document_path": args.document,
        "working_path": str(working_path),
        "reviews_dir": str(reviews_dir),
        "context": asdict(context),
        "pending_questions": [asdict(q) for q in pending_questions],
        "reviews_loaded": len(reviews),
        "iteration": context.iteration
    }

    state_path = Path(args.document).with_suffix('.state.json')
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"\nState saved to: {state_path}")
    print("\nReady for review iterations.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
