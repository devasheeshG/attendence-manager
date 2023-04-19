import cv2
import numpy as np
from pytesseract import image_to_string
import os

if not os.path.exists('temp'):
    os.mkdir('temp')

def OCR(img: str):
    
    # Open image
    img = cv2.imread(img)

    # Convert to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Create a mask
    mask = np.all(img == np.array([35, 63, 89]), axis=-1)
    img[mask] = [0, 0, 0]   # BLACK
    img[~mask] = [255, 255, 255]    # WHITE

    # Convert to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Add padding
    pad_size = 5
    img = cv2.copyMakeBorder(
        img, pad_size, pad_size, pad_size, pad_size, cv2.BORDER_CONSTANT, value=(255, 255, 255))

    # OCR
    options = "--psm 8 -c tessedit_char_whitelist=0123456789"
    res = image_to_string(img, config=options)
    return res.strip()

if __name__ == "__main__":
    # Load image
    img = cv2.imread(r"capchas/740487.png")

    # OCR
    res = OCR(img)
    print(res)