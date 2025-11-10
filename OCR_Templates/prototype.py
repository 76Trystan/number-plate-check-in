import cv2
import pytesseract
import numpy as np

def extract_text_from_image(image_path, show_steps=False):
    """
    Extract text from an image using OCR optimized for license plates.
    
    Args:
        image_path: Path to the image file
        show_steps: If True, display intermediate processing steps
        
    Returns:
        tuple: (extracted_text, processed_image)
    """
    # Load the image
    image = cv2.imread(image_path)
    
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    print(f"Image loaded: {image.shape}")
    
    if show_steps:
        display_and_close(image, 'Original Image')
    
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    if show_steps:
        display_and_close(gray_image, 'Grayscale')
    
    # Apply threshold to get binary image
    _, binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    if show_steps:
        display_and_close(binary, 'Binary (for contour detection)')
    
    # Find contours to locate text regions
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the largest contour (likely the main plate text)
    if contours:
        # Sort contours by area
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # Get bounding boxes and filter by size
        bounding_boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / float(h) if h > 0 else 0
            
            # Filter: reasonable size and aspect ratio for license plate text
            if area > 500 and 1.5 < aspect_ratio < 10:  # License plates are wide
                bounding_boxes.append((x, y, w, h, area))
        
        if bounding_boxes:
            # Take the largest qualifying box
            bounding_boxes.sort(key=lambda b: b[4], reverse=True)
            x, y, w, h, _ = bounding_boxes[0]
            
            # Add some padding
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(gray_image.shape[1] - x, w + 2 * padding)
            h = min(gray_image.shape[0] - y, h + 2 * padding)
            
            # Crop to the license plate region
            cropped = gray_image[y:y+h, x:x+w]
            
            if show_steps:
                # Draw rectangle on original for visualization
                visual = image.copy()
                cv2.rectangle(visual, (x, y), (x+w, y+h), (0, 255, 0), 2)
                display_and_close(visual, 'Detected Plate Region')
                display_and_close(cropped, 'Cropped Plate')
            
            # Use the cropped region for OCR
            gray_to_process = cropped
        else:
            print("No suitable contours found, using full image")
            gray_to_process = gray_image
    else:
        print("No contours found, using full image")
        gray_to_process = gray_image
    
    # Resize for better OCR
    scale_percent = 300  # Enlarge by 300%
    width = int(gray_to_process.shape[1] * scale_percent / 100)
    height = int(gray_to_process.shape[0] * scale_percent / 100)
    resized = cv2.resize(gray_to_process, (width, height), interpolation=cv2.INTER_CUBIC)
    
    if show_steps:
        display_and_close(resized, 'Resized (3x)')
    
    # Apply threshold
    _, processed_image = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    if show_steps:
        display_and_close(processed_image, 'Final Threshold')
    
    # Perform OCR with license plate config
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '
    extracted_text = pytesseract.image_to_string(processed_image, config=custom_config)
    
    # Clean up intermediate images from memory
    del image, gray_image, binary, resized
    
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
image_path = '/Users/trystan/Documents/GitHub/number-plate-check-in/tests/test_images/example3.webp'

# Set show_steps=True to see each processing step
text, processed_image = extract_text_from_image(image_path, show_steps=True)

print("\n" + "="*50)
print("Extracted Text:")
print("="*50)
print(text.strip())
print("="*50)

# Display the final processed image
display_and_close(processed_image, 'Final Processed Image')

# Clean up processed image after display
del processed_image