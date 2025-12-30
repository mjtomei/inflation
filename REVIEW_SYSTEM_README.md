# Iterative Document Review System

A system for continuously improving documents through AI and human review, with autonomous decision-making on which changes improve document integrity.

## Quick Start

### 1. Initialize the System

```bash
python review_loop.py inflation_analysis.md \
    --purpose "Academic working paper on inflation measurement" \
    --audience "Academic researchers and informed public policy readers"
```

This creates:
- `inflation_analysis.context.json` - Document context and constraints
- `inflation_analysis.reviews/` - Directory for review files
- `inflation_analysis.working.md` - Working copy of the document
- `inflation_analysis.changelog.md` - Log of all changes
- `inflation_analysis.state.json` - Current state for Claude Code

### 2. Add Reviews

Place review files in the `.reviews/` directory. Reviews can be:
- AI-generated reviews (ask Claude Code to create them)
- Human reviews
- Existing peer reviews (like `peer_review.md` or `editorial_review.md`)

Copy existing reviews:
```bash
cp peer_review.md inflation_analysis.reviews/
cp editorial_review.md inflation_analysis.reviews/
```

### 3. Parse Reviews into Recommendations

```bash
python review_processor.py inflation_analysis.md --parse-reviews
```

### 4. Run the Review Loop with Claude Code

Ask Claude Code:

```
Please help me run the document review loop for inflation_analysis.md.

1. First, check the current status:
   python review_processor.py inflation_analysis.md --status

2. Generate evaluation prompt:
   python review_processor.py inflation_analysis.md --generate-eval-prompt

3. Evaluate the recommendations (respond with JSON)

4. Apply evaluations:
   python review_processor.py inflation_analysis.md --apply-evaluation '<json>'

5. List approved changes:
   python review_processor.py inflation_analysis.md --list-approved

6. For each approved change, apply it to the document and mark as applied:
   python review_processor.py inflation_analysis.md --mark-applied <rec_id>

7. List uncertain items for my review:
   python review_processor.py inflation_analysis.md --list-uncertain

Continue iterating until convergence.
```

## Integrity Impact Categories

The system evaluates each recommendation for its impact on document **integrity**:

| Impact | Meaning | Action |
|--------|---------|--------|
| **INCREASES** | Makes document more accurate/rigorous | Auto-approve |
| **DECREASES** | Would harm accuracy | Auto-reject |
| **NEUTRAL** | Stylistic only | Auto-approve |
| **UNCERTAIN** | Needs human judgment | Queue for user |
| **CONFLICTS** | Contradicts another change | Queue for user |

## File Structure

```
document.md                    # Original document
document.context.json          # Purpose, audience, constraints
document.working.md            # Working copy (changes applied here)
document.recommendations.json  # All parsed recommendations
document.changelog.md          # History of changes
document.state.json           # State for Claude Code
document.pending_questions.md  # Questions for human (editable)
document.reviews/             # Review files directory
  ├── README.md               # Instructions for adding reviews
  ├── peer_review.md          # Example review
  ├── editorial_review.md     # Example review
  └── ai_factual_review.md    # AI-generated review
```

## Adding Constraints

You can add constraints that the system will respect:

```bash
# Things that must be considered
python review_loop.py doc.md --add-constraint "Maintain academic tone"
python review_loop.py doc.md --add-constraint "Keep under 20 pages"

# Things that must not change
python review_loop.py doc.md --add-non-negotiable "Section 8 democratization thesis"
python review_loop.py doc.md --add-non-negotiable "Argentina case study"
```

## Answering Pending Questions

When the system encounters uncertain recommendations, it adds them to `document.pending_questions.md`. To answer:

1. Open the file
2. Find questions marked with `**ANSWER:**`
3. Type your answer after the colon
4. Save the file
5. Run the review loop again - it will pick up your answers

## Generating AI Reviews

Ask Claude Code to generate specific types of reviews:

```
Please review inflation_analysis.md for FACTUAL ACCURACY and save your review to inflation_analysis.reviews/ai_factual_review.md

Focus on:
- Claims that may be incorrect
- Statistics that need verification
- Citations that may be misrepresented

Use the format:
## Recommendation: <id>
**Category:** factual
**Location:** <quote or section>
**Problem:** <description>
**Suggested Change:** <specific change>
**Rationale:** <why>
```

## Example Claude Code Session

```
User: Let's improve inflation_analysis.md using the review system.

Claude: I'll start by checking the current state.
[runs: python review_processor.py inflation_analysis.md --status]

Claude: I see 45 recommendations, 30 unevaluated. Let me evaluate them.
[runs: python review_processor.py inflation_analysis.md --generate-eval-prompt]
[evaluates and responds with JSON]
[runs: python review_processor.py inflation_analysis.md --apply-evaluation '...']

Claude: 15 recommendations approved. Let me apply them.
[for each approved: reads document, applies change, marks applied]

Claude: 8 uncertain items need your input. Here they are:
1. [rec_id]: Should we add more caveats about AI limitations?
   Options: Yes (more conservative), No (maintain current framing)

Would you like to answer these, or should I continue with non-blocking changes?

User: Yes to #1, continue with others.

Claude: [applies user decision, continues processing]
```

## Tips

1. **Start conservative**: Mark more things as UNCERTAIN initially, then loosen as you build trust

2. **Use non-negotiables**: Protect key arguments you don't want changed

3. **Review the changelog**: Check `document.changelog.md` to see what's been changed

4. **Iterate**: Run multiple passes - early passes catch obvious issues, later passes refine

5. **Mix human and AI reviews**: The system works best with both perspectives

## Troubleshooting

**No recommendations parsed?**
- Check that review files use a supported format (see README.md in reviews directory)
- Try a more structured format with `## Recommendation:` headers

**Changes not applying correctly?**
- Check the working copy, not the original
- Review the changelog for error messages

**Too many uncertain items?**
- Add more constraints to clarify priorities
- Answer some pending questions to train the system's judgment
