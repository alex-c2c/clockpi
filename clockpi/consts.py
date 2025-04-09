from enum import Enum

# Redis
CHANNEL_CLOCKPI: str = "clockpi"
CHANNEL_EPDPI: str = "epdpi"
MSG_CLEAR: str = "clear"
MSG_DRAW: str = "draw"
MSG_BUSY: str = "busy"
MSG_UPDATED: str = "updated"
MSG_RESULT: str = "result"

MSG_BTN: str = "button"
MSG_BTN_NEXT: str = "next"
MSG_BTN_PREV: str = "prev"
MSG_BTN_CHANGE: str = "change"
MSG_BTN_ONOFF: str = "on_off"

# Settings Key
SETTINGS_EPD_BUSY: str = "epd_busy"
SETTINGS_IMAGE_ID: str = "image_id"
SETTINGS_MODE: str = "mode"
SETTINGS_COLOR: str = "color"
SETTINGS_SHADOW: str = "shadow"
SETTINGS_DRAW_GRIDS: str = "draw_grids"

# E-Paper Display Width
EPD_WIDTH: int = 800

# E-Paper Display Height
EPD_HEIGHT: int = 480

# E-Paper Display color per channel
EPD_NC: int = 2

# Allowed upload file extensions
ALLOWED_EXTENSIONS: set[str] = ("png", "jpg", "jpeg", "bmp")

# Colors
COLOR_NONE: int = 0
COLOR_BLACK: int = 1
COLOR_WHITE: int = 2
COLOR_YELLOW: int = 3
COLOR_RED: int = 4
COLOR_BLUE: int = 5
COLOR_GREEN: int = 6

# Time Mode
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
    SECT_9_BOTTOM_RIGHT = 9
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
    FULL_1 = 20  # Small
    FULL_2 = 21  # Medium
    FULL_3 = 22  # Large
    MAX = FULL_3 + 1

# Exceptions
ERR_UPLOAD_NO_FILE = -1
ERR_UPLOAD_INVALID_EXT = -2
ERR_UPLOAD_INVALID_IMAGE = -3
ERR_UPLOAD_POST_PROC = -4
ERR_UPLOAD_HASH = -5
ERR_UPLOAD_COPY = -6
ERR_UPLOAD_SAVE = -7