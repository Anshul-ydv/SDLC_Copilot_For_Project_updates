from fpdf import FPDF
import datetime
from markdown_it import MarkdownIt

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'SDLC Automation Copilot - Document', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', new_x="RMARGIN", new_y="NEXT", align='C')

def generate_pdf_from_text(content: str, filename: str = "generated_document.pdf") -> str:
    pdf = PDFGenerator()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_title("SDLC Generated Document")
    pdf.set_author("SDLC Automation Copilot")

    pdf.set_font('helvetica', '', 12)
    
    # Strip or replace complex unicode characters that Helvetica can't handle
    content = content.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-").replace("…", "...")
    content = content.encode('ascii', 'ignore').decode('ascii')
    
    md = MarkdownIt()
    html_content = md.render(content)
    
    pdf.write_html(html_content)
    
    output_path = f"/tmp/{filename}"
    pdf.output(output_path)
    return output_path

pdf_service = generate_pdf_from_text
