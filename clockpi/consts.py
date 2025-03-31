from curses import COLOR_BLACK
import os, sys
from enum import Enum

EPD_NC:int = 2 # colors per channel

DIR_UPLOAD:str = "upload"
DIR_PROCESSED:str = "processed"
DIR_FONT:str = "font"

COLOR_BLACK:int = 0
COLOR_WHITE:int = 1
COLOR_YELLOW:int = 2
COLOR_RED:int = 3
COLOR_BLUE:int = 4
COLOR_GREEN:int = 5

ALLOWED_EXTENSIONS : set[str] = ('png', 'jpg', 'jpeg', 'bmp')

