import os
import tempfile
from enum import Enum

# E-Paper Display Width
EPD_WIDTH:int = 800

# E-Paper Display Height
EPD_HEIGHT:int = 480

# E-Paper Display color per channel
EPD_NC:int = 2

# Allowed upload file extensions
ALLOWED_EXTENSIONS : set[str] = ('png', 'jpg', 'jpeg', 'bmp')

# Colors
COLOR_NONE:int = 0
COLOR_BLACK:int = 1
COLOR_WHITE:int = 2
COLOR_YELLOW:int = 3
COLOR_RED:int = 4
COLOR_BLUE:int = 5
COLOR_GREEN:int = 6

class TimeMode(Enum):
    OFF = 0
    SECT_9_TOP_LEFT = 1
    SECT_9_TOP_CENTER = 2
    SECT_9_TOP_RIGHT = 3
    SECT_9_MIDDLE_LEFT = 4
    SECT_9_MIDDLE_CENTER = 5
    SECT_9_MIDDLE_RIGHT = 6
    SECT_9_BOTTOM_LEFT = 7
    SECT_9_BOTTOM_CENTER = 8
    SECT_9_BOTTOM_RIGHT= 9
    SECT_6_TOP_LEFT = 10
    SECT_6_TOP_RIGHT = 11
    SECT_6_MIDDLE_LEFT = 12
    SECT_6_MIDDLE_RIGHT = 13
    SECT_6_BOTTOM_LEFT = 14
    SECT_6_BOTTOM_RIGHT = 15
    SECT_4_TOP_LEFT = 16
    SECT_4_TOP_RIGHT = 17
    SECT_4_BOTTOM_LEFT = 18
    SECT_4_BOTTOM_RIGHT = 19
    FULL_1 = 20 # Small
    FULL_2 = 21 # Medium
    FULL_3 = 22 # Large
    MAX = FULL_3 + 1