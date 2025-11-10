import easyocr
import re
import cv2
import numpy as np
import csv
from datetime import datetime
import os

def preprocess_image(image_path):
    """Preprocess image for better OCR results"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.bilateralFilter(gray, 11, 17, 17)
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    return thresh

def clean_plate_text(text):
    """Clean and format license plate text"""
    cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
    return cleaned

def is_likely_plate(text, min_length=5, max_length=8):
    """Check if text matches common license plate patterns"""
    cleaned = clean_plate_text(text)
    if not (min_length <= len(cleaned) <= max_length):
        return False
    has_letter = bool(re.search(r'[A-Z]', cleaned))
    has_number = bool(re.search(r'[0-9]', cleaned))
    return has_letter and has_number

def append_to_csv(plate_text, csv_path):
    """Append detected plate and timestamp to CSV"""
    # Create timestamp in format: YYYY-MM-DD HH:MM
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Create data directory if missing
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    # Check if file exists
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write header if file is new
        if not file_exists:
            writer.writerow(["License Plate", "Timestamp"])
        writer.writerow([plate_text, timestamp])

    print(f"[+] Recorded plate: {plate_text} at {timestamp}")

# MAIN

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Path to test image
image_path = '/Users/trystan/Documents/GitHub/number-plate-check-in/tests/test_images/example3.webp'

# Path to output CSV
csv_path = '/Users/trystan/Documents/GitHub/number-plate-check-in/data/data.csv'

# Read with OCR
print("=" * 50)
print("METHOD 1: Original image")
print("=" * 50)
result1 = reader.readtext(
    image_path,
    allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    paragraph=False,
    width_ths=0.7,
    contrast_ths=0.1,
    adjust_contrast=0.5
)

# Preprocessed version
print("\n" + "=" * 50)
print("METHOD 2: Preprocessed image")
print("=" * 50)
preprocessed = preprocess_image(image_path)
result2 = reader.readtext(preprocessed)

# Combine both
all_results = result1 + result2

plate_candidates = []

for (bbox, text, prob) in all_results:
    cleaned = clean_plate_text(text)
    if is_likely_plate(cleaned) and prob > 0.5:
        plate_candidates.append((cleaned, prob))

# Sort by confidence
plate_candidates.sort(key=lambda x: x[1], reverse=True)

print("\n" + "=" * 50)
print("Likely license plates:")
print("=" * 50)

if plate_candidates:
    for plate, confidence in plate_candidates:
        print(f"Plate: {plate} | Confidence: {confidence:.2f}")
        append_to_csv(plate, csv_path)
else:
    print("No license plates detected with high confidence")
