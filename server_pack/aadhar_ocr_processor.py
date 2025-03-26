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

# Load the ML model for attribute classification
try:
    model = joblib.load("aadhar_classifier.pkl")
except Exception as e:
    logging.error(f"Error loading ML model: {str(e)}")
    model = None  # Continue execution without ML support

# Logging setup
logging.basicConfig(
    filename="ocr_errors.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def extract_data(file_paths, attributes):
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
                extracted_attributes = extract_attributes(text, attributes)
                
                # Check missing attributes and use ML model
                if model:
                    for attr in attributes:
                        if attr not in extracted_attributes or not extracted_attributes[attr]:
                            predicted_attr = predict_attribute(text)
                            if predicted_attr and predicted_attr.get(attr):
                                extracted_attributes[attr] = predicted_attr[attr]

                # Set attributes that are still missing to "Not Found"
                for attr in attributes:
                    if attr not in extracted_attributes or not extracted_attributes[attr]:
                        logging.warning(f"Attribute '{attr}' not found in {file_path}")
                        extracted_attributes[attr] = "Not Found"

                file_result["attributes"] = extracted_attributes
            except Exception as e:
                logging.error(f"Error processing {file_path}: {str(e)}")
                file_result["error"] = str(e)

        extracted_data.append(file_result)
    
    return extracted_data

def extract_text(file_path):
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

def extract_attributes(text, attributes):
    extracted_info = {}
    patterns = {
        "name": r"(?<=\n)[A-Za-z\s.'-]{3,100}(?=\s+S/O)",
        "address": r"(?<=\bS/O\b)[\s\S]*?(?=\b\d{10}\b)",
        "dob": r"DOB:?\s*(\d{2}/\d{2}/\d{4})",
        "gender": r"\b(MALE|FEMALE)\b",
        "aadhar number": r"\d{4}\s\d{4}\s\d{4}"
    }

    for attribute in attributes:
        pattern = patterns.get(attribute.lower())
        if pattern:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_value = match.group(0).replace("\n", " ").strip()
                extracted_info[attribute] = extracted_value

    logging.debug(f"Extracted attributes: {extracted_info}")
    return extracted_info

def predict_attribute(text):
    """
    Uses the ML model to predict the attribute type from OCR text.
    Returns a dictionary with predicted attributes.
    """
    if not model:
        logging.warning("ML model not loaded, skipping prediction.")
        return {}

    try:
        predicted_label = model.predict([text])[0]
        return {predicted_label: text.strip()}
    except Exception as e:
        logging.error(f"Error during ML prediction: {str(e)}")
        return {}

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
