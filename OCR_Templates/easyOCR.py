import easyocr

# Initialize the OCR reader with desired languages
reader = easyocr.Reader(['en']) # 'en' for English

# Read text from an image file
result = reader.readtext('image_with_text.png')

# Print the extracted text and its bounding box
for (bbox, text, prob) in result:
    print(f"Text: {text}, Confidence: {prob:.2f}")