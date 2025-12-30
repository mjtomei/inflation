#!/usr/bin/env python3
"""Add figure numbers to captions."""

import re
from pathlib import Path

tex = Path('inflation_final_humanized.tex').read_text()

lines = tex.split('\n')
new_lines = []
current_fig_num = None

for i, line in enumerate(lines):
    # Track figure labels
    label_match = re.search(r'\\label\{fig:(\d+)\}', line)
    if label_match:
        current_fig_num = label_match.group(1)

    # Fix caption if needed - check previous lines for label
    if '\\caption{' in line and current_fig_num is None:
        # Look back for label
        for j in range(max(0, i-5), i):
            lm = re.search(r'\\label\{fig:(\d+)\}', new_lines[j] if j < len(new_lines) else lines[j])
            if lm:
                current_fig_num = lm.group(1)
                break

    if '\\caption{' in line and current_fig_num:
        caption_match = re.search(r'\\caption\{(.+)\}$', line)
        if caption_match:
            caption_text = caption_match.group(1)
            if not caption_text.startswith('Figure'):
                new_caption = f'Figure {current_fig_num}: {caption_text}'
                line = line.replace(f'\\caption{{{caption_text}}}', f'\\caption{{{new_caption}}}')

    # Reset on figure end
    if '\\end{figure}' in line:
        current_fig_num = None

    new_lines.append(line)

tex = '\n'.join(new_lines)
Path('inflation_final_humanized.tex').write_text(tex)
print('Figure numbers added to captions')
