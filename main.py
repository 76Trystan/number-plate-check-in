import cv2
import pytesseract

def extract_text_from_image(image_path):
    """
    Extract text from an image using OCR.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        tuple: (extracted_text, processed_image)
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
    
    # Clean up intermediate images from memory
    del image, gray_image
    
    return extracted_text, processed_image

def display_and_close(image_array, window_name='Processed Image'):
    """
    Display an image and wait for user to close it.
    Ensures proper cleanup of display windows.
    """
    cv2.imshow(window_name, image_array)
    print(f"\nDisplaying '{window_name}' - Press any key in the image window to close it")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Extra cleanup for macOS
    cv2.waitKey(1)

# Usage
image_path = '/Users/trystan/Documents/GitHub/number-plate-check-in/tests/test_images/example1.jpg'

text, processed_image = extract_text_from_image(image_path)
print("Extracted Text:")
print(text)

# Display the processed image
display_and_close(processed_image, 'Processed Image')

# Clean up processed image after display
del processed_image