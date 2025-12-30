#!/usr/bin/env python3
"""
Review Processor - The decision-making engine for the review loop.

This script is designed to be called by Claude Code to:
1. Parse recommendations from review files
2. Evaluate their integrity impact
3. Apply approved changes
4. Queue uncertain cases

Usage (typically called by Claude Code):
    python review_processor.py <document.md> --parse-reviews
    python review_processor.py <document.md> --evaluate
    python review_processor.py <document.md> --apply-approved
    python review_processor.py <document.md> --status
"""

import json
import os
import sys
import re
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict
from enum import Enum

class IntegrityImpact(Enum):
    INCREASES = "increases"
    DECREASES = "decreases"
    NEUTRAL = "neutral"
    UNCERTAIN = "uncertain"
    CONFLICTS = "conflicts"

def load_state(doc_path: str) -> dict:
    """Load the current state."""
    state_path = Path(doc_path).with_suffix('.state.json')
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    return {}

def save_state(doc_path: str, state: dict):
    """Save state."""
    state_path = Path(doc_path).with_suffix('.state.json')
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)

def load_recommendations(doc_path: str) -> list:
    """Load parsed recommendations."""
    rec_path = Path(doc_path).with_suffix('.recommendations.json')
    if rec_path.exists():
        with open(rec_path) as f:
            return json.load(f)
    return []

def save_recommendations(doc_path: str, recommendations: list):
    """Save recommendations."""
    rec_path = Path(doc_path).with_suffix('.recommendations.json')
    with open(rec_path, 'w') as f:
        json.dump(recommendations, f, indent=2)

