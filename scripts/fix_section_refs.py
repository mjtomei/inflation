#!/usr/bin/env python3
"""
Fix section references to use actual label names from the document.
"""

import re
from pathlib import Path

tex = Path('inflation_final_humanized.tex').read_text()

# Map my attempted refs to actual labels in document
ref_fixes = [
    ('\\ref{sec:related}', '\\ref{related-work}'),
    ('\\ref{sec:official-methodology}', '\\ref{official-inflation-methodology}'),
    ('\\ref{sec:alternatives}', '\\ref{alternative-inflation-measures-1}'),
    ('\\ref{sec:distributional-analysis}', '\\ref{distributional-analysis}'),
    ('\\ref{sec:novel-metrics}', '\\ref{novel-metrics-a-demonstration}'),
    ('\\ref{sec:argentina}', '\\ref{argentina-case-study}'),
    ('\\ref{sec:machine-intel}', '\\ref{machine-intelligence-and-epistemic-democratization}'),
    ('\\ref{sec:conclusion}', '\\ref{conclusion}'),
    ('\\ref{sec:intro}', '\\ref{introduction}'),
]

for old, new in ref_fixes:
    tex = tex.replace(old, new)

# Also need to check for section numbers like "4.3" references
# These are subsections that need proper labels
# Let's just fix these to be text for now or find the right labels

# Fix any remaining broken refs
tex = tex.replace('Section~\\ref{sec:alternatives}.3', 'Section~4.3')
tex = tex.replace('Section~\\ref{sec:machine-intel}.6', 'Section~8.6')
tex = tex.replace('Section~\\ref{sec:distributional-analysis}.1', 'Section~5.1')
tex = tex.replace('Section~\\ref{sec:argentina}.5', 'Section~7.5')

# Fix the broken refs I introduced
tex = tex.replace('Section~\\ref{alternative-inflation-measures-1}.3', 'Section~4.3')
tex = tex.replace('Section~\\ref{machine-intelligence-and-epistemic-democratization}.6', 'Section~8.6')
tex = tex.replace('Section~\\ref{distributional-analysis}.1', 'Section~5.1')
tex = tex.replace('Section~\\ref{argentina-case-study}.5', 'Section~7.5')

Path('inflation_final_humanized.tex').write_text(tex)
print("Fixed section references")
