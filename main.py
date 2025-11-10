import cv2
import pytesseract

# Load the image
image = cv2.imread('/Users/trystan/Documents/GitHub/number-plate-check-in/tests/test_images/example4.png')

# Convert the image to grayscale for better OCR performance
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply some image processing (e.g., thresholding) to enhance text clarity
# This step can be customized based on the image quality
_, processed_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)

# Use Tesseract to perform OCR on the processed image
extracted_text = pytesseract.image_to_string(processed_image)

# Print the extracted text
print("Extracted Text:")
print(extracted_text)

# (Optional) Display the processed image
cv2.imshow('Processed Image', processed_image)
cv2.waitKey(0)
cv2.destroyAllWindows()