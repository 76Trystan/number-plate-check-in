import easyocr
import re
import cv2
import numpy as np
from datetime import datetime

def clean_plate_text(text):
    """Clean and format license plate text"""
    cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
    return cleaned

def is_likely_plate(text, min_length=4, max_length=9):
    """Check if text matches common license plate patterns"""
    cleaned = clean_plate_text(text)
    
    if not (min_length <= len(cleaned) <= max_length):
        return False
    
    has_letter = bool(re.search(r'[A-Z]', cleaned))
    has_number = bool(re.search(r'[0-9]', cleaned))
    
    return has_letter and has_number

def preprocess_frame(frame):
    """Preprocess frame for better OCR"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Sharpen the image
    kernel = np.array([[-1,-1,-1],
                       [-1, 9,-1],
                       [-1,-1,-1]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(sharpened)
    
    return enhanced

# Initialize the OCR reader
print("Initializing OCR reader...")
reader = easyocr.Reader(['en'], gpu=False)
print("OCR reader ready!")

# Open webcam (0 is usually the default webcam)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

# Set camera properties for better performance
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("\n" + "="*50)
print("LIVE LICENSE PLATE DETECTION")
print("="*50)
print("Press 'q' to quit")
print("Press 's' to save current detection")
print("Press 'p' to pause/unpause processing")
print("="*50 + "\n")

frame_count = 0
process_every_n_frames = 3  # Process every 3rd frame for performance
last_detected_plate = ""
paused = False
saved_plates = []

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Could not read frame")
        break
    
    # Create a copy for display
    display_frame = frame.copy()
    
    # Add status text
    status = "PAUSED" if paused else "DETECTING..."
    cv2.putText(display_frame, status, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if not paused else (0, 0, 255), 2)
    
    # Process frame for OCR (not every frame for performance)
    if not paused and frame_count % process_every_n_frames == 0:
        # Preprocess for better OCR
        processed = preprocess_frame(frame)
        
        # Run OCR
        results = reader.readtext(processed, 
                                 allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                                 paragraph=False)
        
        # Look for license plates
        best_plate = None
        best_confidence = 0
        
        for (bbox, text, prob) in results:
            if is_likely_plate(text) and prob > 0.3:
                cleaned = clean_plate_text(text)
                if prob > best_confidence:
                    best_plate = cleaned
                    best_confidence = prob
                    best_bbox = bbox
        
        # Display detected plate
        if best_plate:
            last_detected_plate = best_plate
            
            # Draw bounding box
            pts = np.array(best_bbox, dtype=np.int32)
            cv2.polylines(display_frame, [pts], True, (0, 255, 0), 3)
            
            # Display plate text
            cv2.putText(display_frame, f"PLATE: {best_plate}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            cv2.putText(display_frame, f"Confidence: {best_confidence:.2f}", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            print(f"Detected: {best_plate} (Confidence: {best_confidence:.2f})")
    
    # Show last detected plate even when not processing
    elif last_detected_plate:
        cv2.putText(display_frame, f"Last: {last_detected_plate}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    
    # Display saved plates count
    if saved_plates:
        cv2.putText(display_frame, f"Saved: {len(saved_plates)}", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    
    # Show the frame
    cv2.imshow('License Plate Detection', display_frame)
    
    # Handle key presses
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('s') and last_detected_plate:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        saved_plates.append((last_detected_plate, timestamp))
        print(f"✓ Saved: {last_detected_plate} at {timestamp}")
    elif key == ord('p'):
        paused = not paused
        print("PAUSED" if paused else "RESUMED")
    
    frame_count += 1

# Cleanup
cap.release()
cv2.destroyAllWindows()

# Print saved plates
if saved_plates:
    print("\n" + "="*50)
    print("SAVED LICENSE PLATES")
    print("="*50)
    for plate, timestamp in saved_plates:
        print(f"{timestamp} - {plate}")
else:
    print("\nNo plates saved.")