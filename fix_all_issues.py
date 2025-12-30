#!/usr/bin/env python3
"""
Comprehensive fix for LaTeX document:
1. Fix table structure (remove nested table/longtable)
2. Fix section labels to match references
3. Remove duplicate labels
4. Remove stray manual section number
"""

import re
from pathlib import Path

tex = Path('inflation_final_humanized.tex').read_text()

# ============================================================================
# 1. Fix section labels to match the short reference names used in text
# ============================================================================

label_renames = [
    # Main sections - change labels to match references
    ('\\label{sec:related-work}', '\\label{sec:related}'),
    ('\\label{sec:official-inflation-m}', '\\label{sec:official}'),
    ('\\label{sec:distributional-analy}', '\\label{sec:distributional}'),
    ('\\label{sec:novel-metrics-a-demo}', '\\label{sec:novel}'),
    ('\\label{sec:case-study-argentina}', '\\label{sec:argentina}'),
    ('\\label{sec:machine-intelligence}', '\\label{sec:machine}'),
]

for old, new in label_renames:
    tex = tex.replace(old, new)

print("Fixed main section labels")

# ============================================================================
# 2. Fix duplicate label: sec:alternative-inflatio appears twice
# First occurrence (line 233) is "Alternative Inflation Measures" subsection under Related Work
# Second occurrence (line 538) is "4. Alternative Inflation Measures" subsection - remove this one
# ============================================================================

# The stray "4. Alternative Inflation Measures" section at line 537-538
# This appears to be a duplicate/leftover from earlier processing
# Let's check and remove it or rename its label

# First rename the duplicate to something unique
tex = tex.replace(
    '\\subsection{4. Alternative Inflation\nMeasures}\\label{sec:alternative-inflatio}',
    ''  # Remove this entirely - it's a duplicate
)

# Also try without newline
tex = tex.replace(
    '\\subsection{4. Alternative Inflation Measures}\\label{sec:alternative-inflatio}',
    ''
)

print("Removed duplicate alternative inflation section")

# ============================================================================
# 3. Fix table structure - remove nested table/longtable
# longtable should NOT be inside table environment
# Convert to just longtable with caption at bottom
# ============================================================================

# Pattern to find table wrapping longtable
# \begin{table}[H]
# \centering
# \small
# \begin{longtable}...
# ...
# \end{longtable}
# \caption{...}
# \label{...}
# \end{table}

def fix_table_structure(match):
    """Convert nested table/longtable to just longtable with caption"""
    content = match.group(0)

    # Extract caption and label
    caption_match = re.search(r'\\caption\{([^}]+)\}', content)
    label_match = re.search(r'\\label\{([^}]+)\}', content)

    caption = caption_match.group(1) if caption_match else ''
    label = label_match.group(1) if label_match else ''

    # Extract longtable content
    lt_match = re.search(r'\\begin\{longtable\}(\[.*?\])?\{([^}]+)\}(.*?)\\end\{longtable\}', content, re.DOTALL)
    if not lt_match:
        return content  # Can't parse, leave as is

    align_opt = lt_match.group(1) or ''
    col_spec = lt_match.group(2)
    lt_content = lt_match.group(3)

    # Build new longtable with caption at end
    new_table = f'''\\begin{{longtable}}{align_opt}{{{col_spec}}}
{lt_content.strip()}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{longtable}}'''

    return new_table

# Match table environments containing longtable
table_pattern = r'\\begin\{table\}\[H\].*?\\begin\{longtable\}.*?\\end\{longtable\}.*?\\end\{table\}'
tex = re.sub(table_pattern, fix_table_structure, tex, flags=re.DOTALL)

print("Fixed table structure (removed nested table/longtable)")

# ============================================================================
# 4. For standalone longtables, add \captionsetup for proper numbering
# ============================================================================

# Add longtable caption setup to preamble if not present
if '\\usepackage{caption}' not in tex:
    # Add after longtable package
    tex = tex.replace(
        '\\usepackage{longtable,booktabs,array}',
        '\\usepackage{longtable,booktabs,array}\n\\usepackage{caption}'
    )
    print("Added caption package")

# ============================================================================
# 5. Reset table/figure counters properly
# ============================================================================

# Make sure counters are reset
if '\\setcounter{table}{0}' not in tex:
    tex = tex.replace(
        '\\begin{document}',
        '\\begin{document}\n\\setcounter{table}{0}\n\\setcounter{figure}{0}'
    )

print("Ensured counter resets")

# ============================================================================
# 6. Clean up any remaining issues
# ============================================================================

# Remove empty lines that might have been left
tex = re.sub(r'\n{4,}', '\n\n\n', tex)

# Fix any remaining malformed labels (label inside section title)
tex = re.sub(r'\\(section|subsection)\{([^\\}]+)\\label\{([^}]+)\}',
             lambda m: f'\\{m.group(1)}{{{m.group(2)}}}\\label{{{m.group(3)}}}',
             tex)

print("Cleaned up formatting")

# ============================================================================
# Write output
# ============================================================================

Path('inflation_final_humanized.tex').write_text(tex)
print("\nAll fixes applied!")
