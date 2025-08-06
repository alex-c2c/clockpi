import os

from datetime import datetime
from logging import Logger, getLogger
from PIL import Image, ImageDraw, ImageFont, ImageFile
from PIL.ImageFont import FreeTypeFont

from app.consts import *
from app.models import WallpaperModel
from app import redis_controller
from app.queue import logic

from .consts import *

logger: Logger = getLogger(__name__)

"""""
LOGIC
"""""

def get_time_pos(mode: int) -> tuple[int, int]:
	# 9 Section
	if mode == TIMEMODE_SECT_9_TOP_LEFT:
		return 0 * EPD_WIDTH / 3 + SECT_9_OFFSET_X, 0 * EPD_HEIGHT / 3 + SECT_9_OFFSET_Y
	elif mode == TIMEMODE_SECT_9_TOP_CENTER:
		return 1 * EPD_WIDTH / 3 + SECT_9_OFFSET_X, 0 * EPD_HEIGHT / 3 + SECT_9_OFFSET_Y
	elif mode == TIMEMODE_SECT_9_TOP_RIGHT:
		return 2 * EPD_WIDTH / 3 + SECT_9_OFFSET_X, 0 * EPD_HEIGHT / 3 + SECT_9_OFFSET_Y
	elif mode == TIMEMODE_SECT_9_MIDDLE_LEFT:
		return 0 * EPD_WIDTH / 3 + SECT_9_OFFSET_X, 1 * EPD_HEIGHT / 3 + SECT_9_OFFSET_Y
	elif mode == TIMEMODE_SECT_9_MIDDLE_CENTER:
		return 1 * EPD_WIDTH / 3 + SECT_9_OFFSET_X, 1 * EPD_HEIGHT / 3 + SECT_9_OFFSET_Y
	elif mode == TIMEMODE_SECT_9_MIDDLE_RIGHT:
		return 2 * EPD_WIDTH / 3 + SECT_9_OFFSET_X, 1 * EPD_HEIGHT / 3 + SECT_9_OFFSET_Y
	elif mode == TIMEMODE_SECT_9_BOTTOM_LEFT:
		return 0 * EPD_WIDTH / 3 + SECT_9_OFFSET_X, 2 * EPD_HEIGHT / 3 + SECT_9_OFFSET_Y
	elif mode == TIMEMODE_SECT_9_BOTTOM_CENTER:
		return 1 * EPD_WIDTH / 3 + SECT_9_OFFSET_X, 2 * EPD_HEIGHT / 3 + SECT_9_OFFSET_Y
	elif mode == TIMEMODE_SECT_9_BOTTOM_RIGHT:
		return 2 * EPD_WIDTH / 3 + SECT_9_OFFSET_X, 2 * EPD_HEIGHT / 3 + SECT_9_OFFSET_Y

	# 6 Section
	elif mode == TIMEMODE_SECT_6_TOP_LEFT:
		return 0 * EPD_WIDTH / 2 + SECT_6_OFFSET_X, 0 * EPD_HEIGHT / 3 + SECT_6_OFFSET_Y
	elif mode == TIMEMODE_SECT_6_TOP_RIGHT:
		return 1 * EPD_WIDTH / 2 + SECT_6_OFFSET_X, 0 * EPD_HEIGHT / 3 + SECT_6_OFFSET_Y
	elif mode == TIMEMODE_SECT_6_MIDDLE_LEFT:
		return 0 * EPD_WIDTH / 2 + SECT_6_OFFSET_X, 1 * EPD_HEIGHT / 3 + SECT_6_OFFSET_Y
	elif mode == TIMEMODE_SECT_6_MIDDLE_RIGHT:
		return 1 * EPD_WIDTH / 2 + SECT_6_OFFSET_X, 1 * EPD_HEIGHT / 3 + SECT_6_OFFSET_Y
	elif mode == TIMEMODE_SECT_6_BOTTOM_LEFT:
		return 0 * EPD_WIDTH / 2 + SECT_6_OFFSET_X, 2 * EPD_HEIGHT / 3 + SECT_6_OFFSET_Y
	elif mode == TIMEMODE_SECT_6_BOTTOM_RIGHT:
		return 1 * EPD_WIDTH / 2 + SECT_6_OFFSET_X, 2 * EPD_HEIGHT / 3 + SECT_6_OFFSET_Y

	# 4 Section
	elif mode == TIMEMODE_SECT_4_TOP_LEFT:
		return 0 * EPD_WIDTH / 2 + SECT_4_OFFSET_X, 0 * EPD_HEIGHT / 2 + SECT_4_OFFSET_Y
	elif mode == TIMEMODE_SECT_4_TOP_RIGHT:
		return (
			1 * EPD_WIDTH / 2 + +SECT_4_OFFSET_X,
			0 * EPD_HEIGHT / 2 + SECT_4_OFFSET_Y,
		)
	elif mode == TIMEMODE_SECT_4_BOTTOM_LEFT:
		return (
			0 * EPD_WIDTH / 2 + +SECT_4_OFFSET_X,
			1 * EPD_HEIGHT / 2 + SECT_4_OFFSET_Y,
		)
	elif mode == TIMEMODE_SECT_4_BOTTOM_RIGHT:
		return (
			1 * EPD_WIDTH / 2 + +SECT_4_OFFSET_X,
			1 * EPD_HEIGHT / 2 + SECT_4_OFFSET_Y,
		)

	# Full Screen
	elif mode == TIMEMODE_FULL_1:
		return 150, 100
	elif mode == TIMEMODE_FULL_2:
		return 88, 65
	elif mode == TIMEMODE_FULL_3:
		return 15, 30
	else:
		return 0, 0


