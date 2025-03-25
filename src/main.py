#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import logging
import time
import traceback
import datetime

DIR_IMG:str = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'img')
DIR_LIB:str = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(DIR_LIB):
    sys.path.append(DIR_LIB)

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd7in3e

logging.basicConfig(level=logging.DEBUG)

def main() -> None:
    font18 = ImageFont.truetype(os.path.join(DIR_IMG, 'Font.ttc'), 18)
    font24 = ImageFont.truetype(os.path.join(DIR_IMG, 'Font.ttc'), 24)
    font40 = ImageFont.truetype(os.path.join(DIR_IMG, 'Font.ttc'), 40)
    font80 = ImageFont.truetype(os.path.join(DIR_IMG, 'Font.ttc'), 80)

    try:
        logging.info("Starting...")
        epd = epd7in3e.EPD()
        epd.init()
        epd.Clear()
    
        logging.info("Drawing Image")
        Himage = Image.open(os.path.join(DIR_IMG, "7in3e.bmp"))
        draw = ImageDraw.Draw(Himage)
        draw.text((50, 50), 'HELLO WORLD', font = font80, fill = epd.BLACK)
        epd.display(epd.getbuffer(Himage))
        epd.sleep()
        
        logging.info("sleeping for 30s...")
        time.sleep(30)

        logging.info("Waking up...")
        epd.init()

        logging.info("Update Image")
        Himage = Image.open(os.path.join(DIR_IMG, "7in3e.bmp"))
        draw = ImageDraw.Draw(Himage)
        draw.text((300, 200), 'HELLO WORLD', font = font80, fill = epd.BLUE)
        epd.display(epd.getbuffer(Himage))
        epd.sleep()

        logging.info("sleeping for 30s...")
        time.sleep(30)

        logging.info("waking up...")
        epd.init()

        logging.info("Clearing screen")
        epd.Clear()

        logging.info("Sleeping...")
        epd.sleep()
    
    except IOError as e:
        logging.error(e)

    except KeyboardInterrupt:
        logging.info("Exiting...")
        epd7in3e.epdconfig.module_exit(cleanup=True)
        exit()


if __name__ == "__main__":
    main()
