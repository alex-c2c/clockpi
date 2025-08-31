import base64
import os

from datetime import datetime
from logging import Logger, getLogger
from PIL.Image import Image
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont
from PIL import ImageFont as PImgFont
from PIL import Image as PImg
from PIL import ImageDraw as PImgDraw

from app import redis_controller
from app.consts import *
from app.queue.logic import *
from app.wallpaper.models import WallpaperModel

from .consts import *

logger: Logger = getLogger(__name__)

"""""
LOGIC
"""""

def draw_grids(draw: ImageDraw) -> None:
	# White every 10px
	for x in range(80):
		x_p: int = (x + 1) * 10
		draw.line((x_p, 0, x_p, 480), Color.WHITE.get_epd_color(), 1)
	for y in range(48):
		y_p: int = (y + 1) * 10
		draw.line((0, y_p, 800, y_p), Color.WHITE.get_epd_color(), 1)

	# Black 1/3
	draw.line((266, 0, 266, 480), Color.BLACK.get_epd_color(), 1)
	draw.line((532, 0, 532, 480), Color.BLACK.get_epd_color(), 1)
	draw.line((0, 159, 800, 159), Color.BLACK.get_epd_color(), 1)
	draw.line((0, 319, 800, 319), Color.BLACK.get_epd_color(), 1)

	# Red 1/2
	draw.line((400, 0, 400, 480), Color.RED.get_epd_color(), 1)
	draw.line((0, 240, 800, 240), Color.RED.get_epd_color(), 1)


# Copied from epd7in3e.py
def convert_image_to_buffer(image:Image) -> list[int]:
	# Create a pallette with the 7 colors supported by the panel
	pal_image = PImg.new("P", (1,1))
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
	buf = [0x00] * int(EPD_WIDTH * int(EPD_HEIGHT / 2))
	idx = 0
	for i in range(0, len(buf_7color), 2):
		buf[idx] = (buf_7color[i] << 4) + buf_7color[i+1]
		idx += 1

	return buf


def process_image(
	file_path: str,
	time: str,
	x: int,
	y: int,
	w: float,
	h: float,
	color: int,
	shadow: int,
	draw_grid: bool
):
	logger.info(f"process_image {file_path=} {time=} {x=} {y=} {w=} {h=} {color=} {shadow=} {draw_grid=}")

	# Create image
	if file_path == "" or not os.path.isfile(file_path):
		image: Image = PImg.new("RGB", (EPD_WIDTH, EPD_HEIGHT))
	else:
		image: Image = PImg.open(file_path)
	
	# Create draw canvas from image
	draw: ImageDraw = PImgDraw.Draw(image)

	# Debug - draw grids
	if draw_grid:
		draw_grids(draw)

	x_pos: int = int((x * 0.01) * EPD_WIDTH)
	y_pos: int = int((y * 0.01) * EPD_HEIGHT)
	width: float = (w * 0.01) * EPD_WIDTH
	font_path: str = os.path.join(DIR_FONT, "RobotoMono-Bold.ttf")
	font_size: int = 10
	font: FreeTypeFont = PImgFont.truetype(font_path, font_size)
	
	# get the correct font size
	text_width = draw.textlength(time, font=font)
	while text_width < width:
		font_size += 1
		font = PImgFont.truetype(font_path, font_size)
		text_width = draw.textlength(time, font=font)
	
	# draw shadow text first
	draw.text((x_pos + TEXT_OFFSET_X + SHADOW_OFFSET_X * w * 0.01, y_pos + TEXT_OFFSET_Y + SHADOW_OFFSET_Y * w * 0.01), time, shadow, font, anchor="lt")

	# draw text next
	draw.text((x_pos + TEXT_OFFSET_X, y_pos + TEXT_OFFSET_Y), time, color, font, anchor="lt")
	
	return image


def get_busy() -> bool:
	return True if redis_controller.rget(R_SETTINGS_EPD_BUSY, "0") == "1" else False


def update_clock_display():
	logger.info(f"update_clock_display")
	
	wallpaper: WallpaperModel | None = WallpaperModel.query.get(get_current_id())
	if wallpaper is None:
		return

	file_path: str = os.path.join(DIR_APP_UPLOAD, wallpaper.file_name)
	if not os.path.isfile(file_path):
		return

	time: str = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}"
	x: int = wallpaper.x
	y: int = wallpaper.y
	w: float = wallpaper.w
	h: float = wallpaper.h
	color: int = wallpaper.color.get_epd_color()
	shadow: int = wallpaper.shadow.get_epd_color()
	draw_grids: bool = redis_controller.get_draw_grids()
	
	image = process_image(file_path, time, x, y, w, h, color, shadow, draw_grids)
		
	buffer: list[int] = convert_image_to_buffer(image)
	encoded_data: str = base64.b64encode(bytes(buffer)).decode("utf-8")
	#logger.debug(f"{encoded_data=}")
	logger.debug(f"{len(buffer)=}")
	#buffer_str: str = ":".join(str(e) for e in buffer)

	redis_controller.rpublish(f"{R_CH_DRAW}_10.0.20.2", encoded_data)


def clear_clock_display() -> None:
	logger.debug(f"clear_clock_display")
	redis_controller.rpublish(f"{R_CH_CLEAR}_10.0.20.2", "")


def save_current_to_temp() -> None:
	logger.info(f"save_current_to_temp")
	
	wallpaper: WallpaperModel | None = WallpaperModel.query.get(get_current_id())
	if wallpaper is None:
		return

	hash: str = wallpaper.hash
	if len(hash) == 0:
		return

	file_path: str = os.path.join(DIR_APP_UPLOAD, f"{hash}.bmp")
	if not os.path.isfile(file_path):
		return

	time: str = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}"
	x: int = wallpaper.x
	y: int = wallpaper.y
	w: float = wallpaper.w
	h: float = wallpaper.h
	color: int = wallpaper.color.get_epd_color()
	shadow: int = wallpaper.shadow.get_epd_color()
	draw_grids: bool = redis_controller.get_draw_grids()
	
	image = process_image(file_path, time, x, y, w, h, color, shadow, draw_grids)
	
	image.save(os.path.join(DIR_APP_UPLOAD, f"test.bmp"))
