import os
import tempfile

from enum import Enum


"""
SLEEP STATUS
"""
class SleepStatus(Enum):
	AWAKE = "AWAKE"
	SLEEP = "SLEEP"

"""
REDIS CONSTS
"""
#R_CH_SUB: str = "clockpi"
#R_CH_PUB: str = "epdpi"
R_CH_DRAW: str = "epdpi_draw"
R_CH_CLEAR: str = "epdpi_clear"

#R_MSG_CLEAR: str = "clear"
#R_MSG_DRAW: str = "draw"
#R_MSG_BUSY: str = "busy"
#R_MSG_UPDATED: str = "updated"
#R_MSG_RESULT: str = "result"

#R_IMAGE_QUEUE: str = "img_queue"
R_SLEEP_STATUS: str = "sleep_status"

#R_SETTINGS_EPD_BUSY: str = "epd_busy"
#R_SETTINGS_DRAW_GRIDS: str = "draw_grids"


"""
ERROR CODES
"""
# Exceptions - Auth (100)

# Exceptions - EPD (200)

# Exceptions - Main (300)

# Exceptions - Queue (400)
ERR_QUEUE_INVALID_ID = -401
ERR_QUEUE_TOO_SHORT = -402
ERR_QUEUE_DUPLICATE_ID = -403

# Exceptions Sleep (500)
ERR_SLEEP_INVALID_DATA = -501
ERR_SLEEP_INVALID_ID = -502

# Exceptions - Wallpaper (600)
ERR_UPLOAD_NO_FILE = -601
ERR_UPLOAD_INVALID_EXT = -602
ERR_UPLOAD_INVALID_IMAGE = -603
ERR_UPLOAD_POST_PROC = -604
ERR_UPLOAD_HASH = -605
ERR_UPLOAD_COPY = -606
ERR_UPLOAD_SAVE = -607
ERR_WALLPAPER_INVALID_PARAMS = -608
ERR_WALLPAPER_INVALID_ID = -609


"""
DIRECTORIES
"""
DIR_APP_UPLOAD: str = os.path.join(os.path.dirname(__file__), "..", "upload")
DIR_FONT: str = os.path.join(os.path.dirname(__file__), "..", "font")
DIR_TMP_UPLOAD: str = os.path.join(tempfile.gettempdir(), "upload")
DIR_TMP_PROCESSED: str = os.path.join(tempfile.gettempdir(), "processed")
