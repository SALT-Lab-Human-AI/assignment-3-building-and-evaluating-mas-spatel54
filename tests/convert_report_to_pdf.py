"""
Convert Technical Report from Markdown to PDF
"""

from markdown2 import markdown
from weasyprint import HTML, CSS
from pathlib import Path

# Read markdown
md_file = Path("submission_artifacts/TECHNICAL_REPORT.md")
pdf_file = Path("submission_artifacts/technical_report.pdf")

print("Converting Technical Report to PDF...")
print(f"Source: {md_file}")
print(f"Output: {pdf_file}")

with open(md_file, 'r') as f:
    md_content = f.read()

# Convert markdown to HTML
html_content = markdown(md_content, extras=['tables', 'fenced-code-blocks'])

# Add CSS for better formatting
css_content = """
@page {
    size: letter;
    margin: 1in;
}

body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 12pt;
    line-height: 1.0;
    color: #333;
}

h1 {
    font-size: 18pt;
    font-weight: bold;
    margin-top: 0;
    margin-bottom: 12pt;
    text-align: center;
}

h2 {
    font-size: 14pt;
    font-weight: bold;
    margin-top: 16pt;
    margin-bottom: 8pt;
}

h3 {
    font-size: 13pt;
    font-weight: bold;
    margin-top: 12pt;
    margin-bottom: 6pt;
}

p {
    margin-bottom: 6pt;
    text-align: justify;
}

ul, ol {
    margin-bottom: 8pt;
}

li {
    margin-bottom: 4pt;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 12pt 0;
    font-size: 11pt;
}

th, td {
    border: 1px solid #ddd;
    padding: 6pt;
    text-align: left;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

code {
    background-color: #f5f5f5;
    padding: 2pt 4pt;
    font-family: 'Courier New', monospace;
    font-size: 10pt;
}

pre {
    background-color: #f5f5f5;
    padding: 8pt;
    border-left: 3pt solid #ccc;
    overflow-x: auto;
    margin: 8pt 0;
}

pre code {
    background-color: transparent;
    padding: 0;
}

strong {
    font-weight: bold;
}

em {
    font-style: italic;
}

hr {
    border: none;
    border-top: 1pt solid #ccc;
    margin: 16pt 0;
}

a {
    color: #0066cc;
    text-decoration: none;
}

blockquote {
    border-left: 3pt solid #ccc;
    padding-left: 12pt;
    margin: 12pt 0;
    font-style: italic;
}
"""

# Create full HTML document
full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Multi-Agent Research Assistant for HCI</title>
</head>
<body>
{html_content}
</body>
</html>
"""

# Convert to PDF
HTML(string=full_html).write_pdf(
    pdf_file,
    stylesheets=[CSS(string=css_content)]
)

print(f"\n✓ PDF created successfully!")
print(f"File size: {pdf_file.stat().st_size / 1024:.1f} KB")
print(f"\nOpen with: open {pdf_file}")
