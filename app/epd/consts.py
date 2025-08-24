import os
from enum import Enum

# Dimensions
if os.getenv("ORIENTATION", "").lower() == "vertical":
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
#COLOR_EPD_BLACK	= 0x000000	# 0000  BGR
#COLOR_EPD_WHITE	= 0xffffff  # 0001
#COLOR_EPD_YELLOW	= 0x00ffff  # 0010
#COLOR_EPD_RED	= 0x0000ff  # 0011
#COLOR_EPD_ORANGE: int = 0x0080ff 	# 0100
#COLOR_EPD_BLUE	= 0xff0000  # 0101
#COLOR_EPD_GREEN	= 0x00ff00  # 0110

class Color(Enum):
	BLACK	= "BLACK"
	WHITE	= "WHITE"
	YELLOW	= "YELLOW"
	RED		= "RED"
	BLUE	= "BLUE"
	GREEN	= "GREEN"
	# ORANGE = "ORANGE" 	# 0100

	def get_epd_color(self):
		if self.name == "BLACK":
			return 0x000000	# 0000  BGR
		elif self.name == "WHITE":
			return 0xffffff  # 0001
		elif self.name == "YELLOW":
			return 0x00ffff  # 0010
		elif self.name == "RED":
			return 0x0000ff  # 0011
		#COLOR_EPD_ORANGE: int = 0x0080ff 	# 0100
		elif self.name == "BLUE":
			return 0xff0000  # 0101
		elif self.name == "GREEN":
			return 0x00ff00  # 0110
		else:
			assert False


# Offsets
TEXT_OFFSET_X: int = 10
TEXT_OFFSET_Y: int = 0

SHADOW_OFFSET_X: int = -10
SHADOW_OFFSET_Y: int = 10
