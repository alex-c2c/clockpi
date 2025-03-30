import os, sys
from enum import Enum

EPD_WIDTH:int = 800 # pixel count of the Waveshare E-paper display 7"3e
EPD_HEIGHT:int = 480 # pixel count of the Waveshare E-paper display 7"3e
EPD_NC:int = 2 # colors per channel

DIR_UPLOAD:str = "upload"
DIR_PROCESSED:str = "processed"
DIR_FONT:str = "font"
    
ALLOWED_EXTENSIONS : set[str] = ('png', 'jpg', 'jpeg', 'bmp')

