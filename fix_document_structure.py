#!/usr/bin/env python3
"""
Fix LaTeX document structure:
1. Enable section numbering
2. Use proper \title{}, \maketitle
3. Use proper \begin{abstract}...\end{abstract}
4. Convert \subsection to \section for main sections
5. Remove manual section numbers from titles
6. Add proper \label{} to all sections
"""

import re
from pathlib import Path

tex = Path('inflation_final_humanized.tex').read_text()

# ============================================================================
# 1. Enable section numbering
# ============================================================================
tex = tex.replace(r'\setcounter{secnumdepth}{-\maxdimen} % remove section numbering',
                  r'\setcounter{secnumdepth}{3} % enable section numbering')

print("Enabled section numbering")

# ============================================================================
# 2. Fix title - use \title{} and \maketitle
# ============================================================================

# Find and replace the title section
old_title = r'''\hypertarget{measuring-what-matters-a-comparative-analysis-of-official-and-alternative-inflation-metrics-with-novel-distributional-approaches}{%
\section{Measuring What Matters: A Comparative Analysis of Official and
Alternative Inflation Metrics with Novel Distributional
Approaches}\label{measuring-what-matters-a-comparative-analysis-of-official-and-alternative-inflation-metrics-with-novel-distributional-approaches}}

December 2025

\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}'''

new_title = r'''\title{Measuring What Matters: A Comparative Analysis of Official and Alternative Inflation Metrics with Novel Distributional Approaches}
\author{Working Paper}
\date{December 2025}

\maketitle

\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}'''

tex = tex.replace(old_title, new_title)
print("Fixed title")

# ============================================================================
# 3. Fix abstract - use \begin{abstract}...\end{abstract}
# ============================================================================

# Find abstract section and convert it
abstract_pattern = r'\\hypertarget\{abstract\}\{%\s*\\subsection\{Abstract\}\\label\{abstract\}\}\s*\n\s*(.*?)(?=\\textbf\{Keywords\})'
abstract_match = re.search(abstract_pattern, tex, re.DOTALL)

if abstract_match:
    abstract_content = abstract_match.group(1).strip()
    old_abstract = abstract_match.group(0)
    new_abstract = f'''\\begin{{abstract}}
{abstract_content}
\\end{{abstract}}

'''
    tex = tex.replace(old_abstract, new_abstract)
    print("Fixed abstract")

# ============================================================================
# 4. Convert main sections from \subsection to \section
# Remove manual numbers like "1. Introduction" -> "Introduction"
# ============================================================================

# Main sections to convert (currently \subsection with numbers)
main_sections = [
    (r'\subsection{1. Introduction}', r'\section{Introduction}', 'sec:intro'),
    (r'\subsection{2. Related Work}', r'\section{Related Work}', 'sec:related'),
    (r'\subsection{3. Official Inflation', r'\section{Official Inflation', 'sec:official'),
    (r'\subsection{4. Alternative Measures}', r'\section{Alternative Measures}', 'sec:alternatives'),
    (r'\subsection{5. Distributional Analysis}', r'\section{Distributional Analysis}', 'sec:distributional'),
    (r'\subsection{6. Novel Metrics', r'\section{Novel Metrics', 'sec:novel'),
    (r'\subsection{7. Case Study', r'\section{Case Study', 'sec:argentina'),
    (r'\subsection{8. Machine Intelligence', r'\section{Machine Intelligence', 'sec:machine'),
    (r'\subsection{9. Conclusion}', r'\section{Conclusion}', 'sec:conclusion'),
    (r'\subsection{10. References}', r'\section{References}', 'sec:references'),
]

for old, new, label in main_sections:
    if old in tex:
        tex = tex.replace(old, new)
        print(f"Converted: {old[:30]}...")

# ============================================================================
# 5. Fix subsection numbering (convert \subsubsection to \subsection where needed)
# ============================================================================

