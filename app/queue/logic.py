import random
from logging import Logger, getLogger

from app import redis_controller
from app.consts import *
from app.wallpaper.model import WallpaperModel

logger: Logger = getLogger(__name__)

"""""
LOGIC
"""""

def generate_initial_queue() -> None:
	wallpapers: list = WallpaperModel.query.all()
	queue: list[int] = []

	for model in wallpapers:
		queue.append(model.id)

	random.shuffle(queue)

	save_queue(queue)


def get_queue() -> list[int]:
	rqueue: str = redis_controller.rget(R_IMAGE_QUEUE, "")
	return [int(i) for i in rqueue.split("^") if i is not ""]


def save_queue(queue: list[int]) -> None:
	logger.debug(f"save_queue {queue=}")
	redis_controller.rset(R_IMAGE_QUEUE, "^".join(str(i) for i in queue))


def shift_next() -> None:
	queue: list[int] = get_queue()

	if len(queue) <= 1:
		return

	first: int = queue.pop(0)
	queue.append(first)

	save_queue(queue)


def get_current_id() -> int:
	queue: list[int] = get_queue()

	if len(queue) > 0:
		return queue[0]

	return 0


def shuffle_queue() -> None:
	queue: list[int] = get_queue()
	random.shuffle(queue)
	save_queue(queue)


def append_to_queue(id: int) -> int:
	queue: list[int] = get_queue()

	if id in queue:
		return ERR_QUEUE_DUPLICATE_ID

	queue.append(id)
	save_queue(queue)

	return 0


def move_to_first(id: int) -> int:
	queue: list[int] = get_queue()

	size: int = len(queue)
	if size <= 1:
		return 0

	for x in range(size):
		if queue[x] == id:
			queue.pop(x)
			queue.insert(0, id)
			save_queue(queue)
			return 0

	return ERR_QUEUE_INVALID_ID


def remove_id(id: int) -> int:
	queue: list[int] = get_queue()

	size: int = len(queue)
	if size <= 0:
		return 0

	for x in range(size):
		if queue[x] == id:
			queue.pop(x)
			save_queue(queue)
			return 0

	return ERR_QUEUE_INVALID_ID
