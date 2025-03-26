# import sys
# import json
# import os
# import re
# import logging
# import pandas as pd
# import joblib
# from pytesseract import image_to_string
# from PIL import Image
# from pdf2image import convert_from_path
# import pytesseract

# # Set Tesseract and Poppler paths
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# poppler_path = r'C:\poppler-24.08.0\Library\bin'

# # Load ML model and vectorizer if available
# model_path = "inter_classifier.pkl"
# vectorizer_path = "vectorizer.pkl"
# model = joblib.load(model_path) if os.path.exists(model_path) else None
# vectorizer = joblib.load(vectorizer_path) if os.path.exists(vectorizer_path) else None

# # Logging setup
# logging.basicConfig(
#     filename="ocr_errors.log",
#     level=logging.DEBUG,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

# def extract_data(file_paths, attributes):
#     """ Extracts text and structured data from files and saves to Excel. """
#     extracted_data = []

#     for file_path in file_paths:
#         file_result = {"file": os.path.basename(file_path)}

#         if not os.path.exists(file_path):
#             logging.error(f"File {file_path} not found")
#             file_result["error"] = "File not found"
#         else:
#             try:
#                 text = extract_text(file_path)
#                 logging.debug(f"Raw OCR text from {file_path}: {text}")
#                 cleaned_text = clean_text(text)
#                 file_result["attributes"] = extract_attributes(cleaned_text, attributes)
#             except Exception as e:
#                 logging.error(f"Error processing {file_path}: {str(e)}")
#                 file_result["error"] = str(e)

#         extracted_data.append(file_result)

#     save_to_excel(extracted_data)  # Save results to Excel
#     return extracted_data

# def extract_text(file_path):
#     """ Extract text from an image or PDF. """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"File {file_path} not found.")

#     try:
#         if file_path.lower().endswith('.pdf'):
#             images = convert_from_path(file_path, poppler_path=poppler_path)
#             text = "\n".join([image_to_string(img, config='--psm 11') for img in images])
#         else:
#             image = Image.open(file_path)
#             text = image_to_string(image, config='--psm 11')

#         if not text.strip():
#             raise ValueError(f"OCR returned empty text for {file_path}")
#         return text
#     except Exception as e:
#         raise RuntimeError(f"Error extracting text from {file_path}: {str(e)}")

# def clean_text(text):
#     """ Clean OCR text by removing extra spaces and special characters. """
#     text = re.sub(r'\n+', ' ', text)
#     text = re.sub(r'\s{2,}', ' ', text)
#     text = text.strip()
#     logging.debug(f"Cleaned text: {text}")
#     return text

# def extract_attributes(text, attributes):
#     """ Extract attributes using regex; fall back to ML model if regex fails. """
#     patterns = {
#         # "name": r"to certify that\s+([A-Z\s]+?)(?=\s*Father Name)|to certify that\s+([A-Z\s]+)",
#         # "father's name": r"Father['’]?s?\s*Name\s*[:\-]?\s*([A-Z\s]+)(?=\s*Mother['’]?s?\s*Name|$)",  
#         # "mother's name": r"Mother['’]?s?\s*Name\s*[:\-]?\s*([A-Z\s]+?)(?=\s*bearing\s*Registered\s*No|$)",
#         # "aadhaar number": r"\b\d{12}\b",
#         # "registered number": r"(?:Registered\s*No\.\s*)?(\b\d{10,11}\b)",
#         # "grand total": r"In words\s*[:\-]?\s*\([A-Z\s]+\)\*"
#         "name": r"to certify that\s+([A-Z\s]+?)(?=\s*Father Name)|to certify that\s+([A-Z\s]+)",
#         "father's name": r"Father['’]?s?\s*Name\s*[:\-]?\s*([A-Z\s]+)(?=\s*Mother['’]?s?\s*Name|$)",  
#         "mother's name": r"Mother['’]?s?\s*Name\s*[:\-]?\s*([A-Z\s]+?)(?=\s*bearing\s*Registered\s*No|$)",
        
