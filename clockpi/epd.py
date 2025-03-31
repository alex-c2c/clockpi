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
    SECT_9_MIDDLE_LEFT = 2
    SECT_9_BOTTOM_LEFT = 3
    SECT_9_TOP_CENTER = 4
    SECT_9_MIDDLE_CENTER = 5
    SECT_9_BOTTOM_CENTER = 6
    SECT_9_TOP_RIGHT = 7
    SECT_9_MIDDLE_RIGHT = 8
    SECT_9_BOTTOM_RIGHT = 9
    SECT_4_TOP_LEFT = 10
    SECT_4_BOTTOM_LEFT = 11
    SECT_4_TOP_RIGHT = 12
    SECT_4_BOTTOM_RIGHT = 13
    FULL_1 = 14 # Small
    FULL_2 = 15 # Medium
    FULL_3 = 16 # Large
    MAX = 17


font_bold = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Roboto-Bold.ttf'), 80)
font_full_1 = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Roboto-Light.ttf'), 200)
font_full_2 = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Roboto-Light.ttf'), 250)
font_full_3 = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Roboto-Light.ttf'), 300)


def is_machine_valid() -> bool:
    return "IS_RASPBERRYPI" in os.environ


def get_time_pos(time_pos:TimePos) -> tuple[int, int]:
    if time_pos == TimePos.SECT_9_TOP_LEFT:
        return 0 * c.EPD_WIDTH / 3 + 33, 0 * c.EPD_HEIGHT / 3 + 25
    elif time_pos == TimePos.SECT_9_MIDDLE_LEFT:
        return 0 * c.EPD_WIDTH / 3 + 33, 1 * c.EPD_HEIGHT / 3 + 25
    elif time_pos == TimePos.SECT_9_BOTTOM_LEFT:
        return 0 * c.EPD_WIDTH / 3 + 33, 2 * c.EPD_HEIGHT / 3 + 25
    elif time_pos == TimePos.SECT_9_TOP_CENTER:
        return 1 * c.EPD_WIDTH / 3 + 33, 0 * c.EPD_HEIGHT / 3 + 25
    elif time_pos == TimePos.SECT_9_MIDDLE_CENTER:
        return 1 * c.EPD_WIDTH / 3 + 33, 1 * c.EPD_HEIGHT / 3 + 25
    elif time_pos == TimePos.SECT_9_BOTTOM_CENTER:
        return 1 * c.EPD_WIDTH / 3 + 33, 2 * c.EPD_HEIGHT / 3 + 25
    elif time_pos == TimePos.SECT_9_TOP_RIGHT:
        return 2 * c.EPD_WIDTH / 3 + 33, 0 * c.EPD_HEIGHT / 3 + 25
    elif time_pos == TimePos.SECT_9_MIDDLE_RIGHT:
        return 2 * c.EPD_WIDTH / 3 + 33, 1 * c.EPD_HEIGHT / 3 + 25
    elif time_pos == TimePos.SECT_9_BOTTOM_RIGHT:
        return 2 * c.EPD_WIDTH / 3 + 33, 2 * c.EPD_HEIGHT / 3 + 25
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
    else:
        return font_bold
    

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
        from lib.waveshare_epd import epd7in3e
        epd = epd7in3e.EPD()
        epd.init()
        epd.clear()
        epd.sleep()
        
    except IOError as e:
        logging.error(e)


def draw_image_with_time(file_path:str, time:str, pos:TimePos, refresh:bool = False) -> None:
    if not is_machine_valid():
        logging.warning(f"Unable to draw image")
        return
    
    if not os.path.isfile(file_path):
        logging.warning("Cannot display invalid file")
        return
    
    try:
        from lib.waveshare_epd import epd7in3e
        epd = epd7in3e.EPD()
        epd.init()
        
        if refresh:
            epd.clear()

        #  Create image
        img = Image.open(file_path)
        
        if pos == TimePos.OFF or time == "":
            return
        
        draw = ImageDraw.Draw(img)

        # Debug - draw grids
        draw_grids(draw, epd)

        # Draw time
        draw.text(get_time_pos(pos), time, epd.BLACK, get_font(pos))

        # Send to display
        epd.display(epd.getbuffer(img))
        
        # Sleep
        epd.sleep()
            
    except IOError as e:
        logging.error(e)


def draw_image(file_path:str) -> None:
    if not is_machine_valid():
        logging.warning(f"Unable to draw image")
        return
    
    if not os.path.isfile(file_path):
        logging.warning("Cannot display invalid file")
        return
    
    try:
        from lib.waveshare_epd import epd7in3e
        epd = epd7in3e.EPD()
        epd.init()
        epd.clear()

        # Drawing on the image
        img = Image.open(file_path)
        epd.display(epd.getbuffer(img))
        epd.sleep()
            
    except IOError as e:
        logging.error(e)
    
'''
try:
    logging.info("epd7in3e Demo")

    epd = epd7in3e.EPD()   
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font40 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)
    
    # Drawing on the image
    logging.info("1.Drawing on the image...")
    Himage = Image.new('RGB', (epd.width, epd.height), epd.WHITE)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((5, 0), 'hello world', font = font18, fill = epd.RED)
    draw.text((5, 20), '7.3inch e-Paper (e)', font = font24, fill = epd.YELLOW)
    draw.text((5, 45), u'微雪电子', font = font40, fill = epd.GREEN)
    draw.text((5, 85), u'微雪电子', font = font40, fill = epd.BLUE)
    draw.text((5, 125), u'微雪电子', font = font40, fill = epd.BLACK)

    draw.line((5, 170, 80, 245), fill = epd.BLUE)
    draw.line((80, 170, 5, 245), fill = epd.YELLOW)
    draw.rectangle((5, 170, 80, 245), outline = epd.BLACK)
    draw.rectangle((90, 170, 165, 245), fill = epd.GREEN)
    draw.arc((5, 250, 80, 325), 0, 360, fill = epd.RED)
    draw.chord((90, 250, 165, 325), 0, 360, fill = epd.YELLOW)
    epd.display(epd.getbuffer(Himage))
    time.sleep(3)
    
    # read bmp file 
    logging.info("2.read bmp file")
    Himage = Image.open(os.path.join(picdir, '7in3e.bmp'))
    epd.display(epd.getbuffer(Himage))
    time.sleep(3)
    
    logging.info("Clear...")
    epd.Clear()
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in3e.epdconfig.module_exit(cleanup=True)
    exit()
'''
