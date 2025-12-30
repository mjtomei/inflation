# AI Detection Experiments Session Log

**Date**: December 30, 2025
**Tool**: Claude Code (Claude Opus 4.5)

## Session Overview

This session explored methods to reduce AI detectability of the inflation analysis paper while documenting the experiments for transparency.

## Work Completed

### 1. AI Detection System Setup

Installed and configured two open-source AI detection systems:
- **RoBERTa-base OpenAI Detector** (2019): HuggingFace model trained on GPT-2 output
- **Binoculars** (ICML 2024): Modern detector using perplexity ratios

### 2. Baseline Testing

Tested the original paper (`inflation_analysis.md`):
- RoBERTa score: **93.1% AI**
- Binoculars score: **~5% AI** (95% human)

Key finding: The two detectors completely disagreed.

### 3. Humanization Approaches Developed

Created multiple Python scripts to transform text:

| Script | Approach | Best Score |
|--------|----------|------------|
| `humanize_text.py` | Conservative linguistic transforms | ~93% |
| `aggressive_humanize.py` | Informal replacements, interjections | 88-89% |
| `perplexity_humanize.py` | Uncommon synonyms, unusual starters | ~91% |
| `combined_humanize.py` | All approaches combined | 88.2% |
| `noise_injection.py` | Typos, spelling variants, fragments | ~89% |
| `final_humanize.py` | Light, non-compounding transforms | ~93% |

### 4. Control Experiments

Tested known human-written academic text against RoBERTa:
- Classic economics textbook prose: **99.9% AI**
- Informal economics explanation: **81.1% AI**
- Twitter thread format: **76.3% AI**
- Internet meme speak: **55.8% AI**

**Conclusion**: RoBERTa flags formal academic writing as AI regardless of actual authorship.

### 5. Key Findings

1. **Detector disagreement**: RoBERTa and Binoculars give opposite results
2. **Surface transforms ineffective**: Word substitutions don't significantly reduce scores
3. **Tradeoff exists**: 88% achievable but only with degraded readability
4. **Academic style triggers detection**: Formal writing itself is flagged

### 6. Files Created

**Humanization scripts**:
- `ai_detector.py` - RoBERTa detection wrapper
- `humanize_text.py` - Conservative transforms
- `aggressive_humanize.py` - Aggressive transforms
- `perplexity_humanize.py` - Perplexity manipulation
- `combined_humanize.py` - Combined approach
- `noise_injection.py` - Noise injection
- `light_humanize.py` - Light transforms
- `final_humanize.py` - Final conservative approach

**Output files**:
- `inflation_final_humanized.md` - Final humanized paper with Appendix D
- `inflation_final_humanized.tex` - LaTeX version
- `inflation_final_humanized.pdf` - 32-page PDF

**Intermediate versions** (for reference):
- `inflation_combined_v1.md` - 88.2% score but garbled text
- `inflation_noise_v1.md` - Noise injection result
- Various other intermediate versions

### 7. Appendix D Added

Added new appendix section to the paper documenting:
- Motivation for experiments
- Detection systems tested
- Baseline results
- Humanization approaches and results
- Control experiments on human text
- Analysis and conclusions
- Tools and replication information

## Commands to Reproduce

```bash
# Activate environment
source ai_detect_env/bin/activate

# Run detection on a file
python ai_detector.py inflation_analysis.md

# Apply final humanization
python final_humanize.py inflation_analysis.md -o output.md

# Generate PDF
pandoc inflation_final_humanized.md -o inflation_final_humanized.tex
pdflatex inflation_final_humanized.tex
```

## Summary Table

| Metric | Value |
|--------|-------|
| Original RoBERTa score | 93.1% |
| Best score achieved | 88.2% |
| Final clean version score | 93.6% |
| Human academic text scores | 74-99% |
| Binoculars score (original) | ~5% AI |

## Conclusion

The RoBERTa detector appears miscalibrated for modern AI output and academic writing. The 88-93% scores for this paper are competitive with scores for clearly human-written formal text. We prioritized readability over detection scores and documented all experiments transparently in Appendix D.

---

*To resume this work, activate the `ai_detect_env` virtual environment and use the scripts in this directory.*
