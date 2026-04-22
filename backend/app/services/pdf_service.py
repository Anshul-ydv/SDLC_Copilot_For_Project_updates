import os
import re
from fpdf import FPDF, HTMLMixin
from datetime import datetime


class PDFGenerator(FPDF, HTMLMixin):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(30, 80, 160)
        self.cell(0, 10, 'SDLC Automation Copilot', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', 'I', 9)
        self.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', new_x="RMARGIN", new_y="NEXT", align='C')


def sanitize_for_pdf(content: str) -> str:
    """Sanitize markdown/unicode content for safe PDF rendering."""
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    content = content.encode('ascii', 'ignore').decode('ascii')
    return content


def markdown_to_simple_html(content: str) -> str:
    """Convert basic markdown to simple HTML that fpdf2 can render."""
    lines = content.split('\n')
    html_lines = []
    in_table = False

    for line in lines:
        stripped = line.strip()

        # Table rows
        if stripped.startswith('|') and stripped.endswith('|'):
            if not in_table:
                html_lines.append('<table border="1" cellpadding="4" cellspacing="0" width="100%">')
                in_table = True
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            # Skip separator rows (like |---|---|)
            if all(set(c) <= set(['-', ':', ' ']) for c in cells):
                continue
            # Clean cells - remove any HTML tags that fpdf2 doesn't support in tables
            clean_cells = []
            for c in cells:
                # Remove <br> tags and replace with space
                c = c.replace('<br/>', ' ').replace('<br>', ' ')
                # Remove bold tags inside cells for simplicity
                c = re.sub(r'</?b>', '', c)
                clean_cells.append(c)
            html_lines.append('<tr>' + ''.join(f'<td>{c}</td>' for c in clean_cells) + '</tr>')
            continue
        else:
            if in_table:
                html_lines.append('</table><br/>')
                in_table = False

        if stripped.startswith('### '):
            html_lines.append(f'<h3>{stripped[4:]}</h3>')
        elif stripped.startswith('## '):
            html_lines.append(f'<h2>{stripped[3:]}</h2>')
        elif stripped.startswith('# '):
            html_lines.append(f'<h1>{stripped[2:]}</h1>')
        elif stripped.startswith('**') and stripped.endswith('**'):
            html_lines.append(f'<b>{stripped[2:-2]}</b><br/>')
        elif stripped.startswith('- ') or stripped.startswith('* '):
            html_lines.append(f'<li>{stripped[2:]}</li>')
        elif stripped == '':
            html_lines.append('<br/>')
        else:
            line_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', stripped)
            html_lines.append(f'{line_html}<br/>')

    if in_table:
        html_lines.append('</table>')

    return '\n'.join(html_lines)


def generate_pdf_from_text(content: str, filename: str = "generated_document.pdf") -> str:
    """Generate a PDF from markdown/plain text content and return the file path."""
    pdf = PDFGenerator()
    pdf.alias_nb_pages()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_title("SDLC Generated Document")
    pdf.set_author("SDLC Automation Copilot")

    clean_content = sanitize_for_pdf(content)
    html_content = markdown_to_simple_html(clean_content)

    pdf.set_font('Helvetica', '', 11)
    pdf.write_html(html_content)

    output_dir = "/tmp/sdlc_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    pdf.output(output_path)
    return output_path


pdf_service = generate_pdf_from_text