def get_font(mode: int) -> FreeTypeFont:
	if mode == TIMEMODE_FULL_1:
		return ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 200)
	elif mode == TIMEMODE_FULL_2:
		return ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 250)
	elif mode == TIMEMODE_FULL_3:
		return ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 300)
	elif (
		mode == TIMEMODE_SECT_4_TOP_LEFT
		or mode == TIMEMODE_SECT_4_TOP_RIGHT
		or mode == TIMEMODE_SECT_4_BOTTOM_LEFT
		or mode == TIMEMODE_SECT_4_BOTTOM_RIGHT
	):
		return ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 130)

	elif (
		mode == TIMEMODE_SECT_6_TOP_LEFT
		or mode == TIMEMODE_SECT_6_TOP_RIGHT
		or mode == TIMEMODE_SECT_6_MIDDLE_LEFT
		or mode == TIMEMODE_SECT_6_MIDDLE_RIGHT
		or mode == TIMEMODE_SECT_6_BOTTOM_LEFT
		or mode == TIMEMODE_SECT_6_BOTTOM_RIGHT
	):
		return ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 130)
	else:
		return ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 80)


def draw_grids(draw: ImageDraw) -> None:
	# White every 10px
	for x in range(80):
		x_p: int = (x + 1) * 10
		draw.line((x_p, 0, x_p, 480), COLOR_EPD_WHITE, 1)
	for y in range(48):
		y_p: int = (y + 1) * 10
		draw.line((0, y_p, 800, y_p), COLOR_EPD_WHITE, 1)

	# Black 1/3
	draw.line((266, 0, 266, 480), COLOR_EPD_BLACK, 1)
	draw.line((532, 0, 532, 480), COLOR_EPD_BLACK, 1)
	draw.line((0, 159, 800, 159), COLOR_EPD_BLACK, 1)
	draw.line((0, 319, 800, 319), COLOR_EPD_BLACK, 1)

	# Red 1/2
	draw.line((400, 0, 400, 480), COLOR_EPD_RED, 1)
	draw.line((0, 240, 800, 240), COLOR_EPD_RED, 1)
 

