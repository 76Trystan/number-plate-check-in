import easyocr
import re
import cv2
import numpy as np
import csv
from datetime import datetime
import os

def preprocess_frame(frame):
    """Preprocess frame for better OCR results"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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

def auto_save_if_confident(plate, confidence, csv_path, recent_saves, saved_count):
    """Automatically save plate if confidence is above 0.4"""
    if confidence > 0.4 and plate not in recent_saves:
        append_to_csv(plate, csv_path)
        saved_count += 1
        recent_saves.add(plate)
        
        # Clear recent saves after 10 plates to allow re-detection
        if len(recent_saves) > 10:
            recent_saves.clear()
        
        print(f"\n✓ AUTO-SAVED: {plate} (Confidence: {confidence:.2f})")
        return saved_count
    return saved_count

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

# MAIN - LIVE WEBCAM VERSION

# Initialize EasyOCR reader
print("Initializing OCR reader...")
reader = easyocr.Reader(['en'], gpu=False)
print("OCR reader ready!")

# Path to output CSV
csv_path = '/Users/trystan/Documents/GitHub/number-plate-check-in/dashboard/public/data/data.csv' # Path to output CSV for local use only

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("\n" + "="*50)
print("LIVE LICENSE PLATE DETECTION")
print("="*50)
print("Press 'q' to quit")
print("Press 's' to manually save current detection")
print("Press 'p' to pause/unpause processing")
print("Auto-save enabled for confidence > 0.4")
print("="*50)
print(f"Saving detections to: {csv_path}")
print("="*50 + "\n")

frame_count = 0
process_every_n_frames = 5  # Process every 5th frame for performance
last_detected_plates = []
paused = False
saved_count = 0
recent_saves = set()  # Track recently saved plates to avoid duplicates

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
        print("\n" + "=" * 50)
        print(f"Processing frame {frame_count}...")
        print("=" * 50)
        
        # METHOD 1: Original frame
        result1 = reader.readtext(
            frame,
            allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            paragraph=False,
            width_ths=0.7,
            contrast_ths=0.1,
            adjust_contrast=0.5
        )
        
        # METHOD 2: Preprocessed frame
        preprocessed = preprocess_frame(frame)
        result2 = reader.readtext(preprocessed)
        
        # Combine both results
        all_results = result1 + result2
        
        plate_candidates = []
        
        for (bbox, text, prob) in all_results:
            cleaned = clean_plate_text(text)
            if is_likely_plate(cleaned) and prob > 0.5:
                plate_candidates.append((cleaned, prob, bbox))
        
        # Sort by confidence
        plate_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Store detected plates
        last_detected_plates = plate_candidates[:3]  # Keep top 3
        
        # Display detected plates
        if plate_candidates:
            print("Likely license plates:")
            for i, (plate, confidence, bbox) in enumerate(plate_candidates[:3]):
                print(f"  {i+1}. Plate: {plate} | Confidence: {confidence:.2f}")
                
                # Auto-save if confidence > 0.4 (only top result)
                if i == 0:
                    saved_count = auto_save_if_confident(plate, confidence, csv_path, recent_saves, saved_count)
                    
                    # Draw bounding box for top result
                    pts = np.array(bbox, dtype=np.int32)
                    cv2.polylines(display_frame, [pts], True, (0, 255, 0), 3)
        else:
            print("No license plates detected with high confidence")
    
    # Display detected plates on screen
    y_offset = 70
    for i, (plate, confidence, bbox) in enumerate(last_detected_plates):
        color = (0, 255, 0) if i == 0 else (255, 255, 0)
        cv2.putText(display_frame, f"{i+1}. {plate} ({confidence:.2f})", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        y_offset += 35
    
    # Display saved count
    cv2.putText(display_frame, f"Saved: {saved_count}", (10, display_frame.shape[0] - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    
    # Show the frame
    cv2.imshow('License Plate Detection', display_frame)
    
    # Handle key presses
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('s') and last_detected_plates:
        # Save the top detection
        top_plate, top_confidence, _ = last_detected_plates[0]
        
        # Avoid saving the same plate multiple times in quick succession
        if top_plate not in recent_saves:
            append_to_csv(top_plate, csv_path)
            saved_count += 1
            recent_saves.add(top_plate)
            
            # Clear recent saves after 10 plates to allow re-detection
            if len(recent_saves) > 10:
                recent_saves.clear()
            
            print(f"\n SAVED TO CSV: {top_plate} (Confidence: {top_confidence:.2f})")
        else:
            print(f"\n Plate {top_plate} was recently saved, skipping duplicate")
            
    elif key == ord('p'):
        paused = not paused
        print("\n" + ("="*50))
        print("PAUSED" if paused else "RESUMED")
        print("="*50)
    
    frame_count += 1

# Cleanup
cap.release()
cv2.destroyAllWindows()

print("\n" + "="*50)
print(f"Session complete. Total plates saved: {saved_count}")
print(f"Data saved to: {csv_path}")
print("="*50)