import os
import logging
from PIL import Image, ImageDraw, ImageFont
from enum import Enum
from . import consts as c

logging.basicConfig(level=logging.DEBUG)

class TimePos(Enum):
    TOP_LEFT = 1
    MIDDLE_LEFT = 2
    BOTTOM_LEFT = 3
    TOP_CENTER = 4
    MIDDLE_CENTER = 5
    BOTTOM_CENTER = 6
    TOP_RIGHT = 7
    MIDDLE_RIGHT = 8
    BOTTOM_RIGHT = 9
    FULL_1 = 10
    FULL_2 = 11
    FULL_3 = 12

font18 = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Font.ttc'), 18)
font24 = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Font.ttc'), 24)
font40 = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Font.ttc'), 40)
font80 = ImageFont.truetype(os.path.join(c.DIR_FONT, 'Clock2017L.ttc'), 80)

def is_machine_valid() -> bool:
    return "IS_RASPBERRYPI" in os.environ

def get_start_pos(time_pos:TimePos) -> tuple[int, int]:
    if time_pos == TimePos.TOP_LEFT:
        return 0, 0
    elif time_pos == TimePos.MIDDLE_LEFT:
        return 0, 0
    elif time_pos == TimePos.BOTTOM_LEFT:
        return 0, 0
    elif time_pos == TimePos.TOP_LEFT:
        return 0, 0
    elif time_pos == TimePos.TOP_LEFT:
        return 0, 0
    elif time_pos == TimePos.TOP_LEFT:
        return 0, 0
    elif time_pos == TimePos.TOP_LEFT:
        return 0, 0
    elif time_pos == TimePos.TOP_LEFT:
        return 0, 0
    elif time_pos == TimePos.TOP_LEFT:
        return 0, 0
    elif time_pos == TimePos.TOP_LEFT:
        return 0, 0
    elif time_pos == TimePos.TOP_LEFT:
        return 0, 0
    elif time_pos == TimePos.TOP_LEFT:
        return 0, 0


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


def draw_image_with_time(file_path:str, time:str, pos:TimePos) -> None:
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
        draw = ImageDraw.Draw(img)
        
        # test grid
        draw.line((266,0, 266, 480), epd.BLACK, 2)
        draw.line((532,0, 532, 480), epd.BLACK, 2)
        draw.line((0,159, 800, 159), epd.BLACK, 2)
        draw.line((0,319, 800, 319), epd.BLACK, 2)
        
        # draw time
        x, y = get_start_pos(pos)
        draw.text((x, y), time, epd.BLACK, font80)
        
        epd.display(epd.getbuffer(img))
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