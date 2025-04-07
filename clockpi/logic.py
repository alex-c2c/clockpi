import os
import logging


def redis_event_handler(msg) -> None:
    logging.debug(msg=f"{msg=}")
    
    if msg["type"] != "pmessage":
        return
    
    data:list[str] = msg["data"].split("^")
    if len(data) != 2 or data[0] != "busy":
        return
    
    os.environ['epd_busy'] = "1" if data[1] == "1" else "0"
    

def update_epd_busy(busy:str) -> None:
    update_epd_busy(True if busy == "1" else False)


def update_epd_busy(busy:bool) -> None:
    os.environ["epd_busy"] = "1" if busy else "0"
    

def get_epd_busy() -> bool:
    busy:bool = True if os.environ.get("epd_busy") == "1" else False
    return busy