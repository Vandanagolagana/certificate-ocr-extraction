import sys
import json
import os
import re
import logging
import joblib
from pytesseract import image_to_string
from PIL import Image
from pdf2image import convert_from_path
import pytesseract

# Set Tesseract and Poppler paths
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
poppler_path = r'C:\\poppler-24.08.0\\Library\\bin'

# Load trained ML model
try:
    model = joblib.load("id_classifier.pkl")
except Exception as e:
    logging.error(f"Error loading ML model: {str(e)}")
    model = None  # If model is missing, regex will be used exclusively

# Logging setup
logging.basicConfig(
    filename="ocr_errors.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def extract_data(file_paths, attributes):
    """ Extract data from multiple PDF/image files. """
    extracted_data = []
    
    for file_path in file_paths:
        file_result = {"file": os.path.basename(file_path)}

        if not os.path.exists(file_path):
            logging.error(f"File {file_path} not found")
            file_result["error"] = "File not found"
        else:
            try:
                text = extract_text(file_path)
                logging.debug(f"Raw OCR text from {file_path}: {text}")
                cleaned_text = clean_text(text)
                file_result["attributes"] = extract_attributes(cleaned_text, attributes)
            except Exception as e:
                logging.error(f"Error processing {file_path}: {str(e)}")
                file_result["error"] = str(e)

        extracted_data.append(file_result)
    
    return extracted_data

def extract_text(file_path):
    """ Extract text from images or PDFs using OCR. """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")
   
    try:
        if file_path.lower().endswith('.pdf'):
            images = convert_from_path(file_path, poppler_path=poppler_path)
            text = "\n".join([image_to_string(img, config='--psm 11') for img in images])
        else:
            image = Image.open(file_path)
            text = image_to_string(image, config='--psm 11')

        if not text.strip():
            raise ValueError(f"OCR returned empty text for {file_path}")
        return text
    except Exception as e:
        raise RuntimeError(f"Error extracting text from {file_path}: {str(e)}")

def clean_text(text):
    """ Clean extracted text by removing extra spaces and newlines. """
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    logging.debug(f"Cleaned text: {text}")
    return text

def predict_with_ml(text):
    """ Use ML model to predict attributes when regex fails. """
    if model:
        prediction = model.predict([text])
        return prediction[0]  # Return the predicted attribute
    return "Not Found"

def extract_attributes(text, attributes):
    """ Extract attributes using regex first, then fallback to ML model. """
    extracted_info = {}
    patterns = {
        "name": r"([A-Z]\.[A-Za-z]+)",  # Matches G.Vandana
        "roll no": r"(\d{5}[A-Z]\d{4}|\d{12})",  # Matches 21131A0554
        "dob": r"D\.O\.B\s*[:\-]?\s*(\d{2}-\d{2}-\d{4})",
        "blood group": r"Blood\s*Group\s*[:\-]?\s*([ABOAB]+[\s]?[+-]?(?:positive|negative)?)",
        "emergency contact": r"Emergency Contact\s*[:\-]?\s*(\d+)", 
        "mobile": r"Mobile\s*[:\-]?\s*(\d+)"
    }

    for attribute in attributes:
        pattern = patterns.get(attribute.lower())
        if pattern:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_info[attribute] = match.group(1).strip()  # Extract only matched value
            else:
                # Use ML model if regex fails
                extracted_info[attribute] = predict_with_ml(text)
        else:
            extracted_info[attribute] = "Not Found"
    
    logging.debug(f"Extracted attributes: {extracted_info}")
    return extracted_info

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(json.dumps({"error": "Usage: python ocr_processor.py <file1> <file2> ... '<attributes_list_as_json>'"}))

    file_paths = sys.argv[1:-1]

    try:
        attributes = json.loads(sys.argv[-1])
        if not isinstance(attributes, list):
            raise ValueError("Attributes must be a list.")
    except (json.JSONDecodeError, ValueError) as e:
        sys.exit(json.dumps({"error": f"Error parsing attributes: {str(e)}"}))

    result = extract_data(file_paths, attributes)

    # ✅ Ensure only JSON is printed
    print(json.dumps(result, indent=4, ensure_ascii=False))