def parse_review_file(review_path: str, source_name: str) -> list:
    """Parse a review file into structured recommendations."""
    with open(review_path) as f:
        content = f.read()

    recommendations = []

    # Pattern 1: "Reviewer Comment X:" format (peer review style)
    reviewer_pattern = r'###\s*Reviewer Comment\s*(\d+)[:\s]*([^\n]*)\n(.*?)(?=###\s*Reviewer Comment|\Z)'
    matches = re.findall(reviewer_pattern, content, re.DOTALL)

    for num, title, body in matches:
        # Look for suggested revision
        suggested = re.search(r'\*\*Suggested revision[:\*]*\s*(.+?)(?=\n\n---|\n\n###|\Z)', body, re.DOTALL | re.IGNORECASE)
        suggestion = suggested.group(1).strip() if suggested else ""

        # Extract the quoted concern
        concern = re.search(r'>\s*(.+?)(?=\n\n|\*\*Suggested)', body, re.DOTALL)
        concern_text = concern.group(1).strip() if concern else body[:300]

        rec = {
            'id': f"{source_name}_comment_{num}",
            'source': source_name,
            'category': categorize_recommendation(body),
            'description': title.strip() if title.strip() else concern_text[:100],
            'specific_change': suggestion if suggestion else "See reviewer comment",
            'location': extract_location(body),
            'rationale': concern_text[:500],
            'impact': None,
            'impact_reasoning': None,
            'applied': False,
            'rejected': False,
            'rejection_reason': None
        }
        recommendations.append(rec)

    # Pattern 2: Editorial review "### N. Title" format
    if not recommendations:
        editorial_pattern = r'###\s*(\d+)\.\s*([^\n]+)\n(.*?)(?=###\s*\d+\.|\n##\s|\Z)'
        matches = re.findall(editorial_pattern, content, re.DOTALL)

        for num, title, body in matches:
            # Look for suggested revision
            suggested = re.search(r'\*\*Suggested (?:revision|remedy)[:\*]*\s*(.+?)(?=\n\n---|\n\n###|\Z)', body, re.DOTALL | re.IGNORECASE)
            suggestion = suggested.group(1).strip() if suggested else ""

            # Look for problem statement
            problem = re.search(r'\*\*(?:Problem|Assessment)[:\*]*\s*(.+?)(?=\n\n|\*\*Suggested)', body, re.DOTALL | re.IGNORECASE)
            problem_text = problem.group(1).strip() if problem else ""

            if suggestion or problem_text:
                rec = {
                    'id': f"{source_name}_{num}",
                    'source': source_name,
                    'category': categorize_recommendation(title + body),
                    'description': title.strip(),
                    'specific_change': suggestion if suggestion else problem_text[:300],
                    'location': extract_location(body),
                    'rationale': problem_text[:500] if problem_text else "See review",
                    'impact': None,
                    'impact_reasoning': None,
                    'applied': False,
                    'rejected': False,
                    'rejection_reason': None
                }
                recommendations.append(rec)

    # Pattern 3: "Bias N:" format from editorial review
    bias_pattern = r'###\s*Bias\s*(\d+)[:\s]*([^\n]+)\n(.*?)(?=###\s*Bias|\n##\s|\Z)'
    bias_matches = re.findall(bias_pattern, content, re.DOTALL)

    for num, title, body in bias_matches:
        suggested = re.search(r'\*\*Suggested (?:revision|remedy)[:\*]*\s*(.+?)(?=\n\n---|\n\n###|\Z)', body, re.DOTALL | re.IGNORECASE)
        suggestion = suggested.group(1).strip() if suggested else ""

        assessment = re.search(r'\*\*Assessment[:\*]*\s*(.+?)(?=\n\n|\*\*Suggested)', body, re.DOTALL | re.IGNORECASE)
        assessment_text = assessment.group(1).strip() if assessment else ""

        if suggestion:
            rec = {
                'id': f"{source_name}_bias_{num}",
                'source': source_name,
                'category': 'methodological',
                'description': f"Bias: {title.strip()}",
                'specific_change': suggestion,
                'location': "throughout",
                'rationale': assessment_text[:500] if assessment_text else "See bias analysis",
                'impact': None,
                'impact_reasoning': None,
                'applied': False,
                'rejected': False,
                'rejection_reason': None
            }
            recommendations.append(rec)

    # Pattern 4: "Passage N:" rewrite suggestions
    passage_pattern = r'###\s*Passage\s*(\d+)[:\s]*([^\n]*)\n(.*?)(?=###\s*Passage|\n##\s|\Z)'
    passage_matches = re.findall(passage_pattern, content, re.DOTALL)

    for num, title, body in passage_matches:
        current = re.search(r'\*\*Current[:\*]*\s*>?\s*(.+?)(?=\n\n\*\*Problem|\*\*Suggested)', body, re.DOTALL | re.IGNORECASE)
        suggested = re.search(r'\*\*Suggested[:\*]*\s*>?\s*(.+?)(?=\n\n---|\n\n###|\Z)', body, re.DOTALL | re.IGNORECASE)

        if suggested:
            rec = {
                'id': f"{source_name}_passage_{num}",
                'source': source_name,
                'category': 'stylistic',
                'description': title.strip() if title.strip() else f"Rewrite passage {num}",
                'specific_change': suggested.group(1).strip(),
                'location': current.group(1).strip()[:100] if current else "unspecified",
                'rationale': "See suggested rewrite",
                'impact': None,
                'impact_reasoning': None,
                'applied': False,
                'rejected': False,
                'rejection_reason': None
            }
            recommendations.append(rec)

    # Pattern 5: Structural problems
    structural_pattern = r'###\s*Structural Problem\s*(\d+)[:\s]*([^\n]+)\n(.*?)(?=###\s*Structural Problem|\n##\s|\Z)'
    structural_matches = re.findall(structural_pattern, content, re.DOTALL)

    for num, title, body in structural_matches:
        suggested = re.search(r'\*\*Suggested (?:revision|remedy)[:\*]*\s*(.+?)(?=\n\n---|\n\n###|\Z)', body, re.DOTALL | re.IGNORECASE)
        suggestion = suggested.group(1).strip() if suggested else ""

        if suggestion:
            rec = {
                'id': f"{source_name}_structural_{num}",
                'source': source_name,
                'category': 'structural',
                'description': title.strip(),
                'specific_change': suggestion,
                'location': "document structure",
                'rationale': "See structural analysis",
                'impact': None,
                'impact_reasoning': None,
                'applied': False,
                'rejected': False,
                'rejection_reason': None
            }
            recommendations.append(rec)

    # Pattern 6: Simple "Suggested revision:" anywhere
    if not recommendations:
        simple_pattern = r'\*\*Suggested (?:revision|remedy)[:\*]*\s*(.+?)(?=\n\n---|\n\n\*\*|\Z)'
        matches = re.findall(simple_pattern, content, re.DOTALL | re.IGNORECASE)

        for i, suggestion in enumerate(matches, 1):
            suggestion = suggestion.strip()
            if len(suggestion) > 20:  # Skip very short matches
                rec = {
                    'id': f"{source_name}_suggestion_{i}",
                    'source': source_name,
                    'category': categorize_recommendation(suggestion),
                    'description': suggestion[:100],
                    'specific_change': suggestion,
                    'location': "unspecified",
                    'rationale': "See suggested revision",
                    'impact': None,
                    'impact_reasoning': None,
                    'applied': False,
                    'rejected': False,
                    'rejection_reason': None
                }
                recommendations.append(rec)

    return recommendations

