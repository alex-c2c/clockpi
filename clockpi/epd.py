import os
import logging
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
from enum import Enum

from . import consts as c

logging.basicConfig(level=logging.DEBUG)

class TimePos(Enum):
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


font_9_sect = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Roboto-Bold.ttf'), 80)
font_6_sect = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Roboto-Bold.ttf'), 100)
font_4_sect = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Roboto-Bold.ttf'), 160)

font_full_1 = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Roboto-Light.ttf'), 200)
font_full_2 = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Roboto-Light.ttf'), 250)
font_full_3 = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Roboto-Light.ttf'), 300)


def is_machine_valid() -> bool:
    return "IS_RASPBERRYPI" in os.environ


def get_time_pos(time_pos:TimePos, epd) -> tuple[int, int]:
    # 9 Section
    if time_pos == TimePos.SECT_9_TOP_LEFT:
        return 0 * epd.width / 3 + 33, 0 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_9_TOP_CENTER:
        return 1 * epd.width / 3 + 33, 0 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_9_TOP_RIGHT:
        return 2 * epd.width / 3 + 33, 0 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_9_MIDDLE_LEFT:
        return 0 * epd.width / 3 + 33, 1 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_9_MIDDLE_CENTER:
        return 1 * epd.width / 3 + 33, 1 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_9_MIDDLE_RIGHT:
        return 2 * epd.width / 3 + 33, 1 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_9_BOTTOM_LEFT:
        return 0 * epd.width / 3 + 33, 2 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_9_BOTTOM_CENTER:
        return 1 * epd.width / 3 + 33, 2 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_9_BOTTOM_RIGHT:
        return 2 * epd.width / 3 + 33, 2 * epd.height / 3 + 25
    
    # 6 Section
    elif time_pos == TimePos.SECT_6_TOP_LEFT:
        return 0 * epd.width / 2 + 33, 0 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_6_TOP_RIGHT:
        return 1 * epd.width / 2 + 33, 0 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_6_MIDDLE_LEFT:
        return 0 * epd.width / 2 + 33, 1 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_6_MIDDLE_RIGHT:
        return 1 * epd.width / 2 + 33, 1 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_6_BOTTOM_LEFT:
        return 0 * epd.width / 2 + 33, 2 * epd.height / 3 + 25
    elif time_pos == TimePos.SECT_6_BOTTOM_RIGHT:
        return 1 * epd.width / 2 + 33, 2 * epd.height / 3 + 25
    
    # 4 Section
    elif time_pos == TimePos.SECT_4_TOP_LEFT:
        return 0 * epd.width / 2 + 33, 0 * epd.height / 2 + 25
    elif time_pos == TimePos.SECT_4_TOP_RIGHT:
        return 1 * epd.width / 2 + 33, 0 * epd.height / 2 + 25
    elif time_pos == TimePos.SECT_4_BOTTOM_LEFT:
        return 0 * epd.width / 2 + 33, 1 * epd.height / 2 + 25
    elif time_pos == TimePos.SECT_4_BOTTOM_RIGHT:
        return 1 * epd.width / 2 + 33, 1 * epd.height / 2 + 25
    
    # Full Screen
    elif time_pos == TimePos.FULL_1:
        return 150, 100
    elif time_pos == TimePos.FULL_2:
        return 88, 65
    elif time_pos == TimePos.FULL_3:
        return 25, 30
    else:
        return 0, 0
    

def get_font(time_pos:TimePos) -> FreeTypeFont:
    if time_pos == TimePos.FULL_1:
        return font_full_1
    elif time_pos == TimePos.FULL_2:
        return font_full_2
    elif time_pos == TimePos.FULL_3:
        return font_full_3
    elif time_pos == TimePos.SECT_4_TOP_LEFT or \
            time_pos == TimePos.SECT_4_TOP_RIGHT or \
            time_pos == TimePos.SECT_4_BOTTOM_LEFT or \
            time_pos == TimePos.SECT_4_BOTTOM_RIGHT:
        return font_4_sect
    elif time_pos == TimePos.SECT_6_TOP_LEFT or \
            time_pos == TimePos.SECT_6_TOP_RIGHT or \
            time_pos == TimePos.SECT_6_MIDDLE_LEFT or \
            time_pos == TimePos.SECT_6_MIDDLE_RIGHT or \
            time_pos == TimePos.SECT_6_BOTTOM_LEFT or \
            time_pos == TimePos.SECT_6_BOTTOM_RIGHT:
        return font_6_sect
    else:
        return font_9_sect


