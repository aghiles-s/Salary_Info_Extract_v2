import pytesseract

def apply_ocr(images):
    return [pytesseract.image_to_string(img) for img in images]