"""Functions used in the computation of subtasks of the pdfgen task"""
from reportlab.pdfgen import canvas

point = 1
inch = 72

def make_pdf_file(text, output_filename, np):
    c = canvas.Canvas(output_filename, pagesize=(8.5 * inch, 11 * inch))
    c.setStrokeColorRGB(0,0,0)
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica", 12 * point)
    for pn in range(1, np + 1):
        v = 10 * inch
        for subtline in text.split( '\n' ):
            c.drawString( 1 * inch, v, subtline )
            v -= 12 * point
        c.showPage()
    c.save()

def run_pdfgen_task(text, output_filename):
    make_pdf_file(text, output_filename, 1)

