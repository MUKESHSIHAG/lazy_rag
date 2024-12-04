import pdfplumber
import os

def extract_text(pdf_path):
    """Extract text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_pdf_data(pdf_path):
    """Extract text, tables, and images from a PDF."""
    print("Extracting text...")
    text = extract_text(pdf_path)
    
    return {
        "text": text
    }

# Example Usage
pdf_path = "/Users/mukeshsihag/Desktop/nlp/backend/data/economy_survey.pdf"
output_folder = "/Users/mukeshsihag/Desktop/nlp/backend/data"

print("Starting extraction...")
pdf_data = extract_pdf_data(pdf_path)

# Save the extracted data
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Save text to a file
with open(os.path.join(output_folder, "raw_text.txt"), "w", encoding="utf-8") as f:
    f.write(pdf_data["text"])

print("Extraction complete!")
