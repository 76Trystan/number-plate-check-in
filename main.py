import cv2
import pytesseract

def extract_text_from_image(image_path, show_steps=False):
    """
    Extract text from an image using OCR with preprocessing.
    
    Args:
        image_path: Path to the image file
        show_steps: If True, display intermediate processing steps
        
    Returns:
        str: Extracted text from the image
    """
    print("Loading image...")
    # Load the image
    image = cv2.imread(image_path)
    
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    print("Image loaded successfully")
    
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print("Converted to grayscale")
    
    # Blur to reduce noise (bilateral filter preserves edges)
    print("Applying bilateral filter...")
    blurred = cv2.bilateralFilter(gray_image, 11, 17, 17)
    
    if show_steps:
        cv2.imshow("Original Grayscale", gray_image)
        cv2.imshow("Bilateral Filter", blurred)
    
    # Perform edge detection
    print("Detecting edges...")
    edged = cv2.Canny(blurred, 170, 200)
    
    if show_steps:
        cv2.imshow("Canny Edges", edged)
    
    # Apply thresholding for OCR
    print("Applying threshold...")
    _, processed_image = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)
    
    if show_steps:
        cv2.imshow("Thresholded", processed_image)
        print("\n*** Press ANY KEY in the image windows to continue ***\n")
    
    # Perform OCR before releasing images
    print("Running OCR...")
    extracted_text = pytesseract.image_to_string(processed_image)
    print("OCR complete")
    
    # Show windows if requested, then clean up
    if show_steps:
        cv2.waitKey(0)  # This waits for you to press a key!
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # Extra cleanup for macOS
    
    # Clean up - release images from memory
    del image, gray_image, blurred, edged, processed_image
    
    return extracted_text

# Usage
image_path = '/Users/trystan/Documents/GitHub/number-plate-check-in/tests/test_images/example4.png'

# Extract text and show processing steps
print("Processing image...")
text = extract_text_from_image(image_path, show_steps=True)

# Print the extracted text to terminal
print("\n" + "="*50)
print("EXTRACTED TEXT:")
print("="*50)
print(text)
print("="*50)

# Also print cleaned version (strip whitespace)
cleaned_text = text.strip()
if cleaned_text:
    print(f"\nCleaned text: '{cleaned_text}'")
else:
    print("\nNo text detected in image")