#!/usr/bin/env python3
"""
Generate PDF from markdown report using WeasyPrint.
Creates a professional academic-style document.
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path
import re

# Read the markdown file
md_path = Path("inflation_analysis.md")
md_content = md_path.read_text()

# Remove JEL classification and keywords lines (per user request)
md_content = re.sub(r'\*\*Keywords\*\*:.*?\n', '', md_content)
md_content = re.sub(r'\*\*JEL Classification\*\*:.*?\n', '', md_content)

# Convert markdown to HTML
md_extensions = ['tables', 'fenced_code', 'toc']
html_body = markdown.markdown(md_content, extensions=md_extensions)

# Fix image paths to be absolute
html_body = html_body.replace('src="figures/', f'src="{Path.cwd()}/figures/')

# Professional academic CSS styling - LaTeX-inspired
css_style = """
@page {
    size: letter;
    margin: 1in;
    @top-center {
        content: "Measuring What Matters";
        font-size: 9pt;
        color: #666;
        font-family: 'Times New Roman', Times, serif;
    }
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        font-family: 'Times New Roman', Times, serif;
    }
}

@page :first {
    @top-center { content: none; }
}

body {
    font-family: 'Times New Roman', Times, Georgia, serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #000;
    text-align: justify;
    hyphens: auto;
}

h1 {
    font-size: 16pt;
    font-weight: bold;
    text-align: center;
    margin-top: 0;
    margin-bottom: 1em;
    line-height: 1.3;
    page-break-after: avoid;
}

h2 {
    font-size: 12pt;
    font-weight: bold;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
    text-align: left;
}

h3 {
    font-size: 11pt;
    font-weight: bold;
    font-style: italic;
    margin-top: 1em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
    text-align: left;
}

p {
    margin-top: 0;
    margin-bottom: 0.8em;
    text-align: justify;
    orphans: 2;
    widows: 2;
}

blockquote {
    margin: 1em 2em;
    font-style: italic;
}

/* Tables - LaTeX booktabs style */
table {
    border-collapse: collapse;
    margin: 1em auto;
    font-size: 10pt;
    page-break-inside: avoid;
    width: auto;
}

th, td {
    padding: 4px 10px;
    text-align: left;
    border: none;
    vertical-align: top;
}

thead tr {
    border-top: 2px solid #000;
    border-bottom: 1px solid #000;
}

tbody tr:last-child {
    border-bottom: 2px solid #000;
}

th {
    font-weight: bold;
}

/* Caption for tables */
table + p em:only-child,
p em:only-child {
    display: block;
    text-align: left;
    font-size: 10pt;
    font-style: italic;
    margin: 0.5em 0 1em 0;
}

/* Lists - compact */
ul, ol {
    margin: 0.5em 0;
    padding-left: 1.5em;
}

li {
    margin-bottom: 0.2em;
    text-align: justify;
}

/* Nested lists */
li > ul, li > ol {
    margin-top: 0.2em;
    margin-bottom: 0.2em;
}

/* Images/Figures */
img {
    max-width: 90%;
    height: auto;
    display: block;
    margin: 1em auto;
    page-break-inside: avoid;
}

/* Strong and emphasis */
strong {
    font-weight: bold;
}

em {
    font-style: italic;
}

/* Code */
code {
    font-family: 'Courier New', Courier, monospace;
    font-size: 9pt;
}

pre {
    font-family: 'Courier New', Courier, monospace;
    font-size: 9pt;
    margin: 1em 0;
    page-break-inside: avoid;
}

/* Horizontal rules - thin line */
hr {
    border: none;
    border-top: 0.5pt solid #000;
    margin: 1.5em 0;
}

/* Links */
a {
    color: #000;
    text-decoration: none;
}

/* Title formatting */
h1 + p strong:only-child {
    display: block;
    text-align: center;
    font-size: 12pt;
    font-weight: normal;
    margin: 0.5em 0;
}

/* Date line after working paper */
h1 ~ p:nth-of-type(2) {
    text-align: center;
    margin-bottom: 1.5em;
}

/* Abstract header */
h2:first-of-type {
    text-align: left;
    font-size: 12pt;
}

/* Keywords and JEL */
p strong:first-child {
    font-weight: bold;
}

/* References - hanging indent */
h2#references ~ p,
h2:last-of-type ~ p {
    text-indent: -2em;
    padding-left: 2em;
    margin-bottom: 0.5em;
    text-align: left;
}

/* Table captions above tables */
p + table {
    margin-top: 0;
}

/* Page breaks */
h2 {
    page-break-before: auto;
    page-break-after: avoid;
}

/* Ensure figures stay with captions */
img + p {
    page-break-before: avoid;
}

/* Note styling */
p:has(> em:only-child) {
    text-align: left;
    font-size: 10pt;
}
"""

# Create full HTML document
html_document = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Measuring What Matters</title>
</head>
<body>
{html_body}
</body>
</html>
"""

# Generate PDF
output_path = Path("inflation_analysis.pdf")
HTML(string=html_document, base_url=str(Path.cwd())).write_pdf(
    output_path,
    stylesheets=[CSS(string=css_style)]
)

print(f"PDF generated: {output_path}")
print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")
