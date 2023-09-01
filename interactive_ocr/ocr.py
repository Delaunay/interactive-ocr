import os

from PIL import Image
import pytesseract

import cv2
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")

import numpy

_base = os.path.dirname(os.path.realpath(__file__))
pytesseract.pytesseract.tesseract_cmd = f'/usr/bin/tesseract'


def image_to_string(img):
    return pytesseract.image_to_string(img, lang='eng')


def read_image(img):
    # Post Processing
    cv_img = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)

    # up scale the image to help pytesseract
    scale_percent = 600
    width = int(cv_img.shape[1] * scale_percent / 100)
    height = int(cv_img.shape[0] * scale_percent / 100)
    dim = (width, height)

    cv_img = cv2.resize(cv_img, dim, cv2.INTER_LINEAR)

    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # debug save
    cv2.imwrite('tmp/tmp.png', gray)

    # OCR
    img = Image.fromarray(gray)
    return image_to_string(img)
