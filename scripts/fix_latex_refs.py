#!/usr/bin/env python3
"""
Fix LaTeX cross-references:
1. Remove "Figure X:" and "Table X:" prefixes from captions
2. Change labels to descriptive names
3. Add labels to sections
4. Replace text references with \ref{} commands
"""

import re
from pathlib import Path

tex = Path('inflation_final_humanized.tex').read_text()

# ============================================================================
# MAPPING: Old labels to new descriptive labels
# ============================================================================

FIGURE_LABELS = {
    'fig:3': 'fig:truflation',
    'fig:4': 'fig:race-disparity',
    'fig:5': 'fig:regional',
    'fig:6': 'fig:spending-composition',
    'fig:7': 'fig:argentina',
    'fig:8': 'fig:metrics-framework',
    'fig:9': 'fig:time-cost',
    'fig:10': 'fig:necessity-discretionary',
    'fig:11': 'fig:asset-adjusted',
    'fig:12': 'fig:housing-affordability',
    'fig:13': 'fig:grocery-basket',
}

TABLE_LABELS = {
    'tab:1': 'tab:methodology-changes',
    'tab:2': 'tab:income-quintile',
    'tab:3': 'tab:race-gap',
    'tab:4': 'tab:regional-cpi',
    'tab:5': 'tab:argentina',
    'tab:6': 'tab:time-cost',
    'tab:7': 'tab:asset-adjusted',
    'tab:8': 'tab:housing-affordability',
}

# ============================================================================
# 1. Remove "Figure X:" and "Table X:" prefixes from captions
# ============================================================================

# Remove "Figure X: " prefix from captions
tex = re.sub(r'\\caption\{Figure \d+: ', r'\\caption{', tex)

# Remove "Table X: " prefix from captions
tex = re.sub(r'\\caption\{Table \d+: ', r'\\caption{', tex)

print("Removed Figure/Table prefixes from captions")

# ============================================================================
# 2. Replace old labels with descriptive labels
# ============================================================================

for old, new in FIGURE_LABELS.items():
    tex = tex.replace(f'\\label{{{old}}}', f'\\label{{{new}}}')
    tex = tex.replace(f'\\ref{{{old}}}', f'\\ref{{{new}}}')

for old, new in TABLE_LABELS.items():
    tex = tex.replace(f'\\label{{{old}}}', f'\\label{{{new}}}')
    tex = tex.replace(f'\\ref{{{old}}}', f'\\ref{{{new}}}')

print("Updated figure and table labels to descriptive names")

# ============================================================================
# 3. Add section labels - using simple string replacement
# ============================================================================

section_additions = [
    ('\\section{Introduction}\\label{introduction}', '\\section{Introduction}\\label{sec:intro}'),
    ('\\subsection{CPI Methodology and Bias}\\label{cpi-methodology-and-bias}', '\\subsection{CPI Methodology and Bias}\\label{sec:cpi-methodology}'),
    ('\\subsection{Alternative Inflation Measures}\\label{alternative-inflation-measures}', '\\subsection{Alternative Inflation Measures}\\label{sec:alt-measures}'),
    ('\\subsection{Distributional Effects of Inflation}\\label{distributional-effects-of-inflation}', '\\subsection{Distributional Effects of Inflation}\\label{sec:distributional}'),
    ('\\subsection{Information Asymmetry and Epistemic Authority}\\label{information-asymmetry-and-epistemic-authority}', '\\subsection{Information Asymmetry and Epistemic Authority}\\label{sec:info-asymmetry}'),
    ('\\section{Official Inflation Methodology}\\label{official-inflation-methodology}', '\\section{Official Inflation Methodology}\\label{sec:official-methodology}'),
    ('\\section{Alternative Measures}\\label{alternative-measures}', '\\section{Alternative Measures}\\label{sec:alternatives}'),
    ('\\section{Distributional Analysis}\\label{distributional-analysis}', '\\section{Distributional Analysis}\\label{sec:distributional-analysis}'),
    ('\\section{Novel Metrics}\\label{novel-metrics}', '\\section{Novel Metrics}\\label{sec:novel-metrics}'),
    ('\\section{Argentina Case Study}\\label{argentina-case-study}', '\\section{Argentina Case Study}\\label{sec:argentina}'),
    ('\\section{Machine Intelligence and Epistemic Democratization}\\label{machine-intelligence-and-epistemic-democratization}', '\\section{Machine Intelligence and Epistemic Democratization}\\label{sec:machine-intel}'),
    ('\\section{Conclusion}\\label{conclusion}', '\\section{Conclusion}\\label{sec:conclusion}'),
    ('\\section{References}\\label{references}', '\\section{References}\\label{sec:references}'),
    ('\\section{Related Work}\\label{related-work}', '\\section{Related Work}\\label{sec:related}'),
]

for old, new in section_additions:
    tex = tex.replace(old, new)

print("Updated section labels")