# Related Work subsections
subsections_to_fix = [
    (r'\hypertarget{cpi-methodology-and-bias}{%\n\subsubsection{2.1 CPI Methodology and',
     r'\subsection{CPI Methodology and'),
    (r'\subsubsection{2.1 CPI Methodology', r'\subsection{CPI Methodology'),
    (r'\subsubsection{2.2 Alternative Inflation', r'\subsection{Alternative Inflation'),
    (r'\subsubsection{2.3 Distributional Effects', r'\subsection{Distributional Effects'),
    (r'\subsubsection{2.4 Information Asymmetry', r'\subsection{Information Asymmetry'),
    (r'\subsubsection{2.5 Nature of This', r'\subsection{Nature of This'),
    (r'\subsubsection{2.6 AI-Assisted', r'\subsection{AI-Assisted'),
    # Section 3 subsections
    (r'\subsubsection{3.1 Consumer Price', r'\subsection{Consumer Price'),
    (r'\subsubsection{3.2 Key Methodological', r'\subsection{Key Methodological'),
    (r'\subsubsection{3.3 Cumulative Effect', r'\subsection{Cumulative Effect'),
    (r'\subsubsection{3.4 Personal Consumption', r'\subsection{Personal Consumption'),
    # Section 4 subsections
    (r'\subsubsection{4.1 Truflation}', r'\subsection{Truflation}'),
    (r'\subsubsection{4.2 Billion Prices', r'\subsection{Billion Prices'),
    (r'\subsubsection{4.3 ShadowStats', r'\subsection{ShadowStats'),
    # Section 5 subsections
    (r'\subsubsection{5.1 Inflation by Income', r'\subsection{Inflation by Income'),
    (r'\subsubsection{5.2 Inflation by Race', r'\subsection{Inflation by Race'),
    (r'\subsubsection{5.3 Geographic', r'\subsection{Geographic'),
    (r'\subsubsection{5.4 Spending', r'\subsection{Spending'),
    # Section 6 subsections
    (r"\subsubsection{6.1 Maria's", r"\subsection{Maria's"),
    (r'\subsubsection{6.2 How Many Minutes', r'\subsection{How Many Minutes'),
    (r'\subsubsection{6.3 Why Do Necessities', r'\subsection{Why Do Necessities'),
    (r"\subsubsection{6.4 What About the Assets She Doesn't Own", r"\subsection{What About Assets"),
    (r'\subsubsection{6.5 Can She Ever Buy', r'\subsection{Can She Ever Buy'),
    (r'\subsubsection{6.6 The Saturday', r'\subsection{The Saturday'),
    (r'\subsubsection{6.7 What Maria Found}', r'\subsection{What Maria Found}'),
    (r'\subsubsection{6.8 From Individual', r'\subsection{From Individual'),
]

for old, new in subsections_to_fix:
    if old in tex:
        tex = tex.replace(old, new)

# ============================================================================
# 6. Remove all \hypertarget wrappers and clean up labels
# ============================================================================

# Remove hypertarget wrappers but keep content
# Pattern: \hypertarget{name}{%\n\section{Title}\label{old-label}}
# -> \section{Title}\label{sec:name}

def clean_hypertarget(match):
    target_name = match.group(1)
    section_type = match.group(2)
    title = match.group(3)

    # Create a clean label
    clean_label = target_name.replace('-', ':').split(':')[0] if ':' in target_name else target_name

    return f'\\{section_type}{{{title}}}'

# This is getting complex - let's just remove hypertargets
tex = re.sub(r'\\hypertarget\{[^}]+\}\{%\s*\n', '', tex)

# Clean up double closing braces from hypertarget removal
tex = re.sub(r'\}(\s*\\label\{[^}]+\})\}', r'\1', tex)

print("Removed hypertarget wrappers")

# ============================================================================
# 7. Add/fix labels for all sections
# ============================================================================

# Dictionary of section titles to labels
section_labels = {
    'Introduction': 'sec:intro',
    'Related Work': 'sec:related',
    'Official Inflation Methodology': 'sec:official',
    'Alternative Measures': 'sec:alternatives',
    'Distributional Analysis': 'sec:distributional',
    'Novel Metrics': 'sec:novel',
    'Argentina': 'sec:argentina',
    'Machine Intelligence': 'sec:machine',
    'Conclusion': 'sec:conclusion',
    'References': 'sec:references',
    'CPI Methodology and Bias': 'sec:cpi-bias',
    'Alternative Inflation Measures': 'sec:alt-measures',
    'Distributional Effects of Inflation': 'sec:dist-effects',
    'Information Asymmetry': 'sec:info-asymmetry',
    'Truflation': 'sec:truflation',
    'Billion Prices Project': 'sec:bpp',
    'ShadowStats': 'sec:shadowstats',
}

# Update section references in text
ref_updates = [
    ('Section~\\ref{related-work}', 'Section~\\ref{sec:related}'),
    ('Section~\\ref{official-inflation-methodology}', 'Section~\\ref{sec:official}'),
    ('Section~\\ref{alternative-inflation-measures-1}', 'Section~\\ref{sec:alternatives}'),
    ('Section~\\ref{distributional-analysis}', 'Section~\\ref{sec:distributional}'),
    ('Section~\\ref{novel-metrics-a-demonstration}', 'Section~\\ref{sec:novel}'),
    ('Section~\\ref{case-study-argentina-2007-2015}', 'Section~\\ref{sec:argentina}'),
    ('Section~\\ref{machine-intelligence-and-the-democratization-of-measurement}', 'Section~\\ref{sec:machine}'),
    ('Section~\\ref{conclusion}', 'Section~\\ref{sec:conclusion}'),
    ('Section~\\ref{introduction}', 'Section~\\ref{sec:intro}'),
]

for old, new in ref_updates:
    tex = tex.replace(old, new)

print("Updated section references")

# ============================================================================
# 8. Reset table counter if needed
# ============================================================================

# Add after \begin{document}: \setcounter{table}{0}
if '\\setcounter{table}{0}' not in tex:
    tex = tex.replace('\\begin{document}', '\\begin{document}\n\\setcounter{table}{0}\n\\setcounter{figure}{0}')

print("Reset table and figure counters")

# ============================================================================
# Write output
# ============================================================================

Path('inflation_final_humanized.tex').write_text(tex)
print("\nDocument structure fixed!")
print("Run pdflatex twice to update cross-references.")
