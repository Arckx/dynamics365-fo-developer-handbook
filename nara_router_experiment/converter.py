"""
D365 F&O Combined Guide — Markdown to PDF converter (Playwright/Chromium edition)
Renders via a real Chromium engine, so all CSS (table-layout: fixed,
word-break, etc.) works exactly as it would in your actual browser —
no xhtml2pdf or Pango/GTK limitations.
"""

import markdown
from playwright.sync_api import sync_playwright

BOOK_ORDER = [
    "d365-fao-interest.md",
    "d365-fao-learning-journey.md",
    "d365-learning-guide.md",
    "d365-xpp-quick-reference.md",
    "d365-xpp-exercises.md",
    "d365-guide-cross-reference.md",
    "d365-glossary.md",
]

OUTPUT_PDF = "D365_Combined_Guide.pdf"

GLYPH_REPLACEMENTS = {
    "✅": "[x]",
    "❌": "[ ]",
    "⚠️": "[!]",
    "⚠": "[!]",
    "🏁": "[FINISH]",
    "│": "|",
    "├": "+",
    "─": "-",
    "└": "+",
    "▼": "v",
    "\ufe0f": "",
}


def clean_text(text):
    for old, new in GLYPH_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def build_html(files):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    sections = []
    for i, fname in enumerate(files):
        with open(fname, "r", encoding="utf-8") as fh:
            raw = fh.read()
        raw = clean_text(raw)
        html_body = md.convert(raw)
        md.reset()
        page_break = "" if i == 0 else '<div style="page-break-before: always;"></div>'
        sections.append(f"{page_break}\n{html_body}")

    body = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{ size: A4; margin: 2cm 1.8cm; }}
    body {{
        font-family: "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.45;
    }}
    h1 {{ font-size: 19pt; margin-top: 0; page-break-before: always; }}
    h1:first-of-type {{ page-break-before: avoid; }}
    h2 {{ font-size: 14pt; margin-top: 16pt; }}
    h3 {{ font-size: 11.5pt; margin-top: 12pt; }}

    pre {{
        font-family: Consolas, "Courier New", monospace;
        font-size: 8pt;
        background-color: #f4f4f4;
        white-space: pre-wrap;
        word-wrap: break-word;
        padding: 6pt;
        border: 0.5pt solid #ccc;
    }}
    code {{
        font-family: Consolas, "Courier New", monospace;
        font-size: 8pt;
        background-color: #f4f4f4;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }}

    table {{
        table-layout: fixed;
        width: 100%;
        border-collapse: collapse;
        margin: 10pt 0;
    }}
    th, td {{
        border: 0.5pt solid #999;
        padding: 4pt 5pt;
        text-align: left;
        font-size: 8.5pt;
        word-wrap: break-word;
        overflow-wrap: break-word;
        word-break: break-word;
        vertical-align: top;
    }}
    th {{ background-color: #e8e8e8; font-weight: bold; }}
    td code, th code {{
        font-size: 7.5pt;
        word-break: break-all;
        white-space: pre-wrap;
    }}

    blockquote {{
        border-left: 3pt solid #ccc;
        margin-left: 0;
        padding-left: 10pt;
        color: #555;
    }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def main():
    print("Building combined document in book order:")
    for i, f in enumerate(BOOK_ORDER, 1):
        print(f"  {i}. {f}")

    html = build_html(BOOK_ORDER)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(
            path=OUTPUT_PDF,
            format="A4",
            margin={"top": "2cm", "bottom": "2cm", "left": "1.8cm", "right": "1.8cm"},
            print_background=True,
        )
        browser.close()

    print(f"\nDone. Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    main()