from fpdf import FPDF
import datetime

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'SDLC Automation Copilot - Document', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_pdf_from_text(content: str, filename: str = "generated_document.pdf") -> str:
    pdf = PDFGenerator()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_title("SDLC Generated Document")
    pdf.set_author("SDLC Automation Copilot")

    pdf.set_font('helvetica', '', 12)
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
            
        if line.startswith('### '):
            pdf.set_font('helvetica', 'B', 14)
            pdf.multi_cell(190, 10, line[4:])
            pdf.set_font('helvetica', '', 12)
        elif line.startswith('## '):
            pdf.set_font('helvetica', 'B', 16)
            pdf.multi_cell(190, 12, line[3:])
            pdf.set_font('helvetica', '', 12)
        elif line.startswith('# '):
            pdf.set_font('helvetica', 'B', 18)
            pdf.multi_cell(190, 15, line[2:])
            pdf.set_font('helvetica', '', 12)
        elif line.startswith('* ') or line.startswith('- '):
            pdf.multi_cell(190, 10, "  - " + line[2:])
        else:
            pdf.multi_cell(190, 10, line)
            
    output_path = f"/tmp/{filename}"
    pdf.output(output_path)
    return output_path

pdf_service = generate_pdf_from_text
