#!/usr/bin/python
# -*- coding:utf-8 -*-

from itertools import product
import sys
import os
import logging
import time
import traceback
import datetime

DIR_IMG:str = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'img')
DIR_LIB:str = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(DIR_LIB):
    sys.path.append(DIR_LIB)

from PIL import Image, ImageDraw, ImageFont, ImagePalette
import numpy as np
#from waveshare_epd import epd7in3e

logging.basicConfig(level=logging.DEBUG)


def crop(img:Image) -> Image:
    left:float = (img.width - 800) * 0.5
    right:float = left + 800
    top:float = (img.height - 480) * 0.5
    bottom:float = top + 480
    
    return img.crop((left, top, right, bottom))


def get_new_val(old_val, nc):
    return np.round(old_val * (nc - 1)) / (nc - 1)


# Floyd-Steinberg dither the image img into a palette with nc colours per channel.
def fs_dither(img:Image, nc:int) -> Image:

    h:int = img.height
    w:int = img.width
    arr = np.array(img, dtype=float) / 255

    for ir in range(h):
        for ic in range(w):
            # NB need to copy here for RGB arrays otherwise err will be (0,0,0)!
            old_val = arr[ir, ic].copy()
            new_val = get_new_val(old_val, nc)
            arr[ir, ic] = new_val
            err = old_val - new_val
            # In this simple example, we will just ignore the border pixels.
            if ic < w - 1:
                arr[ir, ic+1] += err * 7/16
            if ir < h - 1:
                if ic > 0:
                    arr[ir+1, ic-1] += err * 3/16
                arr[ir+1, ic] += err * 5/16
                if ic < w - 1:
                    arr[ir+1, ic+1] += err / 16

    carr = np.array(arr/np.max(arr, axis=(0,1)) * 255, dtype=np.uint8)
    return Image.fromarray(carr)


def palette_reduce(img:Image, nc:int) -> Image:
    """Simple palette reduction without dithering."""
    arr = np.array(img, dtype=float) / 255
    arr = get_new_val(arr, nc)

    carr = np.array(arr/np.max(arr) * 255, dtype=np.uint8)
    return Image.fromarray(carr)


def main(file_path:str) -> None:
    try:
        img = Image.open(file_path)
        nc:int = 2 # number or color components
        
        # resize
        ratio:float = max(800/img.width, 480/img.height);
        img.thumbnail((img.width*ratio, img.height*ratio), Image.Resampling.LANCZOS)
        
        # Crop
        img:Image = crop(img) 
        
        img = fs_dither(img, 2)
        img = palette_reduce(img, 2)
        #img.show()
        
        path_list:list[str] = os.path.splitext(file_path)
        out_path:str = path_list[0] + "_small" + path_list[-1]
        img.save(out_path, "jpg")
        
    except IOError as error:
        logging.error(error)
        

if __name__ == "__main__":
    file_path:str = sys.argv[1]
    main(file_path)
