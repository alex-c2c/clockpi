from enum import Enum

# Redis
R_CHANNEL_CLOCKPI: str = "clockpi"
R_CHANNEL_EPDPI: str = "epdpi"

R_MSG_CLEAR: str = "clear"
R_MSG_DRAW: str = "draw"
R_MSG_BUSY: str = "busy"
R_MSG_UPDATED: str = "updated"
R_MSG_RESULT: str = "result"
R_MSG_BTN: str = "button"
R_MSG_BTN_NEXT: str = "next"
R_MSG_BTN_ONOFF: str = "on_off"

R_IMAGE_QUEUE: str = "img_queue"
R_SLEEP_STATUS: str = "sleep_status"

R_SETTINGS_EPD_BUSY: str = "epd_busy"
R_SETTINGS_DRAW_GRIDS: str = "draw_grids"


# E-Paper Display Width
EPD_WIDTH: int = 800


# E-Paper Display Height
EPD_HEIGHT: int = 480


# E-Paper Display color per channel
EPD_NC: int = 2


# Allowed upload file extensions
ALLOWED_EXTENSIONS: set[str] = ("png", "jpg", "jpeg", "bmp")


# Sleep Status
class SleepStatus(Enum):
	AWAKE = 0
	PENDING_SLEEP = 1
	SLEEP = 2
	PENDING_AWAKE = 3


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


TIME_MODE_DICT: dict[str, int] = {
	"off": int(TimeMode.OFF.value),
	"sect_9_top_left": int(TimeMode.SECT_9_TOP_LEFT.value),
	"sect_9_top_center": int(TimeMode.SECT_9_TOP_CENTER.value),
	"sect_9_top_right": int(TimeMode.SECT_9_TOP_RIGHT.value),
	"sect_9_middle_left": int(TimeMode.SECT_9_MIDDLE_LEFT.value),
	"sect_9_middle_center": int(TimeMode.SECT_9_MIDDLE_CENTER.value),
	"sect_9_middle_right": int(TimeMode.SECT_9_MIDDLE_RIGHT.value),
	"sect_9_bottom_left": int(TimeMode.SECT_9_BOTTOM_LEFT.value),
	"sect_9_bottom_center": int(TimeMode.SECT_9_BOTTOM_CENTER.value),
	"sect_9_bottom_right": int(TimeMode.SECT_9_BOTTOM_RIGHT.value),
	"sect_6_top_left": int(TimeMode.SECT_6_TOP_LEFT.value),
	"sect_6_top_right": int(TimeMode.SECT_6_TOP_RIGHT.value),
	"sect_6_middle_left": int(TimeMode.SECT_6_MIDDLE_LEFT.value),
	"sect_6_middle_right": int(TimeMode.SECT_6_MIDDLE_RIGHT.value),
	"sect_6_bottom_left": int(TimeMode.SECT_6_BOTTOM_LEFT.value),
	"sect_6_bottom_right": int(TimeMode.SECT_6_BOTTOM_RIGHT.value),
	"sect_4_top_left": int(TimeMode.SECT_4_TOP_LEFT.value),
	"sect_4_top_right": int(TimeMode.SECT_4_TOP_RIGHT.value),
	"sect_4_bottom_left": int(TimeMode.SECT_4_BOTTOM_LEFT.value),
	"sect_4_bottom_right": int(TimeMode.SECT_4_BOTTOM_RIGHT.value),
	"full_1": int(TimeMode.FULL_1.value),
	"full_2": int(TimeMode.FULL_2.value),
	"full_3": int(TimeMode.FULL_3.value),
}


# Text Colors
class TextColor(Enum):
	NONE: int = 0
	BLACK: int = 1
	WHITE: int = 2
	YELLOW: int = 3
	RED: int = 4
	BLUE: int = 5
	GREEN: int = 6


# Text Colors Dictionary
TEXT_COLOR_DICT: dict[str, int] = {
	"none": int(TextColor.NONE.value),
	"black": int(TextColor.BLACK.value),
	"white": int(TextColor.WHITE.value),
	"yellow": int(TextColor.YELLOW.value),
	"red": int(TextColor.RED.value),
	"blue": int(TextColor.BLUE.value),
	"green": int(TextColor.GREEN.value),
}


# Exceptions
ERR_UPLOAD_NO_FILE = -1
ERR_UPLOAD_INVALID_EXT = -2
ERR_UPLOAD_INVALID_IMAGE = -3
ERR_UPLOAD_POST_PROC = -4
ERR_UPLOAD_HASH = -5
ERR_UPLOAD_COPY = -6
ERR_UPLOAD_SAVE = -7

ERR_SCH_INVALID_DATA = -20
# ERR_SCH_INVALID_HOUR = -21
# ERR_SCH_INVALID_MINUTE= -22
# ERR_SCH_INVALID_DURATION = -23
