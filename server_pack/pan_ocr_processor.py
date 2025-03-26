import sys
import json
import os
import re
import logging
from pytesseract import image_to_string
from PIL import Image
from pdf2image import convert_from_path
import pytesseract

# Set Tesseract and Poppler paths
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
poppler_path = r'C:\poppler-24.08.0\Library\bin'

# Logging setup
logging.basicConfig(
    filename="pan_ocr_errors.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def clean_text(text):
    """ Cleans extracted OCR text by removing unwanted characters and extra spaces. """
    text = re.sub(r'[^A-Za-z0-9/\s]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces
    return text

def extract_data(file_paths, attributes):
    extracted_data = []
    patterns = {
        "name": r"Name\s*\n([A-Z\s]+)",  # Extracts the name after "Name"
        "pan number": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",  # Matches 10-character PAN
        "dob": r"\b\d{2}/\d{2}/\d{4}\b",  # Matches "29/07/2004"
        "father's name": r"Father'?s Name\s*\n([A-Z\s]+)"  # Extracts Father's Name after "Father's Name"
    }

    for file_path in file_paths:
        file_result = {"file": os.path.basename(file_path)}

        if not os.path.exists(file_path):
            logging.error(f"File {file_path} not found")
            file_result["error"] = "File not found"
        else:
            try:
                # Convert PDF to images and extract text
                images = convert_from_path(file_path, poppler_path=poppler_path)
                raw_text = "\n".join([image_to_string(img, config='--psm 6') for img in images])
                cleaned_text = clean_text(raw_text)  # Apply text cleaning
                
                extracted_info = {}
                
                # Extract Name: Correctly identify the name
                name_match = re.findall(patterns["name"], cleaned_text)
                extracted_info["name"] = name_match[0].strip() if name_match else "Not Found"

                # Extract PAN Number
                pan_match = re.search(patterns["pan number"], cleaned_text)
                extracted_info["pan number"] = pan_match.group().strip() if pan_match else "Not Found"

                # Extract Date of Birth
                dob_match = re.search(patterns["dob"], cleaned_text)
                extracted_info["dob"] = dob_match.group().strip() if dob_match else "Not Found"

                # Extract Father's Name
                father_match = re.findall(patterns["father's name"], cleaned_text)
                extracted_info["father's name"] = father_match[0].strip() if father_match else "Not Found"

                file_result["attributes"] = extracted_info
            except Exception as e:
                logging.error(f"Error processing {file_path}: {str(e)}")
                file_result["error"] = str(e)

        extracted_data.append(file_result)

    print(json.dumps(extracted_data, indent=4))

if __name__ == "__main__":
    file_paths = sys.argv[1:-1]
    attributes = json.loads(sys.argv[-1])

    result = extract_data(file_paths, attributes)