# Copied from epd7in3e.py
def convert_image_to_buffer(image:Image) -> list[int]:
	# Create a pallette with the 7 colors supported by the panel
	pal_image = Image.new("P", (1,1))
	pal_image.putpalette( (0,0,0,  255,255,255,  255,255,0,  255,0,0,  0,0,0,  0,0,255,  0,255,0) + (0,0,0)*249)
	# pal_image.putpalette( (0,0,0,  255,255,255,  0,255,0,   0,0,255,  255,0,0,  255,255,0, 255,128,0) + (0,0,0)*249)

	# Check if we need to rotate the image
	imwidth, imheight = image.size
	if(imwidth == EPD_WIDTH and imheight == EPD_HEIGHT):
		image_temp = image
	elif(imwidth == EPD_HEIGHT and imheight == EPD_WIDTH):
		image_temp = image.rotate(90, expand=True)
	else:
		logger.warning("Invalid image dimensions: %d x %d, expected %d x %d" % (imwidth, imheight, EPD_WIDTH, EPD_HEIGHT))

	# Convert the soruce image to the 7 colors, dithering if needed
	image_7color = image_temp.convert("RGB").quantize(palette=pal_image)
	buf_7color = bytearray(image_7color.tobytes('raw'))

	# PIL does not support 4 bit color, so pack the 4 bits of color
	# into a single byte to transfer to the panel
	buf = [0x00] * int(EPD_WIDTH * EPD_HEIGHT / 2)
	idx = 0
	for i in range(0, len(buf_7color), 2):
		buf[idx] = (buf_7color[i] << 4) + buf_7color[i+1]
		idx += 1

	return buf


def process_image(
	file_path: str,
	time: str,
	mode: int,
	color: int,
	shadow: int,
	draw_grid: bool
):
	logger.info(f"process_image {file_path=} {time=} {mode=} {color=} {shadow=} {draw_grid=}")
    
    # Create image
	if file_path == "" or not os.path.isfile(file_path):
		image: Image = Image.new("RGB", (EPD_WIDTH, EPD_HEIGHT))
	else:
		image: ImageFile = Image.open(file_path)
	
	# Create draw canvas from image
	draw: ImageDraw = ImageDraw.Draw(image)

	# Debug - draw grids
	if draw_grid:
		draw_grids(draw)

	# Draw time
	if mode != TIMEMODE_OFF and time != "":
		x, y = get_time_pos(mode)
		font: ImageFont = get_font(mode)

		# draw shadow text first
		draw.text((x + SHADOW_OFFSET_X, y + SHADOW_OFFSET_Y), time, shadow, font)

		# draw text next
		draw.text((x, y), time, color, font)
  
	return image


def prepare_image() -> tuple[str, str, int, int, int, bool]:
	logger.info(f"prepare_image")
 
	file_path: str = ""
	image_queue: tuple[int] = logic.get_queue()
	if len(image_queue) > 0:
		wallpaper = WallpaperModel.query.get(image_queue[0])
		if wallpaper is not None:			
			hash: str = wallpaper.hash
			if len(hash) > 0:
				file_path: str = os.path.join(DIR_APP_UPLOAD, f"{hash}.bmp")
				if not os.path.isfile(file_path):
					file_path = ""
				else:
					logger.warning(f"Invalid {file_path=}")
			else:
				logger.warning(f"Wallpaper hash is empty")
		else:
			logger.warning(f"Invalid wallapaper ID: {image_queue[0]}")

	time: str = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}"
	mode: int = wallpaper.mode
	color: int = wallpaper.color
	shadow: int = wallpaper.shadow
	draw_grids: bool = redis_controller.get_draw_grids()
 
	return file_path, time, mode, color, shadow, draw_grids


def get_busy() -> bool:
	return True if redis_controller.rget(R_SETTINGS_EPD_BUSY, "0") == "1" else False


def update_clock_display():
     logger.info(f"update_clock_display")
     
     file_path, time, mode, color, shadow, draw_grids = prepare_image()
     
     image = process_image(file_path, time, mode, color, shadow, draw_grids)
     
     buffer: list[int] = convert_image_to_buffer(image)
     buffer_str: str = ":".join(str(e) for e in buffer)
     
     redis_controller.rpublish(R_CH_PUB, 1, f"{R_MSG_DRAW}^{buffer_str}")


def clear_clock_display() -> None:
	logger.debug(f"clear_clock_display")
	redis_controller.rpublish(R_CH_PUB, 1, R_MSG_CLEAR)


def update_frame_display() -> None:
    ...
    

def clear_frame_display() -> None:
    ...
