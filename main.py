import easyocr
import re
import cv2
import numpy as np

def preprocess_image(image_path):
    """Preprocess image for better OCR results"""
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp
    denoised = cv2.bilateralFilter(gray, 11, 17, 17)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

def clean_plate_text(text):
    """Clean and format license plate text"""
    # Remove spaces and special characters, keep only alphanumeric
    cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
    return cleaned

def is_likely_plate(text, min_length=5, max_length=8):
    """Check if text matches common license plate patterns"""
    cleaned = clean_plate_text(text)
    
    # Basic length check
    if not (min_length <= len(cleaned) <= max_length):
        return False
    
    # Should contain both letters and numbers for most plates
    has_letter = bool(re.search(r'[A-Z]', cleaned))
    has_number = bool(re.search(r'[0-9]', cleaned))
    
    return has_letter and has_number

# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Path to your image
image_path = '/Users/trystan/Documents/GitHub/number-plate-check-in/tests/test_images/example7.jpg'

# Try multiple approaches for best results
print("=" * 50)
print("METHOD 1: Original image")
print("=" * 50)
result1 = reader.readtext(
    image_path,
    allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    paragraph=False,
    width_ths=0.7,  # Adjust word grouping
    contrast_ths=0.1,  # Lower threshold for low contrast text
    adjust_contrast=0.5  # Enhance contrast
)

print("All detected text:")
print("-" * 50)
for (bbox, text, prob) in result1:
    print(f"Text: {text:15s} | Confidence: {prob:.2f}")

print("\n" + "=" * 50)
print("METHOD 2: Preprocessed image")
print("=" * 50)

# Option 1: Use preprocessed image for better results
preprocessed = preprocess_image(image_path)
result = reader.readtext(preprocessed)

# Option 2: Or use original image with adjusted parameters
# result = reader.readtext(
#     image_path,
#     allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',  # Only allow alphanumeric
#     paragraph=False,
#     min_size=20  # Ignore very small text
# )

print("All detected text:")
print("-" * 50)

plate_candidates = []

# Combine results from both methods
all_results = result1 + result

for (bbox, text, prob) in all_results:
    print(f"Text: {text:15s} | Confidence: {prob:.2f}")
    
    # Filter for likely license plates
    if is_likely_plate(text) and prob > 0.5:  # Lowered threshold for detection
        cleaned = clean_plate_text(text)
        plate_candidates.append((cleaned, prob))

print("\n" + "=" * 50)
print("Likely license plates:")
print("=" * 50)

if plate_candidates:
    # Sort by confidence
    plate_candidates.sort(key=lambda x: x[1], reverse=True)
    for plate, confidence in plate_candidates:
        print(f"Plate: {plate} | Confidence: {confidence:.2f}")
else:
    print("No license plates detected with high confidence")