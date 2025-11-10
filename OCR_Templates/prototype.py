import cv2
import pytesseract

def extract_text_from_image(image_path):
    """
    Extract text from an image using OCR.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        str: Extracted text from the image
    """
    # Load the image
    image = cv2.imread(image_path)
    
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, processed_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)
    
    # Perform OCR
    extracted_text = pytesseract.image_to_string(processed_image)
    
    # Clean up - release image from memory
    del image, gray_image, processed_image
    
    return extracted_text

def display_and_close(image_array, window_name='Processed Image'):
    """
    Display an image and wait for user to close it.
    Ensures proper cleanup of display windows.
    """
    cv2.imshow(window_name, image_array)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Extra cleanup for macOS
    cv2.waitKey(1)

# Usage
image_path = '/Users/trystan/Documents/GitHub/number-plate-check-in/tests/test_images/example1.jpg'

text = extract_text_from_image(image_path)
print("Extracted Text:")
print(text)