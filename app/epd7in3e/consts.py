from enum import Enum


class SupportedColors(Enum):
	NONE		= "NONE"
	BLACK		= "BLACK"
	WHITE		= "WHITE"
	YELLOW		= "YELLOW"
	RED			= "RED"
	BLUE		= "BLUE"
	GREEN		= "GREEN"
	# ORANGE 	= "ORANGE" 	# 0100

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
			return None
			

# Dimensions
EPD_DIMENSIONS: tuple[int, int] = (800, 480)


# Buffer length
BUFFER_LEN: int = int(EPD_DIMENSIONS[0] * EPD_DIMENSIONS[1] * 0.5)


# E-Paper Display color per channel
EPD_NC: int = 2


# Default Colors
DEFAULT_LABEL_COLOR: str = SupportedColors.WHITE.value
DEFAULT_LABEL_SHADOW: str = SupportedColors.BLACK.value
	

# Offsets
TEXT_OFFSET_X: int = 10
TEXT_OFFSET_Y: int = 0

SHADOW_OFFSET_X: int = -10
SHADOW_OFFSET_Y: int = 10


'''
# EPD supported colors (copied from epd lib)
COLOR_EPD_BLACK	= 0x000000	# 0000  BGR
COLOR_EPD_WHITE	= 0xffffff  # 0001
COLOR_EPD_YELLOW	= 0x00ffff  # 0010
COLOR_EPD_RED	= 0x0000ff  # 0011
COLOR_EPD_ORANGE: int = 0x0080ff 	# 0100
COLOR_EPD_BLUE	= 0xff0000  # 0101
COLOR_EPD_GREEN	= 0x00ff00  # 0110
'''
