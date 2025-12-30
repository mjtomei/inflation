# Inflation Measurement Analysis

An analysis of CPI methodology limitations and alternative inflation metrics, examining how official statistics may not reflect lived economic experiences across different demographic groups.

## Main Output

- **`inflation_final_humanized.pdf`** - Final paper (34 pages)
- **`inflation_final_humanized.tex`** - LaTeX source
- **`references.bib`** - BibTeX bibliography with 50+ cited sources

## Key Topics Covered

- CPI methodology changes since 1980 (hedonic adjustment, geometric weighting, owner's equivalent rent)
- Distributional effects by income quintile, race/ethnicity, and region
- Alternative metrics: Time-Cost Index, Necessity-Weighted CPI, Asset-Adjusted Index
- Real-time inflation data (Truflation) vs official statistics
- Case study: Argentina's inflation measurement controversy (2007-2015)
- Epistemic implications of measurement methodology choices

## Project Structure

```
├── inflation_final_humanized.tex   # Main LaTeX document
├── inflation_final_humanized.pdf   # Compiled paper
├── references.bib                  # Bibliography
├── figures/                        # Generated figures (PNG)
├── scripts/                        # Python scripts
│   ├── generate_figures.py         # Figure generation
│   ├── convert_citations.py        # Citation processing
│   └── ...                         # Various processing scripts
├── drafts/                         # Intermediate document versions
├── reviews/                        # Peer review materials
└── output/                         # Build artifacts and logs
```

## Building

### Regenerate figures

```bash
python3 -m venv venv
source venv/bin/activate
pip install matplotlib numpy
python3 scripts/generate_figures.py
```

### Compile PDF

```bash
pdflatex inflation_final_humanized.tex
bibtex inflation_final_humanized
pdflatex inflation_final_humanized.tex
pdflatex inflation_final_humanized.tex
```

## JEL Classification

E31, E01, D31, C43, D83