def parse_recommendation_section(rec_id: str, section: str, source: str) -> dict:
    """Parse a single recommendation section."""
    # Extract fields
    category = extract_field(section, ['category', 'type'])
    location = extract_field(section, ['location', 'where', 'section'])
    problem = extract_field(section, ['problem', 'issue', 'concern'])
    change = extract_field(section, ['suggested change', 'change', 'suggestion', 'fix', 'revision'])
    rationale = extract_field(section, ['rationale', 'reason', 'why', 'because'])

    if not change and not problem:
        return None

    return {
        'id': f"{source}_{rec_id}".replace(' ', '_'),
        'source': source,
        'category': category or categorize_recommendation(section),
        'description': problem or change[:200] if change else "See details",
        'specific_change': change or problem,
        'location': location or "unspecified",
        'rationale': rationale or "See recommendation",
        'impact': None,
        'impact_reasoning': None,
        'applied': False,
        'rejected': False,
        'rejection_reason': None
    }

def extract_field(text: str, field_names: list) -> str:
    """Extract a field value from text."""
    for name in field_names:
        pattern = rf'\*\*{name}\*\*[:\s]*(.+?)(?=\*\*|\n\n|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    return ""

def extract_specific_change(text: str) -> str:
    """Extract the specific change from recommendation text."""
    patterns = [
        r'(?:suggest(?:ed)?|recommend(?:ed)?|change to|replace with|should be)[:\s]*["\']?(.+?)["\']?(?:\.|$)',
        r'(?:instead|better)[:\s]*["\']?(.+?)["\']?(?:\.|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return text.strip()[:500]

def extract_location(text: str) -> str:
    """Extract location reference from text."""
    patterns = [
        r'(?:in section|section)[:\s]*["\']?([^"\'.\n]+)',
        r'(?:line|paragraph|page)[:\s]*(\d+)',
        r'["\']([^"\']{10,50})["\']',  # Quoted text
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "unspecified"

def extract_rationale(text: str) -> str:
    """Extract rationale from text."""
    patterns = [
        r'(?:because|since|as|this would|this will)[:\s]*(.+?)(?:\.|$)',
        r'(?:improves?|helps?|makes?)[:\s]*(.+?)(?:\.|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "See full recommendation"

def categorize_recommendation(text: str) -> str:
    """Categorize a recommendation based on its content."""
    text_lower = text.lower()

    factual_keywords = ['incorrect', 'wrong', 'error', 'fact', 'data', 'statistic', 'citation', 'source', 'verify']
    structural_keywords = ['structure', 'organization', 'flow', 'order', 'section', 'move', 'reorganize', 'redundant']
    stylistic_keywords = ['style', 'clarity', 'tone', 'word', 'phrase', 'sentence', 'rewrite', 'awkward', 'verbose']
    methodological_keywords = ['method', 'approach', 'rigor', 'limitation', 'bias', 'assumption', 'validity']

    scores = {
        'factual': sum(1 for k in factual_keywords if k in text_lower),
        'structural': sum(1 for k in structural_keywords if k in text_lower),
        'stylistic': sum(1 for k in stylistic_keywords if k in text_lower),
        'methodological': sum(1 for k in methodological_keywords if k in text_lower)
    }

    if max(scores.values()) == 0:
        return 'general'

    return max(scores, key=scores.get)

def parse_all_reviews(doc_path: str) -> list:
    """Parse all review files and return recommendations."""
    reviews_dir = Path(doc_path).with_suffix('.reviews')
    all_recommendations = []

    if not reviews_dir.exists():
        return []

    for review_file in reviews_dir.glob('*.md'):
        if review_file.name == 'README.md':
            continue

        recs = parse_review_file(str(review_file), review_file.stem)
        all_recommendations.extend(recs)

    return all_recommendations

def get_evaluation_summary(recommendations: list) -> dict:
    """Get summary of recommendation evaluations."""
    summary = {
        'total': len(recommendations),
        'increases': len([r for r in recommendations if r.get('impact') == 'increases']),
        'decreases': len([r for r in recommendations if r.get('impact') == 'decreases']),
        'neutral': len([r for r in recommendations if r.get('impact') == 'neutral']),
        'uncertain': len([r for r in recommendations if r.get('impact') == 'uncertain']),
        'conflicts': len([r for r in recommendations if r.get('impact') == 'conflicts']),
        'unevaluated': len([r for r in recommendations if r.get('impact') is None]),
        'applied': len([r for r in recommendations if r.get('applied')]),
        'rejected': len([r for r in recommendations if r.get('rejected')])
    }
    return summary

def generate_evaluation_request(doc_path: str, recommendations: list) -> str:
    """Generate a prompt for Claude to evaluate recommendations."""
    state = load_state(doc_path)
    context = state.get('context', {})

    working_path = Path(doc_path).with_suffix('.working.md')
    if working_path.exists():
        with open(working_path) as f:
            doc_content = f.read()
    else:
        with open(doc_path) as f:
            doc_content = f.read()

    # Only include unevaluated recommendations
    to_evaluate = [r for r in recommendations if r.get('impact') is None]

    if not to_evaluate:
        return "All recommendations have been evaluated."

    rec_text = "\n\n".join([
        f"### {r['id']}\n"
        f"Source: {r['source']}\n"
        f"Category: {r['category']}\n"
        f"Description: {r['description']}\n"
        f"Change: {r['specific_change'][:300]}...\n"
        f"Location: {r['location']}\n"
        f"Rationale: {r['rationale']}"
        for r in to_evaluate[:20]  # Limit to 20 at a time
    ])

    prompt = f"""# Recommendation Evaluation Request

## Document Context
- **Purpose**: {context.get('purpose', 'Academic paper')}
- **Audience**: {context.get('audience', 'Researchers')}
- **Constraints**: {json.dumps(context.get('constraints', []))}
- **Non-negotiables**: {json.dumps(context.get('non_negotiables', []))}

## Task
Evaluate each recommendation below for its impact on document INTEGRITY.

**Integrity** means: accuracy, rigor, honesty, and appropriateness for the stated purpose/audience.

For each recommendation, determine:
- **INCREASES**: Makes the document more accurate, rigorous, or honest
- **DECREASES**: Would make the document less accurate or introduce errors
- **NEUTRAL**: Purely stylistic, no impact on accuracy
- **UNCERTAIN**: Requires human judgment on values or priorities
- **CONFLICTS**: Contradicts another recommendation

## Recommendations to Evaluate

{rec_text}

## Document Content (first 3000 chars)
{doc_content[:3000]}...

## Output Format
Provide your evaluation as a JSON array:
```json
[
  {{
    "id": "<recommendation_id>",
    "impact": "increases|decreases|neutral|uncertain|conflicts",
    "reasoning": "<brief explanation>",
    "confidence": "high|medium|low",
    "question_for_human": "<if uncertain, what question would help?>"
  }}
]
```

Be CONSERVATIVE: if in doubt, mark as UNCERTAIN rather than risk applying harmful changes."""

    return prompt

def apply_evaluation(doc_path: str, evaluation_json: str):
    """Apply evaluation results to recommendations."""
    recommendations = load_recommendations(doc_path)

    try:
        # Try to parse JSON from the response
        # Handle markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', evaluation_json, re.DOTALL)
        if json_match:
            evaluations = json.loads(json_match.group(1))
        else:
            evaluations = json.loads(evaluation_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing evaluation JSON: {e}")
        return False

    # Apply evaluations
    eval_map = {e['id']: e for e in evaluations}

    for rec in recommendations:
        if rec['id'] in eval_map:
            ev = eval_map[rec['id']]
            rec['impact'] = ev.get('impact', 'uncertain')
            rec['impact_reasoning'] = ev.get('reasoning', '')

            # Auto-reject decreases
            if rec['impact'] == 'decreases':
                rec['rejected'] = True
                rec['rejection_reason'] = ev.get('reasoning', 'Would decrease document integrity')

    save_recommendations(doc_path, recommendations)
    return True

def get_approved_changes(doc_path: str) -> list:
    """Get recommendations approved for application."""
    recommendations = load_recommendations(doc_path)

    approved = [
        r for r in recommendations
        if r.get('impact') in ['increases', 'neutral']
        and not r.get('applied')
        and not r.get('rejected')
    ]

    return approved

def mark_applied(doc_path: str, rec_id: str, success: bool, notes: str = ""):
    """Mark a recommendation as applied or failed."""
    recommendations = load_recommendations(doc_path)

    for rec in recommendations:
        if rec['id'] == rec_id:
            if success:
                rec['applied'] = True
            else:
                rec['rejected'] = True
                rec['rejection_reason'] = notes
            break

    save_recommendations(doc_path, recommendations)

    # Log to changelog
    changelog_path = Path(doc_path).with_suffix('.changelog.md')
    with open(changelog_path, 'a') as f:
        status = "APPLIED" if success else "FAILED"
        f.write(f"\n### [{status}] {rec_id}\n")
        f.write(f"Time: {datetime.now().isoformat()}\n")
        if notes:
            f.write(f"Notes: {notes}\n")

def get_uncertain_recommendations(doc_path: str) -> list:
    """Get recommendations marked as uncertain."""
    recommendations = load_recommendations(doc_path)
    return [r for r in recommendations if r.get('impact') == 'uncertain']

def print_status(doc_path: str):
    """Print current status."""
    recommendations = load_recommendations(doc_path)
    summary = get_evaluation_summary(recommendations)
    state = load_state(doc_path)

    print("\n" + "="*60)
    print("REVIEW PROCESSOR STATUS")
    print("="*60)
    print(f"Document: {doc_path}")
    print(f"Iteration: {state.get('context', {}).get('iteration', 0)}")
    print()
    print("Recommendations:")
    print(f"  Total:       {summary['total']}")
    print(f"  Unevaluated: {summary['unevaluated']}")
    print(f"  Increases:   {summary['increases']}")
    print(f"  Decreases:   {summary['decreases']}")
    print(f"  Neutral:     {summary['neutral']}")
    print(f"  Uncertain:   {summary['uncertain']}")
    print(f"  Conflicts:   {summary['conflicts']}")
    print()
    print("Progress:")
    print(f"  Applied:     {summary['applied']}")
    print(f"  Rejected:    {summary['rejected']}")
    print("="*60)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Review Processor')
    parser.add_argument('document', help='Path to the document')
    parser.add_argument('--parse-reviews', action='store_true',
                        help='Parse all review files into recommendations')
    parser.add_argument('--generate-eval-prompt', action='store_true',
                        help='Generate prompt for evaluating recommendations')
    parser.add_argument('--apply-evaluation', type=str,
                        help='Apply evaluation results (JSON string or @filename)')
    parser.add_argument('--list-approved', action='store_true',
                        help='List recommendations approved for application')
    parser.add_argument('--list-uncertain', action='store_true',
                        help='List recommendations needing human judgment')
    parser.add_argument('--mark-applied', type=str,
                        help='Mark a recommendation as applied')
    parser.add_argument('--mark-failed', type=str,
                        help='Mark a recommendation as failed')
    parser.add_argument('--notes', type=str, default='',
                        help='Notes for mark-applied/mark-failed')
    parser.add_argument('--status', action='store_true',
                        help='Print current status')
    parser.add_argument('--export-for-claude', action='store_true',
                        help='Export state for Claude Code to work with')

    args = parser.parse_args()

    if not os.path.exists(args.document):
        print(f"Error: Document not found: {args.document}")
        sys.exit(1)

    if args.parse_reviews:
        recommendations = parse_all_reviews(args.document)
        existing = load_recommendations(args.document)

        # Merge new recommendations with existing
        existing_ids = {r['id'] for r in existing}
        new_recs = [r for r in recommendations if r['id'] not in existing_ids]

        all_recs = existing + new_recs
        save_recommendations(args.document, all_recs)

        print(f"Parsed {len(new_recs)} new recommendations")
        print(f"Total recommendations: {len(all_recs)}")

    elif args.generate_eval_prompt:
        recommendations = load_recommendations(args.document)
        prompt = generate_evaluation_request(args.document, recommendations)
        print(prompt)

    elif args.apply_evaluation:
        eval_json = args.apply_evaluation
        if eval_json.startswith('@'):
            with open(eval_json[1:]) as f:
                eval_json = f.read()

        if apply_evaluation(args.document, eval_json):
            print("Evaluation applied successfully")
            print_status(args.document)
        else:
            print("Failed to apply evaluation")

    elif args.list_approved:
        approved = get_approved_changes(args.document)
        print(f"\nApproved recommendations ({len(approved)}):\n")
        for r in approved:
            print(f"  [{r['id']}] ({r['impact']}) {r['description'][:60]}...")

    elif args.list_uncertain:
        uncertain = get_uncertain_recommendations(args.document)
        print(f"\nUncertain recommendations ({len(uncertain)}):\n")
        for r in uncertain:
            print(f"  [{r['id']}] {r['description'][:60]}...")
            if r.get('impact_reasoning'):
                print(f"    Reasoning: {r['impact_reasoning'][:80]}...")

    elif args.mark_applied:
        mark_applied(args.document, args.mark_applied, True, args.notes)
        print(f"Marked {args.mark_applied} as applied")

    elif args.mark_failed:
        mark_applied(args.document, args.mark_failed, False, args.notes)
        print(f"Marked {args.mark_failed} as failed")

    elif args.status:
        print_status(args.document)

    elif args.export_for_claude:
        recommendations = load_recommendations(args.document)
        state = load_state(args.document)

        export = {
            'document': args.document,
            'state': state,
            'summary': get_evaluation_summary(recommendations),
            'approved_changes': get_approved_changes(args.document),
            'uncertain': get_uncertain_recommendations(args.document),
            'next_steps': []
        }

        if export['summary']['unevaluated'] > 0:
            export['next_steps'].append('Evaluate unevaluated recommendations')
        if export['approved_changes']:
            export['next_steps'].append(f"Apply {len(export['approved_changes'])} approved changes")
        if export['uncertain']:
            export['next_steps'].append(f"Resolve {len(export['uncertain'])} uncertain recommendations")

        print(json.dumps(export, indent=2))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
