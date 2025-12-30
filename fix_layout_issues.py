#!/usr/bin/env python3
"""
Fix layout issues:
1. Add samepage environment around short tables to prevent page breaks
2. Update appendix figure/table lists to use proper references
"""

import re
from pathlib import Path

tex = Path('inflation_final_humanized.tex').read_text()

# =============================================================================
# 1. Add needspace package to prevent tables from breaking
# =============================================================================
if '\\usepackage{needspace}' not in tex:
    tex = tex.replace(
        '\\usepackage{booktabs}',
        '\\usepackage{booktabs}\\usepackage{needspace}'
    )
    print("Added needspace package")

# =============================================================================
# 2. Add \needspace before each longtable to keep short tables together
# Tables are identified by their labels
# =============================================================================

# Pattern to find longtable blocks and add needspace before them
# We'll add \needspace{3in} before tables that are short (less than ~10 rows)

short_table_labels = [
    'tab:methodology-changes',
    'tab:income-quintile',
    'tab:race-ethnicity',
    'tab:regional-variation',
    'tab:time-cost',
    'tab:asset-adjusted',
    'tab:first-time-buyer',
    'tab:maria-findings',
    'tab:argentina'
]

# Add needspace before longtables
# Pattern: \begin{longtable}
tex = re.sub(
    r'(\n)(\\begin\{longtable\})',
    r'\1\\needspace{3in}\n\2',
    tex
)
print("Added needspace before longtables")

# =============================================================================
# 3. Update appendix figure list to use references
# =============================================================================

# First, let's find the appendix figure list section
figure_list_old = '''\\begin{itemize}
\\tightlist
\\item
  Figure 1: Truflation vs.~Official CPI Comparison (2021-2025)
\\item
  Figure 2: Inflation Disparities by Race/Ethnicity
\\item
  Figure 3: Regional CPI Variation (November 2025)
\\item
  Figure 4: Spending Composition by Income Quintile
\\item
  Figure 5: Regional CPI Variation (November 2025)
\\item
  Figure 6: Necessity vs.~Discretionary Inflation (2000-2024)
\\item
  Figure 7: Argentina Case Study (2007-2015)
\\item
  Figure 8: Novel Metrics Framework'''

# Check if this pattern exists
if 'Figure 1: Truflation' in tex:
    # Get the figure labels from the document
    figure_labels = re.findall(r'\\label\{(fig:[^}]+)\}', tex)
    print(f"Found figure labels: {figure_labels}")

# =============================================================================
# 4. Update table list to include all tables with refs
# =============================================================================

# Find table labels
table_labels = re.findall(r'\\label\{(tab:[^}]+)\}', tex)
print(f"Found table labels: {table_labels}")

# =============================================================================
# Write output
# =============================================================================
Path('inflation_final_humanized.tex').write_text(tex)
print("\nLayout fixes applied!")
