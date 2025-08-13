import random
from logging import Logger, getLogger

from sqlalchemy import select

from . import ns

from app import db
from app.consts import *
from app.queue.models import QueueModel
from app.wallpaper.models import WallpaperModel


logger: Logger = getLogger(__name__)

"""""
LOGIC
"""""

def get_queue_model() -> QueueModel:
	models = db.session.scalars(select(QueueModel)).all()
	if len(models) == 0:
		ns.abort(500, "Queue not found!")
	
	return models[0]
	

def generate_initial_queue() -> None:
	wallpapers: list = WallpaperModel.query.all()
	queue: list[int] = []

	for model in wallpapers:
		queue.append(model.id)

	random.shuffle(queue)

	#save_queue(queue)
	

def validate_queue(data: list[int]) -> None:
	for id in data:
		if not isinstance(id, int):
			ns.abort(400, "Invalid data in queue")
			return
		
		if not db.session.get(WallpaperModel, id):
			ns.abort(404, "Invalid or missing wallpaper ID")
			return


def save_queue(model: QueueModel, data: list[int]) -> None:
	logger.debug(f"Attemping to save_queue {data=}")
	
	model.queue = ",".join(str(id) for id in data)
	
	try:
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to save queue {data} due to {e}")
		ns.abort(500, "Internal Server Error")
		return
	
	logger.info(f"Queue {data=} saved")


def shift_next() -> None:
	logger.info(f"Attempting to shift next queue")
	
	model: QueueModel = get_queue_model()
	queue: list[int] = model.get_queue()
	
	if len(queue) <= 1:
		return

	first: int = queue.pop(0)
	queue.append(first)
	
	save_queue(model, queue)
		
	logger.info(f"Queue shifted")


def get_current_id() -> int:
	queue: list[int] = get_queue_model().get_queue()

	if len(queue) > 0:
		return queue[0]

	return 0


def shuffle_queue() -> None:
	logger.info(f"Attempting to shuffle queue")
	
	model: QueueModel = get_queue_model()
	queue: list[int] = model.get_queue()
	
	random.shuffle(queue)
	
	save_queue(model, queue)

	logger.info(f"Queue shuffled: {model.get_queue()}")


def append_to_queue(id: int) -> None:
	logger.info(f"Attempting to append {id} to queue")
	
	model: QueueModel = get_queue_model()
	queue: list[int] = model.get_queue()
	
	if id in queue:
		logger.error(f"Duplicate id: {id}")
		ns.abort(415, "Duplicate ID found")
		return

	queue.append(id)
	
	save_queue(model, queue)
	
	logger.info(f"Queue appended: {model.queue}")


def move_to_first(id: int | None) -> None:
	logger.info(f"Attempting to move {id} to front of queue")
	
	model: QueueModel = get_queue_model()
	queue: list[int] = model.get_queue()
	
	if id not in queue:
		logger.error(f"Unable to find {id} in queue")
		ns.abort(404, "Invalid or missing ID")
		return
	
	size: int = len(queue)
	for x in range(size):
		if queue[x] == id:
			queue.pop(x)
			queue.insert(0, id)
			break
			
	save_queue(model, queue)

	logger.info(f"Moved {id} to front of queue")


def remove_from_queue(id: int) -> None:
	logger.info(f"Attempting to remove {id} from queue")
	
	model: QueueModel = get_queue_model()
	queue: list[int] = model.get_queue()

	if id not in queue:
		logger.error(f"Unable to find {id} in queue")
		ns.abort(404, "Missing or invalid ID")
		return
		
	size: int = len(queue)
	for x in range(size):
		if queue[x] == id:
			queue.pop(x)
			break
	
	save_queue(model, queue)

	logger.info(f"Removed {id} from queue")
