#!/usr/bin/env python3
"""
Final fixes for document structure:
1. Fix malformed labels
2. Remove remaining manual section numbers
3. Convert remaining subsubsections to subsections
4. Fix all section labels
"""

import re
from pathlib import Path

tex = Path('inflation_final_humanized.tex').read_text()

# Fix malformed labels like \section{Title\label{name} -> \section{Title}\label{sec:name}
def fix_malformed_label(match):
    sec_type = match.group(1)  # section, subsection, subsubsection
    title = match.group(2)
    old_label = match.group(3)

    # Create new label
    new_label = 'sec:' + old_label.replace('-', '-')[:20]

    return f'\\{sec_type}{{{title}}}\\label{{{new_label}}}'

# Pattern for malformed labels
tex = re.sub(r'\\(section|subsection|subsubsection)\{([^\\]+)\\label\{([^}]+)\}',
             fix_malformed_label, tex)

print("Fixed malformed labels")

# Remove remaining manual numbers from section titles
# Pattern: \section{N. Title} -> \section{Title}
tex = re.sub(r'\\section\{(\d+)\.\s*', r'\\section{', tex)
tex = re.sub(r'\\subsection\{(\d+)\.(\d+)\s*', r'\\subsection{', tex)
tex = re.sub(r'\\subsubsection\{(\d+)\.(\d+)\s*', r'\\subsection{', tex)

print("Removed manual section numbers")

# Convert subsubsections to subsections for better structure
tex = tex.replace('\\subsubsection{', '\\subsection{')

print("Converted subsubsections to subsections")

# Fix specific section labels to use sec: prefix
label_fixes = [
    ('\\label{introduction}', '\\label{sec:intro}'),
    ('\\label{related-work}', '\\label{sec:related}'),
    ('\\label{official-inflation}', '\\label{sec:official}'),
    ('\\label{alternative-inflation-measures}', '\\label{sec:alternatives}'),
    ('\\label{distributional-analysis}', '\\label{sec:distributional}'),
    ('\\label{novel-metrics}', '\\label{sec:novel}'),
    ('\\label{case-study}', '\\label{sec:argentina}'),
    ('\\label{machine-intelligence}', '\\label{sec:machine}'),
    ('\\label{conclusion}', '\\label{sec:conclusion}'),
    ('\\label{references}', '\\label{sec:references}'),
    ('\\label{truflation}', '\\label{sec:truflation}'),
    ('\\label{marias-question}', '\\label{sec:maria}'),
    ('\\label{geographic-variation}', '\\label{sec:geographic}'),
    ('\\label{cpi-methodology-and-bias}', '\\label{sec:cpi-bias}'),
    ('\\label{alternative-inflation-meas}', '\\label{sec:alt-measures}'),
    ('\\label{distributional-effects-of}', '\\label{sec:dist-effects}'),
    ('\\label{information-asymmetry-and}', '\\label{sec:info-asymmetry}'),
    ('\\label{consumer-price-index-cons}', '\\label{sec:cpi-construction}'),
    ('\\label{key-methodological-compon}', '\\label{sec:methodology-components}'),
    ('\\label{cumulative-effect-of-meth}', '\\label{sec:cumulative-effect}'),
]

for old, new in label_fixes:
    tex = tex.replace(old, new)

print("Fixed section labels")

# Update cross-references to use new labels
ref_fixes = [
    ('\\ref{related-work}', '\\ref{sec:related}'),
    ('\\ref{official-inflation-methodology}', '\\ref{sec:official}'),
    ('\\ref{alternative-inflation-measures-1}', '\\ref{sec:alternatives}'),
    ('\\ref{distributional-analysis}', '\\ref{sec:distributional}'),
    ('\\ref{novel-metrics-a-demonstration}', '\\ref{sec:novel}'),
    ('\\ref{case-study-argentina-2007-2015}', '\\ref{sec:argentina}'),
    ('\\ref{machine-intelligence-and-the-democratization-of-measurement}', '\\ref{sec:machine}'),
    ('\\ref{conclusion}', '\\ref{sec:conclusion}'),
    ('\\ref{introduction}', '\\ref{sec:intro}'),
]

for old, new in ref_fixes:
    tex = tex.replace(old, new)

print("Fixed cross-references")

# Make sure Keywords and JEL are inside abstract or after it properly
# (Should already be outside abstract from previous fix)

# Write output
Path('inflation_final_humanized.tex').write_text(tex)
print("\nFinal fixes applied!")
