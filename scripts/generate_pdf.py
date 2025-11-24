import os
from fpdf import FPDF

def create_pdf(input_file, output_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# "):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt=line[2:], ln=True, align='L')
                pdf.set_font("Arial", size=12)
            elif line.startswith("## "):
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, txt=line[3:], ln=True, align='L')
                pdf.set_font("Arial", size=12)
            elif line.startswith("**"):
                # Simple bold handling for lines starting with bold
                pdf.set_font("Arial", 'B', 12)
                pdf.multi_cell(0, 10, txt=line.replace("**", ""))
                pdf.set_font("Arial", size=12)
            else:
                pdf.multi_cell(0, 10, txt=line)

    pdf.output(output_file)
    print(f"PDF created at {output_file}")

if __name__ == "__main__":
    input_md = "data/regulations/content.md"
    output_pdf = "data/regulations/hazmat_regulations.pdf"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    
    create_pdf(input_md, output_pdf)
