import pytesseract
from PIL import Image

# Set the path to the Tesseract executable (if not in PATH)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Open the image
img = Image.open('image_with_text.png')

# Perform OCR
text = pytesseract.image_to_string(img)

print(text)