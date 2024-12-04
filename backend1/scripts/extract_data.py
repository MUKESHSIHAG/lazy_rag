import PyPDF2

def extract_text_from_pdf(pdf_path, start_page, end_page):
    pdf_text = []
    with open(pdf_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page in range(start_page - 1, end_page):
            pdf_text.append(pdf_reader.pages[page].extract_text())
    return "\n".join(pdf_text)

if __name__ == "__main__":
    pdf_path = "/Users/mukeshsihag/Desktop/nlp/backend1/data/economy_survey.pdf"
    output_txt_file = "/Users/mukeshsihag/Desktop/nlp/backend1/data/raw_text.txt"
    start_page = 1
    end_page = 35

    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path, start_page, end_page)

    with open(output_txt_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Raw text extracted and saved to {output_txt_file}")