# ============================================================================
# 4. Replace text references with \ref{} commands
# ============================================================================

# Figure references - be careful not to replace inside captions
figure_text_refs = [
    ('Figure 3', 'Figure~\\ref{fig:truflation}'),
    ('Figure 4', 'Figure~\\ref{fig:race-disparity}'),
    ('Figure 5', 'Figure~\\ref{fig:regional}'),
    ('Figure 6', 'Figure~\\ref{fig:spending-composition}'),
    ('Figure 7', 'Figure~\\ref{fig:argentina}'),
    ('Figure 8', 'Figure~\\ref{fig:metrics-framework}'),
    ('Figure 9', 'Figure~\\ref{fig:time-cost}'),
    ('Figure 10', 'Figure~\\ref{fig:necessity-discretionary}'),
    ('Figure 11', 'Figure~\\ref{fig:asset-adjusted}'),
    ('Figure 12', 'Figure~\\ref{fig:housing-affordability}'),
    ('Figure 13', 'Figure~\\ref{fig:grocery-basket}'),
]

# Table references
table_text_refs = [
    ('Table 1 ', 'Table~\\ref{tab:methodology-changes} '),
    ('Table 2 ', 'Table~\\ref{tab:income-quintile} '),
    ('Table 3 ', 'Table~\\ref{tab:race-gap} '),
    ('Table 4 ', 'Table~\\ref{tab:regional-cpi} '),
    ('Table 5 ', 'Table~\\ref{tab:argentina} '),
    ('Table 6 ', 'Table~\\ref{tab:time-cost} '),
    ('Table 6)', 'Table~\\ref{tab:time-cost})'),
    ('Table 7 ', 'Table~\\ref{tab:asset-adjusted} '),
    ('Table 7)', 'Table~\\ref{tab:asset-adjusted})'),
    ('Table 8 ', 'Table~\\ref{tab:housing-affordability} '),
    ('Table 8)', 'Table~\\ref{tab:housing-affordability})'),
]

# Section references
section_text_refs = [
    ('Section 2', 'Section~\\ref{sec:related}'),
    ('Section 3', 'Section~\\ref{sec:official-methodology}'),
    ('Section 4', 'Section~\\ref{sec:alternatives}'),
    ('Section 5', 'Section~\\ref{sec:distributional-analysis}'),
    ('Section 6', 'Section~\\ref{sec:novel-metrics}'),
    ('Section 7', 'Section~\\ref{sec:argentina}'),
    ('Section 8', 'Section~\\ref{sec:machine-intel}'),
    ('Section 9', 'Section~\\ref{sec:conclusion}'),
    ('section 3', 'Section~\\ref{sec:official-methodology}'),
    ('section 4', 'Section~\\ref{sec:alternatives}'),
    ('section 5', 'Section~\\ref{sec:distributional-analysis}'),
    ('section 6', 'Section~\\ref{sec:novel-metrics}'),
    ('section 8.6', 'Section~\\ref{sec:machine-intel}'),
]

# Apply replacements (avoiding caption/label contexts)
# First, let's identify and protect caption contents
# Simple approach: just do the replacements

for old, new in figure_text_refs:
    # Don't replace if it's in a caption (figures in appendix list)
    # Pattern: replace only when not preceded by "item "
    if '\\item ' + old not in tex:
        tex = tex.replace(old, new)
    else:
        # Replace only non-list occurrences
        lines = tex.split('\n')
        new_lines = []
        for line in lines:
            if '\\item' in line and old in line:
                new_lines.append(line)  # Keep as-is in lists
            else:
                new_lines.append(line.replace(old, new))
        tex = '\n'.join(new_lines)

for old, new in table_text_refs:
    if '\\item ' + old.strip() not in tex:
        tex = tex.replace(old, new)
    else:
        lines = tex.split('\n')
        new_lines = []
        for line in lines:
            if '\\item' in line and old.strip() in line:
                new_lines.append(line)
            else:
                new_lines.append(line.replace(old, new))
        tex = '\n'.join(new_lines)

for old, new in section_text_refs:
    tex = tex.replace(old, new)

print("Replaced text references with cross-references")

# ============================================================================
# 5. Clean up duplicate refs in appendix lists
# ============================================================================

# The appendix figure/table lists should keep simple text, not refs
# Let's fix them back
appendix_start = tex.find('Appendix B: Figure List')
if appendix_start > 0:
    before_appendix = tex[:appendix_start]
    after_appendix = tex[appendix_start:]

    # In the appendix lists, replace refs back to plain text
    for old, new in figure_text_refs:
        after_appendix = after_appendix.replace(new, old)
    for old, new in table_text_refs:
        after_appendix = after_appendix.replace(new, old.strip())

    tex = before_appendix + after_appendix

print("Fixed appendix lists")

# Write output
Path('inflation_final_humanized.tex').write_text(tex)
print("\nLaTeX file updated successfully!")
print("Run pdflatex twice to update cross-references.")