def get_color(color:int, epd) -> int:
    if color == c.COLOR_BLACK:
        return epd.BLACK
    elif color == c.COLOR_WHITE:
        return epd.WHITE
    elif color == c.COLOR_YELLOW:
        return epd.YELLOW
    elif color == c.COLOR_RED:
        return epd.RED
    elif color == c.COLOR_BLUE:
        return epd.BLUE
    elif color == c.COLOR_GREEN:
        return epd.GREEN
    else:
        logging.warning(f"Selected unknown {color=}")
        return epd.BLACK
    

def draw_grids(draw:ImageDraw, epd) -> None:
    # White every 10px
    for x in range(80):
        x_p:int = (x + 1) * 10
        draw.line((x_p, 0, x_p, 480), epd.WHITE, 1)
    for y in range(48):
        y_p:int = (y + 1) * 10
        draw.line((0, y_p, 800, y_p), epd.WHITE, 1)

    # Black 1/3 
    draw.line((266,0, 266, 480), epd.BLACK, 1)
    draw.line((532,0, 532, 480), epd.BLACK, 1)
    draw.line((0,159, 800, 159), epd.BLACK, 1)
    draw.line((0,319, 800, 319), epd.BLACK, 1)
    
    # Red 1/2
    draw.line((400, 0, 400, 480), epd.RED, 1)
    draw.line((0, 240, 800, 240), epd.RED, 1)


def clear_display() -> None:
    if not is_machine_valid():
        logging.warning("Unable to clear display")
        return

    try:
        from lib.waveshare_epd.epd7in3e import EPD
        epd = EPD()
        epd.init()
        epd.clear()
        epd.sleep()
        
    except IOError as e:
        logging.error(e)


def draw_image_with_time(file_path:str, time:str, pos:TimePos, refresh:bool = False, color:int = c.COLOR_BLACK, draw_grid:bool = False) -> None:
    if not is_machine_valid():
        logging.warning(f"Unable to draw image")
        return
    
    if not os.path.isfile(file_path):
        logging.warning("Cannot display invalid file")
        return
    
    try:
        #from lib.waveshare_epd import epd7in3e
        from lib.waveshare_epd.epd7in3e import EPD
        epd = EPD()
        epd.init()
        
        if refresh:
            epd.clear()

        #  Create image
        img = Image.open(file_path)
        
        if pos == TimePos.OFF or time == "":
            return
        
        draw = ImageDraw.Draw(img)

        # Debug - draw grids
        if draw_grid:
            draw_grids(draw, epd)

        # Draw time
        xy:tuple[int, int] = get_time_pos(pos, epd)
        color:int = get_color(color, epd)
        font:ImageFont = get_font(pos)
        draw.text(xy, time, color, font)

        # Send to display
        epd.display(epd.getbuffer(img))
        
        # Sleep
        epd.sleep()
            
    except IOError as e:
        logging.error(e)


def draw_image(file_path:str, refresh:bool = True) -> None:
    if not is_machine_valid():
        logging.warning(f"Unable to draw image")
        return
    
    if not os.path.isfile(file_path):
        logging.warning("Cannot display invalid file")
        return
    
    try:
        from lib.waveshare_epd.epd7in3e import EPD
        epd = EPD()
        epd.init()
        
        if refresh:
            epd.clear()

        # Drawing on the image
        img = Image.open(file_path)
        epd.display(epd.getbuffer(img))
        epd.sleep()
            
    except IOError as e:
        logging.error(e)
    
