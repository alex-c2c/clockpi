import os

# Dimensions
if os.getenv("ORIENTATION").lower() == "vertical":
    EPD_ORIENTATION :int = 1
    EPD_WIDTH: int = 480
    EPD_HEIGHT: int = 800
else:
    EPD_ORIENTATION: int = 0
    EPD_WIDTH: int = 800
    EPD_HEIGHT: int = 480

# E-Paper Display color per channel
EPD_NC: int = 2

# EPD supported colors (copied from epd lib)
COLOR_EPD_BLACK: int	= 0x000000	# 0000  BGR
COLOR_EPD_WHITE: int	= 0xffffff  # 0001
COLOR_EPD_YELLOW: int	= 0x00ffff  # 0010
COLOR_EPD_RED: int	= 0x0000ff  # 0011
#COLOR_EPD_ORANGE: int = 0x0080ff 	# 0100
COLOR_EPD_BLUE: int	= 0xff0000  # 0101
COLOR_EPD_GREEN: int	= 0x00ff00  # 0110

# Offsets
SHADOW_OFFSET_X: int = -5
SHADOW_OFFSET_Y: int = 5

SECT_9_OFFSET_X: int = 33
SECT_9_OFFSET_Y: int = 25

SECT_6_OFFSET_X: int = 30
SECT_6_OFFSET_Y: int = -10

SECT_4_OFFSET_X: int = 30
SECT_4_OFFSET_Y: int = 30
