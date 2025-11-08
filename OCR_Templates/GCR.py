from google.cloud import vision

# Create a Vision client
client = vision.ImageAnnotatorClient()

# Load the image
with open('image_with_text.png', 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# Perform text detection
response = client.text_detection(image=image)
texts = response.text_annotations

if texts:
    print(f"Full text: {texts[0].description}")
    for text in texts[1:]: # Skip the first element which is the full text
        print(f"Detected text: {text.description}")
else:
    print("No text detected.")