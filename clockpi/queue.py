import random
import logging
from clockpi.db import get_images


LOGGER = logging.getLogger(name="logic")
image_queue: list[int] = []


def get_queue() -> tuple[int]:
    global image_queue
    return tuple(image_queue)


def generate_random_queue() -> None:
    global image_queue
    image_queue.clear()
    
    images = get_images()
    for img in images:
        image_queue.append(img["id"])
    
    random.shuffle(image_queue)
    

def shift_next() -> None:
    global image_queue
    if len(image_queue) <= 1:
        return
    
    current: int = image_queue.pop(0)
    image_queue.append(current)


def get_current_id() -> int:
    global image_queue
    if len(image_queue) > 0:
        return image_queue[0]
    
    return 0


def shuffle_queue() -> None:
    global image_queue
    random.shuffle(image_queue)


def append_to_queue(id:int) -> None:
    global image_queue
    image_queue.append(id)
    

def remove_from_queue(index:int) -> None:
    global image_queue
    image_queue.pop(index)