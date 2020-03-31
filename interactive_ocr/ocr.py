from PIL import Image
import pytesseract
import cv2
import numpy
import os

_base = os.path.dirname(os.path.realpath(__file__))
pytesseract.pytesseract.tesseract_cmd = f'{_base}/tesseract-Win64/tesseract.exe'


def image_to_string(img):
    return pytesseract.image_to_string(img)


def read_image(img):
    # Post Processing
    cv_img = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # debug save
    cv2.imwrite('tmp/tmp.png', gray)

    # OCR
    img = Image.fromarray(gray)
    return image_to_string(img)
