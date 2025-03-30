import os, sys

EPD_WIDTH:int = 800 # pixel count of the Waveshare E-paper display 7"3e
EPD_HEIGHT:int = 480 # pixel count of the Waveshare E-paper display 7"3e
EPD_NC:int = 2 # colors per channel

DIR_UPLOAD:str = "upload"
DIR_PROCESSED:str = "processed"
#DIR_UPLOAD:str = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'upload')
DIR_IMG:str = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'img')
DIR_LIB:str = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(DIR_LIB):
    sys.path.append(DIR_LIB)
    
ALLOWED_EXTENSIONS : set[str] = ('png', 'jpg', 'jpeg', 'bmp')
