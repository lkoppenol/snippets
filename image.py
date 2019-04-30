"""
Author: Laurens Koppenol

### Prerequisites
1. download Poppler
    Windows: http://blog.alivate.com.au/poppler-windows/
    Linux:   https://github.com/Belval/pdf2image
2. Windows:
    extract Poppler ergens & voeg ergens/bin toe aan windows path
4. zorg dat je hoofdletter P het goed doet en voer uit in je favoriete environment:
    `pip install Pillow`
5. voer daarna deze uit in dezelfde environment
    `pip install pdf2image`
6. good to go


### Notes
- Deze module maakt gebruik van Pillow (PIL) als beeld representatie. Pillow heeft nog behoorlijk wat andere operaties die bruikbaar zijn. Meer informatie https://pillow.readthedocs.io/
- Voor meer operaties op beelden raad ik opencv aan. `pip install cv2`. Code om PIL om te zetten in opencv format staat al klaar in de module. https://opencv.org/


Minimal package to read and transform scanned PDF files for further analysis.

Uses Pillow as image representation type.

TODO: allow usage of opencv2 
> import cv2
> import numpy as np
> 
> def pil2cv(pil_image):
>     np_image = np.array(pil_image)
>     cv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR) 
>     return cv_image
> 
> 
> def cv2pil(cv_image):
>     pil_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
>     return pil_image   
"""
import os
import io
import requests

from pdf2image import convert_from_path
import PIL
import asyncio


def load(path):
    """
    Convert a PDF file to a list of images as PIL objects. Every item in the list is a single page. Single paged PDF
    files become a list of length 1.

    :param path: path to a PDF file
    :return: array of PIL objects
    """
    images = convert_from_path(path)
    return images


def rotate_clockwise(img, degrees=90):
    """
    Rotate a PIL image or list of PIL images clockwise. Default 90 degrees.

    :param img: List or single image.
    :param degrees: default 90. Multiple of 90 is recommended ;)
    :return: same format as img
    """
    if type(img) is not list:
        rotated_img = _rotate_clockwise([img], degrees)
        return rotated_img[0]
    else:
        rotated_img = _rotate_clockwise(img, degrees)
        return rotated_img

    
def _rotate_clockwise(img, degrees=90):
    # used by rotate_clockwise to rotate a list of images.
    rotated_img = [im.rotate(-degrees, expand=True) for im in img]
    return rotated_img


def save(img, path):
    """
    Save img to given path. If a list of images is presented the index of the image in the list is inserted between the
    filename and the file extension.

    :param img: List or single image.
    :param path: path including extension.
    :return: nothing
    """
    if type(img) is list:
        root, ext = os.path.splitext(path)
        for i, img in enumerate(img):
            img_path = "{}{}{}".format(root, i, ext)
            img.save(img_path)
    else:
        img.save(path)

        
def to_grayscale(img):
    """
    Make a PIL image or list of PIL images all grey and sad.
    :param img: List or single image.
    :return: grayscale images in same format
    """
    if type(img) is not list:
        gray_img = _to_grayscale([img])
        return gray_img[0]
    else:
        gray_img = _to_grayscale(img)
        return gray_img


def _to_grayscale(img):
    # Used by to_grayscale to convert list of images to grayscale.
    img = [im.convert('LA') for im in img]
    return img
    
    
def sliding_window(img, size, step):
    """
    Slide a square window over the image with steps of given size. If the window is a partial fit the window is
    discarded.

    :param img: List or single image.
    :param size:
    :param step:
    :return:
    """
    if type(img) is not list:
        windows = _sliding_window([img], size, step)
        return windows[0]
    else:
        windows = _sliding_window(img, size, step)
        return windows


def _sliding_window(img, size, step):
    # Used by sliding window to cut sliding windows from a list of PIL images.
    result = []
    for im in img:
        max_width, max_height = im.size

        crops = []
        for w in range(0, max_width-size, step):
            for h in range(0, max_height-size, step):
                bbox = (w, h, w+size, h+size)
                cropped = im.crop(box=bbox)
                crops.append(cropped)
        result.append(crops)

    return result


def resize(img, size, resampling_method):
    """
    Make a PIL image or list of PIL images all small and square.
    :param img: List or single image.
    :param size: new size = width = height
    :param resampling_method: one of IL.Image.NEAREST, -.BILINEAR, -.BICUBIC, -.LANCZOS
    :return: sized images in same format
    """
    assert resampling_method in [
        PIL.Image.NEAREST,
        PIL.Image.BILINEAR,
        PIL.Image.BICUBIC,
        PIL.Image.LANCZOS
    ]

    if type(img) is not list:
        square_img = _resize([img], size, resampling_method)
        return square_img[0]
    else:
        square_img = _resize(img, size, resampling_method)
        return square_img


def _resize(img, size, resampling_method=0):
    # used by resize to resize a list of images.
    img = [im.resize((size, size), resampling_method) for im in img]
    return img


def pyramids(img, input_sizes, target_size, resampling_method=0):
    """
    :param img: image or list of images
    :param input_sizes: list of ints = list of window sizes
    :param target_size: int of square target size
    :param resampling_method: one of IL.Image.NEAREST, -.BILINEAR, -.BICUBIC, -.LANCZOS
    """
    assert resampling_method in [
        PIL.Image.NEAREST,
        PIL.Image.BILINEAR,
        PIL.Image.BICUBIC,
        PIL.Image.LANCZOS
    ]

    if type(img) is not list:
        pyramid = _pyramids([img], input_sizes, target_size, resampling_method)
        return pyramid[0]
    else:
        pyramid = _pyramids(img, input_sizes, target_size, resampling_method)
        return pyramid


def _pyramids(img, input_sizes, target_size, resampling_method):
    # Used by pyramid to make pyramid slices of images
    result = []
    for im in img:
        sliced = []
        for input_size in input_sizes:
            step = input_size // 10 # step is 1/10th of window, floored
            crops = sliding_window(im, input_size, step)
            resized = resize(crops, target_size, resampling_method)
            sliced = sliced + resized
        result.append(sliced)
    
    return result


def query_vision_api(image):
    """
    EXCESS CALLS WILL BE TAKEN FROM YOUR SALARY
    Query Azure Vision API.

    TODO: use different API:
    OCR - https://westus.dev.cognitive.microsoft.com/docs/services/5adf991815e1060e6355ad44/operations/587f2c6a154055056008f200
    Handwriting - https://westus.dev.cognitive.microsoft.com/docs/services/5adf991815e1060e6355ad44/operations/587f2c6a154055056008f200

    :param image: single PIL image
    :param mode: either Handwritten or Printed
    """
    hex_data = _pil2hex(image)

    subscription_key = "haha nee" # STEAL MY KEY = DED IRL
    url = "https://northeurope.api.cognitive.microsoft.com/vision/v2.0/analyze"

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/octet-stream'
    }
    params = {'visualFeatures': 'Categories,Description,Color'}

    response = requests.post(
        url,
        headers=headers,
        params=params,
        data=hex_data
    )
    response.raise_for_status()

    #response_dict = response.json()
    return response


def _pil2hex(image):
    # Transform an image into hex data equal to open(file, 'rb').read()
    output = io.BytesIO()
    image.save(output, format='JPEG')
    hex_data = output.getvalue()
    return hex_data
