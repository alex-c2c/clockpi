import os

from logging import Logger, getLogger
from PIL.Image import Image
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont
from PIL import ImageFont as PImgFont
from PIL import Image as PImg
from PIL import ImageDraw as PImgDraw

from app.consts import *

from .consts import *

logger: Logger = getLogger(__name__)


"""""
LOGIC
"""""


def draw_grids(draw: ImageDraw) -> None:
	# White every 10px
	for x in range(80):
		x_p: int = (x + 1) * 10
		draw.line((x_p, 0, x_p, 480), SupportedColors.WHITE.get_epd_color(), 1)
	for y in range(48):
		y_p: int = (y + 1) * 10
		draw.line((0, y_p, 800, y_p), SupportedColors.WHITE.get_epd_color(), 1)

	# Black 1/3
	draw.line((266, 0, 266, 480), SupportedColors.BLACK.get_epd_color(), 1)
	draw.line((532, 0, 532, 480), SupportedColors.BLACK.get_epd_color(), 1)
	draw.line((0, 159, 800, 159), SupportedColors.BLACK.get_epd_color(), 1)
	draw.line((0, 319, 800, 319), SupportedColors.BLACK.get_epd_color(), 1)

	# Red 1/2
	draw.line((400, 0, 400, 480), SupportedColors.RED.get_epd_color(), 1)
	draw.line((0, 240, 800, 240), SupportedColors.RED.get_epd_color(), 1)


# Copied from epd7in3e.py
def convert_image_to_buffer(image:Image) -> list[int]:
	# Create a palette with the 7 colors supported by the panel
	pal_image: Image = PImg.new("P", (1,1))
	pal_image.putpalette( (0,0,0,  255,255,255,  255,255,0,  255,0,0,  0,0,0,  0,0,255,  0,255,0) + (0,0,0)*249)
	# pal_image.putpalette( (0,0,0,  255,255,255,  0,255,0,   0,0,255,  255,0,0,  255,255,0, 255,128,0) + (0,0,0)*249)

	# Check if we need to rotate the image
	if image.width == EPD_DIMENSIONS[0] and image.height == EPD_DIMENSIONS[1]:
		rot_img: Image = image
	elif image.width == EPD_DIMENSIONS[1] and image.height == EPD_DIMENSIONS[0]:
		rot_img = image.rotate(90, expand=True)
	else:
		logger.warning("Invalid image dimensions: %d x %d, expected %d x %d" % (image.width, image.height, EPD_DIMENSIONS[0], EPD_DIMENSIONS[1]))
	
	# Convert the soruce image to the 7 colors, dithering if needed
	image_7color: Image = rot_img.convert("RGB").quantize(palette=pal_image)
	buf_7color: bytearray = bytearray(image_7color.tobytes('raw'))

	# PIL does not support 4 bit color, so pack the 4 bits of color
	# into a single byte to transfer to the panel
	buffer: list[int] = [0x00] * BUFFER_LEN
	index = 0
	
	for i in range(0, len(buf_7color), 2):
		buffer[index] = (buf_7color[i] << 4) + buf_7color[i+1]
		index += 1

	return buffer


def process_image(
	file_path: str,
	time: str,
	label_x_per: float,
	label_y_per: float,
	label_w_per: float,
	label_h_per: float,
	img_width: int,
	img_height: int,
	color: str,
	shadow: str,
	draw_grid: bool
):
	logger.info(f"process_image {file_path=} {time=} {label_x_per=} {label_y_per=} {label_w_per=} {label_h_per=} {img_width=} {img_height=} {color=} {shadow=} {draw_grid=}")
	
	try:
		epd_color = SupportedColors[color].get_epd_color()
	except Exception as e:
		epd_color = SupportedColors.NONE.get_epd_color()
		logger.error(f"Caught invalid argument: {color=}")
	
	try:
		epd_shadow = SupportedColors[shadow].get_epd_color()
	except Exception as e:
		epd_shadow = SupportedColors.NONE.get_epd_color()
		logger.error(f"Caught invalid argument: {shadow=}")
	
	# Create image
	image: Image = PImg.open(file_path)
	
	# Create draw canvas from image
	draw: ImageDraw = PImgDraw.Draw(image)

	# Debug - draw grids
	if draw_grid:
		draw_grids(draw)

	text_x_pos: int = int(label_x_per * img_width)
	text_y_pos: int = int(label_y_per * img_height)
	text_width: float = label_w_per * img_width
	font_path: str = os.path.join(DIR_FONT, "RobotoMono-Bold.ttf")
	font_size: int = 10
	font: FreeTypeFont = PImgFont.truetype(font_path, font_size)
	
	# get the correct font size
	text_width = draw.textlength(time, font=font)
	while text_width < img_width:
		font_size += 1
		font = PImgFont.truetype(font_path, font_size)
		text_width = draw.textlength(time, font=font)
	
	# draw shadow text first
	if epd_shadow is not None:
		draw.text((text_x_pos + TEXT_OFFSET_X + SHADOW_OFFSET_X * label_w_per * 0.01, text_y_pos + TEXT_OFFSET_Y + SHADOW_OFFSET_Y * label_w_per * 0.01), time, epd_shadow, font, anchor="lt")

	# draw text next
	if epd_color is not None:
		draw.text((text_x_pos + TEXT_OFFSET_X, text_y_pos + TEXT_OFFSET_Y), time, epd_color, font, anchor="lt")
	
	return image


