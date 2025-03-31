import os
import logging
import numpy as np
from PIL import Image as Image

def crop(img:Image, w:int, h:int) -> Image:
    l:float = (img.width - w) * 0.5
    r:float = l + w
    t:float = (img.height - h) * 0.5
    b:float = t + h
    
    return img.crop((l, t, r, b))


def get_new_val(old_val, nc):
    return np.round(old_val * (nc - 1)) / (nc - 1)


# Floyd-Steinberg dither the image img into a palette with nc colours per channel.
# https://scipython.com/blog/floyd-steinberg-dithering/
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


# Simple palette reduction without dithering.
def palette_reduce(img:Image, nc:int) -> Image:
    arr = np.array(img, dtype=float) / 255
    arr = get_new_val(arr, nc)

    carr = np.array(arr/np.max(arr) * 255, dtype=np.uint8)
    return Image.fromarray(carr)


def validate_image(file_path:str) -> bool:
    try:
        img:Image = Image.open(file_path)
        img.verify()
        return True
    except (IOError, SyntaxError):
        return False
    

def procsess_image(file_path:str, dest_path:str, to_width:int, to_height:int, nc:int, del_src:bool = True) -> bool:
    try:
        img:Image = Image.open(file_path)
        w:int = img.width
        h:int = img.height
        
        # resize
        r:float = max(to_width/w, to_height/h);
        img.thumbnail((w * r, h * r), Image.Resampling.LANCZOS)
        
        # Crop
        img:Image = crop(img, to_width, to_height) 
        
        # Apply fyold steinburg dithering
        img = fs_dither(img, nc)
        
        # Reduce palette color
        img = palette_reduce(img, nc)
        
        # Save file
        img.save(dest_path)
        
        if del_src:
            os.remove(file_path)
        
        return True
        
    except IOError as error:
        logging.error(error)
        return False