#         "aadhaar number": r"\b\d{12}\b",
#         "registered number": r"(?:Registered\s*No\.\s*)?(\b\d{10,11}\b)",
#         "grand total": r"In words\s*[:\-]?\s*\*([A-Z\s*]+)\*"
#     }

#     extracted_info = {}
#     for attribute in attributes:
#         pattern = patterns.get(attribute.lower())
#         extracted_value = None

#         if pattern:
#             match = re.findall(pattern, text, re.IGNORECASE)
#             if match:
#                 extracted_value = match[0].strip() if isinstance(match[0], str) else match[0][0].strip()

#         # If regex fails, use ML model
#         if not extracted_value and model and vectorizer:
#             extracted_value = predict_with_ml(text)

#         # If both regex and ML fail, return "Not found"
#         extracted_info[attribute] = extracted_value if extracted_value else "Not found"

#     return extracted_info

# def predict_with_ml(text):
#     """ Use the ML model to predict attributes when regex fails. """
#     try:
#         text_vectorized = vectorizer.transform([text])
#         prediction = model.predict(text_vectorized)
#         return prediction[0]  # Return the predicted label
#     except Exception as e:
#         logging.error(f"ML prediction error: {e}")
#         return None

# def save_to_excel(data):
#     """ Save extracted data to an Excel file. """
#     df = pd.DataFrame(data)
#     output_path = "extracted_data.xlsx"
#     df.to_excel(output_path, index=False, engine="openpyxl")
#     logging.info(f"Data saved to {output_path}")  # ✅ Logs message instead of printing

# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         sys.exit(json.dumps({"error": "Usage: python ocr_processor.py <file1> <file2> ... '<attributes_list_as_json>'"}))

#     file_paths = sys.argv[1:-1]

#     try:
#         attributes = json.loads(sys.argv[-1])
#         if not isinstance(attributes, list):
#             raise ValueError("Attributes must be a list.")
#     except (json.JSONDecodeError, ValueError) as e:
#         sys.exit(json.dumps({"error": f"Error parsing attributes: {str(e)}"}))

#     result = extract_data(file_paths, attributes)

#     # ✅ Ensure pure JSON output
#     try:
#         json_data = json.dumps(result, indent=4, ensure_ascii=False)
#         print(json_data)
#     except Exception as e:
#         logging.error(f"JSON Encoding Error: {e}")
#         sys.exit(json.dumps({"error": "Invalid JSON format"}))

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
                cleaned_text = clean_text(text)
                file_result["attributes"] = extract_attributes(cleaned_text, attributes)
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

def clean_text(text):
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    logging.debug(f"Cleaned text: {text}")
    return text


def extract_attributes(text, attributes):
    """ Extract specific attributes using refined regex patterns. """
    patterns = {
         "name": r"to certify that\s+([A-Z\s]+?)(?=\s*Father Name)|to certify that\s+([A-Z\s]+)",
        "father's name": r"Father['’]?s?\s*Name\s*[:\-]?\s*([A-Z\s]+)(?=\s*Mother['’]?s?\s*Name|$)",  
        "mother's name": r"Mother['’]?s?\s*Name\s*[:\-]?\s*([A-Z\s]+?)(?=\s*bearing\s*Registered\s*No|$)",
        
        "aadhaar number": r"\b\d{12}\b",
        "registered number": r"(?:Registered\s*No\.\s*)?(\b\d{10,11}\b)",
        #"grand total": r"In words\s*[:\-]?\s*\*([A-Z\s*]+)\*"
        
    }

    extracted_info = {}
    for attribute, pattern in patterns.items():
        match = re.findall(pattern, text, re.IGNORECASE)
        if match:
            if attribute == "name":
                # Extract the first non-empty match and strip leading/trailing spaces
                extracted_info[attribute] = next((m.strip() for m in match[0] if m), "NA")
            else:
                extracted_info[attribute] = match[0].strip()
        else:
            extracted_info[attribute] = "NA"

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


