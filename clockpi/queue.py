import random
from clockpi import db, redis_controller
from clockpi.consts import *
from logging import Logger, getLogger


logger: Logger = getLogger(__name__)


def generate_initial_queue() -> None:
	images = db.get_images()
	queue: list[int] = []

	for img in images:
		queue.append(img["id"])

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


def append_to_queue(id: int) -> None:
	queue: list[int] = get_queue()
	queue.append(id)
	save_queue(queue)


def move_to_first(id: int) -> None:
	queue: list[int] = get_queue()

	size: int = len(queue)
	if size <= 1:
		return

	for x in range(size):
		if queue[x] == id:
			queue.pop(x)
			queue.insert(0, id)
			return

	save_queue(queue)


def remove_id(id: int) -> None:
	queue: list[int] = get_queue()

	size: int = len(queue)
	if size <= 0:
		return

	for x in range(size):
		if queue[x] == id:
			queue.pop(x)
			break

	save_queue(queue)


def remove_index(index: int) -> None:
	queue: int = get_queue()

	size: int = len(queue)
	if size <= 0:
		return

	queue.pop(index)
	save_queue(queue)
