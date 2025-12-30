#!/usr/bin/env python3
"""
Generate PDF from peer review markdown using WeasyPrint.
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path

# Read the markdown file
md_path = Path("peer_review.md")
md_content = md_path.read_text()

# Convert markdown to HTML
md_extensions = ['tables', 'fenced_code']
html_body = markdown.markdown(md_content, extensions=md_extensions)

# Professional review CSS styling
css_style = """
@page {
    size: letter;
    margin: 1in;
    @top-center {
        content: "Peer Review";
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
    line-height: 1.5;
    color: #1a1a1a;
}

h1 {
    font-size: 16pt;
    font-weight: bold;
    text-align: center;
    margin-top: 0;
    margin-bottom: 1em;
    border-bottom: 2px solid #333;
    padding-bottom: 0.5em;
}

h2 {
    font-size: 13pt;
    font-weight: bold;
    margin-top: 1.5em;
    margin-bottom: 0.75em;
    color: #1a1a1a;
    border-bottom: 1px solid #ccc;
    padding-bottom: 0.25em;
}

h3 {
    font-size: 11pt;
    font-weight: bold;
    margin-top: 1.25em;
    margin-bottom: 0.5em;
}

p {
    margin-top: 0;
    margin-bottom: 0.75em;
    text-align: justify;
}

/* Reviewer comments - blockquotes */
blockquote {
    margin: 1em 0;
    padding: 0.75em 1em;
    background-color: #f9f9f9;
    border-left: 4px solid #2c5aa0;
    font-style: normal;
}

blockquote p {
    margin-bottom: 0.5em;
}

blockquote p:last-child {
    margin-bottom: 0;
}

/* Tables */
table {
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 10pt;
    width: 100%;
}

th, td {
    border: 1px solid #333;
    padding: 6px 10px;
    text-align: left;
    vertical-align: top;
}

th {
    background-color: #f0f0f0;
    font-weight: bold;
}

/* Lists */
ul, ol {
    margin: 0.75em 0;
    padding-left: 2em;
}

li {
    margin-bottom: 0.35em;
}

/* Emphasis */
strong {
    font-weight: bold;
}

em {
    font-style: italic;
}

/* Horizontal rules */
hr {
    border: none;
    border-top: 1px solid #999;
    margin: 1.5em 0;
}

/* Code */
code {
    font-family: 'Courier New', Courier, monospace;
    font-size: 10pt;
    background-color: #f5f5f5;
    padding: 1px 4px;
}

/* Recommendation styling */
p strong:first-child {
    color: #2c5aa0;
}

/* Suggested revision styling */
p:has(strong:contains("Suggested revision")) {
    background-color: #fff8e6;
    padding: 0.5em;
    border-left: 3px solid #f0ad4e;
    margin: 0.5em 0;
}
"""

# Create full HTML document
html_document = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Peer Review</title>
</head>
<body>
{html_body}
</body>
</html>
"""

# Generate PDF
output_path = Path("peer_review.pdf")
HTML(string=html_document).write_pdf(
    output_path,
    stylesheets=[CSS(string=css_style)]
)

print(f"PDF generated: {output_path}")
print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")
