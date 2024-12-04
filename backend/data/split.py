from PyPDF2 import PdfReader, PdfWriter

def extract_pages(input_pdf, output_pdf, start_page, end_page):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for i in range(start_page - 1, end_page):  # Pages are zero-indexed
        writer.add_page(reader.pages[i])

    with open(output_pdf, "wb") as f:
        writer.write(f)
    print(f"Extracted pages {start_page} to {end_page} into {output_pdf}")

# Input and output paths
input_pdf_path = "/Users/mukeshsihag/Desktop/nlp/backend/data/test.pdf"
output_pdf_path = "test1.pdf"

# Extract pages 48 to 85
extract_pages(input_pdf_path, output_pdf_path, start_page=1, end_page=10)
