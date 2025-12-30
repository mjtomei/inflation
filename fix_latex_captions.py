#!/usr/bin/env python3
"""
Fix LaTeX figure and table captions:
1. Combine duplicate figure captions (keep descriptive one inside figure env)
2. Move table captions underneath tables with proper \caption{}
3. Add list of tables to appendix
"""

import re
from pathlib import Path

tex = Path('inflation_final_humanized.tex').read_text()

# ============================================================================
# FIX FIGURES: Remove short caption, keep only the descriptive \emph paragraph
# Convert \emph{Figure X: description} to proper \caption{description}
# ============================================================================

# Pattern: \begin{figure} ... \caption{Figure X: short} ... \end{figure}
# followed by \emph{Figure X: long description}

def fix_figure(match):
    """Fix a figure block by using the descriptive caption."""
    full_block = match.group(0)

    # Extract figure number from the short caption
    short_caption_match = re.search(r'\\caption\{Figure (\d+):', full_block)
    if not short_caption_match:
        return full_block

    fig_num = short_caption_match.group(1)

    # Find the includegraphics line
    img_match = re.search(r'\\includegraphics(\[.*?\])?\{(.*?)\}', full_block)
    if not img_match:
        return full_block

    img_opts = img_match.group(1) or ''
    img_path = img_match.group(2)

    # Find the descriptive caption in the \emph after the figure
    emph_pattern = rf'\\end{{figure}}\s*\\emph{{Figure {fig_num}: (.*?)}}'
    emph_match = re.search(emph_pattern, full_block, re.DOTALL)

    if emph_match:
        description = emph_match.group(1).strip()
        # Clean up the description
        description = description.replace('\n', ' ').strip()
        # Remove trailing period for caption, it will be added if needed
        if description.endswith('.'):
            description = description[:-1]

        # Build new figure block
        new_block = f'''\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.9\\textwidth]{{{img_path}}}
\\caption{{{description}.}}
\\label{{fig:{fig_num}}}
\\end{{figure}}

'''
        return new_block

    return full_block

# Find figure blocks followed by \emph{Figure descriptions
figure_pattern = r'\\begin\{figure\}.*?\\end\{figure\}\s*\\emph\{Figure \d+:.*?\}'
tex = re.sub(figure_pattern, fix_figure, tex, flags=re.DOTALL)

# ============================================================================
# FIX TABLES: Move \textbf{Table X:} to proper \caption underneath table
# ============================================================================

def fix_table(match):
    """Fix a table block by moving caption underneath."""
    prefix = match.group(1)  # \textbf{Table X: title}
    table_content = match.group(2)  # longtable content

    # Extract table title
    title_match = re.search(r'\\textbf\{Table (\d+): (.*?)\}', prefix)
    if not title_match:
        return match.group(0)

    table_num = title_match.group(1)
    table_title = title_match.group(2).strip()

    # Build the table with caption at the end
    # We need to modify longtable to use regular table for caption support
    # Or add caption inside longtable

    # For longtable, caption goes at the beginning or end
    # Let's put it at the end

    # Find the \end{longtable}
    new_table = f'''\\begin{{table}}[H]
\\centering
{table_content.strip()}
\\caption{{{table_title}}}
\\label{{tab:{table_num}}}
\\end{{table}}

'''
    return new_table

# Pattern for tables: \textbf{Table X: title} followed by longtable
# This is tricky because longtable is not inside a table environment

# Let's do a different approach - find each table pattern and fix it
table_sections = []

# Find all table headers
table_header_pattern = r'\\textbf\{Table (\d+): ([^}]+)\}\s*\n\s*\\begin\{longtable\}'
for match in re.finditer(table_header_pattern, tex):
    table_sections.append({
        'start': match.start(),
        'header_end': match.end(),
        'num': match.group(1),
        'title': match.group(2)
    })

# Process tables in reverse order to preserve positions
for table_info in reversed(table_sections):
    # Find the end of this longtable
    start_pos = table_info['header_end']
    end_match = re.search(r'\\end\{longtable\}', tex[start_pos:])
    if end_match:
        end_pos = start_pos + end_match.end()

        # Extract the longtable content (without \begin and \end)
        longtable_start = tex.find('\\begin{longtable}', table_info['start'])
        longtable_content = tex[longtable_start:end_pos]

        # Create new table with caption at bottom
        new_table = f'''\\begin{{table}}[H]
\\centering
\\small
{longtable_content}
\\caption{{{table_info['title']}}}
\\label{{tab:{table_info['num']}}}
\\end{{table}}
'''
        # Replace the old content
        old_start = table_info['start']
        tex = tex[:old_start] + new_table + tex[end_pos:]

# ============================================================================
# Clean up any remaining duplicate figure descriptions
# ============================================================================

# Remove standalone \emph{Figure X: ...} paragraphs that are now orphaned
orphan_emph_pattern = r'\n\s*\\emph\{Figure \d+: [^}]+\}\s*\n'
tex = re.sub(orphan_emph_pattern, '\n\n', tex)

# ============================================================================
# ADD LIST OF TABLES TO APPENDIX
# ============================================================================

# Find where to insert list of tables (after Figure List in appendix)
figure_list_pattern = r'(\\subsection\{Appendix B: Figure List\}.*?)(\\subsection\{Appendix C:)'
match = re.search(figure_list_pattern, tex, re.DOTALL)

if match:
    figure_list_section = match.group(1)
    next_section = match.group(2)

    # Create table list
    table_list = '''

\\subsection{Appendix B.2: Table List}\\label{appendix-b2-table-list}

\\begin{itemize}
\\tightlist
\\item Table 1: CPI Methodology Changes Since 1980
\\item Table 2: Cumulative Inflation by Income Quintile (2005-2023)
\\item Table 3: Peak Inflation Gap by Race/Ethnicity (2021-2022)
\\item Table 4: Regional CPI Variation (November 2025)
\\item Table 5: Argentina Official vs.~Independent Inflation
\\item Table 6: Time-Cost Index (Minutes of Work to Purchase)
\\item Table 7: CPI vs.~Asset-Adjusted Index (2000 = 100)
\\item Table 8: First-Time Buyer Affordability
\\item Table 9: Maria's Findings Summary
\\item Table 10: Data Sources for Novel Metrics
\\item Table 11: AI Detection Control Experiments
\\end{itemize}

'''
    tex = tex.replace(figure_list_section + next_section,
                     figure_list_section + table_list + next_section)

# ============================================================================
# Fix any remaining issues
# ============================================================================

# Ensure [H] placement for figures
tex = re.sub(r'\\begin\{figure\}\s*\n', '\\begin{figure}[H]\n', tex)
tex = re.sub(r'\\begin\{figure\}\[htbp\]', '\\begin{figure}[H]', tex)

# Make sure float package is loaded for [H]
if '\\usepackage{float}' not in tex:
    tex = tex.replace('\\usepackage{graphicx}', '\\usepackage{graphicx}\n\\usepackage{float}')

# Write output
Path('inflation_final_humanized.tex').write_text(tex)
print("Fixed LaTeX file written.")
