import cv2
import pytesseract
import numpy as np

def detect_license_plate(image, show_steps=False):
    """
    Detect the license plate region in an image.
    
    Args:
        image: Input image (BGR)
        show_steps: If True, display detection steps
        
    Returns:
        cropped plate region or None if not found
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)
    
    if show_steps:
        display_and_close(filtered, 'Step 1: Bilateral Filter')
    
    # Edge detection
    edged = cv2.Canny(filtered, 30, 200)
    
    if show_steps:
        display_and_close(edged, 'Step 2: Edge Detection')
    
    # Find contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]  # Top 30 largest
    
    plate_contour = None
    plate_candidates = []
    
    # Look for rectangular contours with appropriate aspect ratio
    for contour in contours:
        # Approximate the contour
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.018 * perimeter, True)
        
        # License plates are typically rectangular (4 corners)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            area = w * h
            
            # License plate characteristics:
            # - Aspect ratio typically between 2:1 and 5:1 (wider than tall)
            # - Reasonable size (not too small)
            # - Not too thin or too wide
            if 1.5 < aspect_ratio < 6 and area > 1000:
                plate_candidates.append({
                    'contour': approx,
                    'bbox': (x, y, w, h),
                    'area': area,
                    'aspect_ratio': aspect_ratio
                })
    
    if show_steps and plate_candidates:
        visual = image.copy()
        for i, candidate in enumerate(plate_candidates[:5]):  # Show top 5
            x, y, w, h = candidate['bbox']
            cv2.rectangle(visual, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(visual, f"#{i+1}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        display_and_close(visual, 'Step 3: Plate Candidates')
    
    if plate_candidates:
        # Sort by area and take the largest reasonable one
        plate_candidates.sort(key=lambda c: c['area'], reverse=True)
        
        # Try each candidate and see if it contains text
        for candidate in plate_candidates[:3]:  # Check top 3
            x, y, w, h = candidate['bbox']
            
            # Add padding
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(gray.shape[1] - x, w + 2 * padding)
            h = min(gray.shape[0] - y, h + 2 * padding)
            
            # Crop the plate region
            plate_crop = gray[y:y+h, x:x+w]
            
            # Quick OCR test to see if this region contains text
            test_text = pytesseract.image_to_string(plate_crop, config=r'--psm 7').strip()
            
            # If we find alphanumeric characters, this is likely the plate
            if any(c.isalnum() for c in test_text):
                if show_steps:
                    visual = image.copy()
                    cv2.rectangle(visual, (x, y), (x+w, y+h), (0, 255, 0), 3)
                    display_and_close(visual, 'Step 4: Selected Plate Region')
                
                return plate_crop, (x, y, w, h)
        
        # If no text found, just return the largest candidate
        x, y, w, h = plate_candidates[0]['bbox']
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(gray.shape[1] - x, w + 2 * padding)
        h = min(gray.shape[0] - y, h + 2 * padding)
        
        plate_crop = gray[y:y+h, x:x+w]
        return plate_crop, (x, y, w, h)
    
    return None, None

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
    
    # Try to detect the license plate region
    plate_region, bbox = detect_license_plate(image, show_steps=show_steps)
    
    # If detection failed, fall back to full image
    if plate_region is None:
        print("License plate detection failed, using full image")
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cropped = gray_image
    else:
        print(f"License plate detected at: {bbox}")
        cropped = plate_region
        
        if show_steps:
            display_and_close(cropped, 'Detected Plate (Cropped)')
    
    # Resize for better OCR
    scale_percent = 300
    width = int(cropped.shape[1] * scale_percent / 100)
    height = int(cropped.shape[0] * scale_percent / 100)
    resized = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_CUBIC)
    
    if show_steps:
        display_and_close(resized, 'Resized (3x)')
    
    # Try multiple processing approaches
    results = {}
    
    # Approach 1: Otsu threshold
    _, thresh1 = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if show_steps:
        display_and_close(thresh1, 'Approach 1: Otsu')
    
    config1 = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '
    text1 = pytesseract.image_to_string(thresh1, config=config1).strip()
    results['Otsu + PSM7'] = text1
    print(f"Approach 1 (Otsu): '{text1}'")
    
    # Approach 2: Inverted Otsu
    _, thresh2 = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if show_steps:
        display_and_close(thresh2, 'Approach 2: Inverted Otsu')
    
    text2 = pytesseract.image_to_string(thresh2, config=config1).strip()
    results['Inverted Otsu + PSM7'] = text2
    print(f"Approach 2 (Inverted): '{text2}'")
    
    # Approach 3: Adaptive threshold
    adaptive = cv2.adaptiveThreshold(resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
    if show_steps:
        display_and_close(adaptive, 'Approach 3: Adaptive')
    
    text3 = pytesseract.image_to_string(adaptive, config=config1).strip()
    results['Adaptive + PSM7'] = text3
    print(f"Approach 3 (Adaptive): '{text3}'")
    
    # Approach 4: PSM 6 (block of text)
    config2 = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '
    text4 = pytesseract.image_to_string(thresh1, config=config2).strip()
    results['Otsu + PSM6'] = text4
    print(f"Approach 4 (PSM6): '{text4}'")
    
    # Approach 5: No whitelist (sometimes special characters help)
    config3 = r'--oem 3 --psm 7'
    text5 = pytesseract.image_to_string(thresh1, config=config3).strip()
    results['Otsu + No Whitelist'] = text5
    print(f"Approach 5 (No Whitelist): '{text5}'")
    
    # Find best result
    best_text = ""
    best_approach = ""
    for approach, text in results.items():
        if len(text) > len(best_text) and any(c.isalnum() for c in text):
            best_text = text
            best_approach = approach
    
    print(f"\nBest result: {best_approach} = '{best_text}'")
    
    processed_image = thresh1
    extracted_text = best_text
    
    # Clean up
    del image, resized, thresh1, thresh2, adaptive
    
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
print("Final Extracted Text:")
print("="*50)
print(text)
print("="*50)

# Display the final processed image
display_and_close(processed_image, 'Final Processed Image')

# Clean up processed image after display
del processed_image