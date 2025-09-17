import random

from datetime import datetime
from logging import Logger, getLogger
from pytz import timezone

from app import db
from app.consts import *
from app.lib.errors import api_abort, ErrorCode

from ..models import DeviceModel


logger: Logger = getLogger(__name__)


"""""
LOGIC
"""""


def shift_next(device_id: int) -> None:
	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
	
	queue: list[int] = device.queue

	if len(queue) <= 1:
		return

	first: int = queue.pop(0)
	queue.append(first)
	
	device.updated_at = datetime.now(timezone("Asia/Singapore"))
	
	try:
		db.session.commit()
	except Exception as ex:
		logger.error(f"DB commit failed: {ex}")
		api_abort(ErrorCode.DATABASE_ERROR)
	
	logger.info(f"Queue shifted")


def shuffle_queue(device_id: int) -> None:
	logger.info(f"Attempting to shuffle queue")
	
	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	queue: list[int] = device.queue
			
	if len(queue) <= 1:
		return
	
	random.shuffle(queue)
	
	device.updated_at = datetime.now(timezone("Asia/Singapore"))
	
	try:
		db.session.commit()
	except Exception as ex:
		logger.error(f"DB commit failed: {ex}")
		api_abort(ErrorCode.DATABASE_ERROR)		
	
	logger.info(f"Queue shuffled: {device.queue}")


def append_to_queue(device_id: int, wallpaper_id: int) -> None:
	logger.info(f"Attempting to append {wallpaper_id} to queue")

	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	queue: list[int] = device.queue
			
	if wallpaper_id in queue:
		logger.warning(f"Duplicate id: {wallpaper_id}")
		return

	queue.append(wallpaper_id)
	
	device.updated_at = datetime.now(timezone("Asia/Singapore"))
	
	try:
		db.session.commit()
	except Exception as ex:
		logger.error(f"DB commit failed: {ex}")
		api_abort(ErrorCode.DATABASE_ERROR)
	
	logger.info(f"Queue appended: {device.queue}")


def move_to_first(device_id: int, wallpaper_id: int) -> None:
	logger.info(f"Attempting to move {wallpaper_id} to front of queue")

	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
			
	queue: list[int] = device.queue
			
	if wallpaper_id not in queue:
		logger.error(f"Unable to find {wallpaper_id} in queue")
		return
			
	size: int = len(queue)
	for x in range(size):
		if queue[x] == wallpaper_id:
			queue.pop(x)
			queue.insert(0, wallpaper_id)
			break

	device.updated_at = datetime.now(timezone("Asia/Singapore"))
	
	try:
		db.session.commit()
	except Exception as ex:
		logger.error(f"DB commit failed: {ex}")
		api_abort(ErrorCode.DATABASE_ERROR)
		
	logger.info(f"Moved {wallpaper_id} to front of queue")


def remove_from_queue(device_id: int, wallpaper_id: int) -> None:
	logger.info(f"Attempting to remove {wallpaper_id} from queue")

	device: DeviceModel | None = db.session.get(DeviceModel, device_id)

	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
			
	queue: list[int] = device.queue
	
	if wallpaper_id not in queue:
		logger.error(f"Unable to find {wallpaper_id} in queue")
		return
		
	size: int = len(queue)
	for x in range(size):
		if queue[x] == wallpaper_id:
			queue.pop(x)
			break
	
	device.updated_at = datetime.now(timezone("Asia/Singapore"))
	
	try:
		db.session.commit()
	except Exception as ex:
		db.session.rollback()
		logger.error(f"DB commit failed: {ex}")
		api_abort(ErrorCode.DATABASE_ERROR)

	logger.info(f"Removed {wallpaper_id} from queue")
