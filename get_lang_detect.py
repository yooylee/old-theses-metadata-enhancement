import os
import csv
from langdetect import detect
from pdf2image import convert_from_path
import pytesseract
import fitz  # PyMuPDF
from lingua import LanguageDetectorBuilder

# Define the input/output CSV and PDF directory paths
INPUT_CSV = "name_of_your_csv_input.csv"
OUTPUT_CSV = "name_of_your_csv_output.csv"
PDF_DIR = "dspace_download"

# QA pass threshold (%)
QA_THRESHOLD = 0.95  # 95%

# Initialize Lingua language detector
lingua_detector = LanguageDetectorBuilder.from_all_languages().build()

def extract_text_from_pdf(pdf_path, max_pages=20, dpi=100):
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for i, page in enumerate(doc):
            if i >= max_pages:
                break
            full_text += page.get_text()
        doc.close()

        if full_text.strip():
            return full_text
        else:
            return extract_text_via_ocr(pdf_path, max_pages, dpi)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def extract_text_via_ocr(pdf_path, max_pages=20, dpi=100):
    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=max_pages, dpi=dpi)
        ocr_text = ""
        for image in images:
            ocr_text += pytesseract.image_to_string(image) + "\n"
        return ocr_text
    except Exception as e:
        print(f"OCR failed on {pdf_path}: {e}")
        return ""

def detect_language_with_qa(text):
    try:
        lang_detected_code = detect(text) 
        lingua_result = lingua_detector.detect_language_of(text)
        lingua_code = (
            lingua_result.iso_code_639_1.name.lower()
            if lingua_result and lingua_result.iso_code_639_1
            else None
        )

        lingua_lang_name = lingua_result.name if lingua_result else None

        if lingua_code is None:
            return lang_detected_code, "und", False

        if lang_detected_code.lower() == lingua_code:
            return lang_detected_code, lingua_lang_name, True
        else:
            return lang_detected_code, lingua_lang_name, False
    except Exception as e:
        return "und", "und", False

# Step 1: Read CSV and process rows
updated_rows = []
qa_pass_count = 0
qa_fail_count = 0

with open(INPUT_CSV, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames + ["language", "lan", "qa_pass"]
    for row in reader:
        bitstream_uuid = row['Bitstream UUID']
        pdf_path = os.path.join(PDF_DIR, f"{bitstream_uuid}.pdf")

        if os.path.exists(pdf_path):
            text = extract_text_from_pdf(pdf_path)
            lang, lingua_lang, qa_pass = detect_language_with_qa(text)
            if qa_pass:
                qa_pass_count += 1
            else:
                qa_fail_count += 1
        else:
            print(f"File not found: {pdf_path}")
            lang = "missing"
            lingua_lang = "missing"
            qa_pass = False

        row["language"] = lang
        row["lan"] = lingua_lang
        row["qa_pass"] = qa_pass
        updated_rows.append(row)

# Step 2: Write output CSV with QA summary appended
total_records = len(updated_rows)
qa_success_rate = qa_pass_count / total_records * 100 if total_records > 0 else 0

with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as outcsv:
    writer = csv.DictWriter(outcsv, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_rows)

    # Blank row separator
    writer.writerow({})

    # QA summary rows
    writer.writerow({"language": "QA Summary"})
    writer.writerow({"language": "QA Success Rate (%)", "lan": f"{qa_success_rate:.2f}"})
    writer.writerow({"language": "QA Passed", "lan": f"{qa_pass_count}/{total_records}"})
    writer.writerow({"language": "QA Failed", "lan": f"{qa_fail_count}/{total_records}"})
    writer.writerow({"language": "Threshold (%)", "lan": f"{QA_THRESHOLD * 100:.0f}"})

print(f"Done. Results saved to {OUTPUT_CSV}")
