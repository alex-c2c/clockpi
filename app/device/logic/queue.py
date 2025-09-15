from datetime import datetime
import random
from logging import Logger, getLogger

from pytz import timezone

from app import db
from app.consts import *
from app.lib.errors import api_abort, ErrorCode

from ..models import DeviceModel
from ..logic import can_access_device


logger: Logger = getLogger(__name__)


"""""
LOGIC
"""""
	

def shift_next(user_id: int, device_id: int, skip_user_check: bool = False) -> None:
	logger.info(f"Attempting to shift next queue")
	
	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
	
	if not skip_user_check and not can_access_device(user_id, device_id):
		api_abort(ErrorCode.FORBIDDEN)

	queue: list[int] = device.queue
		
	if len(queue) <= 1:
		return

	first: int = queue.pop(0)
	queue.append(first)
	
	db.session.commit()
	
	logger.info(f"Queue shifted")


def shuffle_queue(user_id:int, device_id: int, skip_user_check: bool = False) -> None:
	logger.info(f"Attempting to shuffle queue")
	
	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	if not skip_user_check and not can_access_device(user_id, device_id):
		api_abort(ErrorCode.FORBIDDEN)

	queue: list[int] = device.queue
			
	if len(queue) <= 1:
		return
	
	random.shuffle(queue)
	
	db.session.commit()
	
	logger.info(f"Queue shuffled: {device.queue}")


def append_to_queue(user_id: int, device_id: int, wallpaper_id: int) -> None:
	logger.info(f"Attempting to append {wallpaper_id} to queue")

	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	if not can_access_device(user_id, device_id):
		api_abort(ErrorCode.FORBIDDEN)
	
	queue: list[int] = device.queue
			
	if wallpaper_id in queue:
		logger.warning(f"Duplicate id: {wallpaper_id}")
		return

	queue.append(wallpaper_id)
	device.updated_at = datetime.now(timezone("Asia/Singapore"))
	
	try:
		db.session.commit()
	except Exception as ex:
		db.session.rollback()
		api_abort(ErrorCode.DATABASE_ERROR)
	
	logger.info(f"Queue appended: {device.queue}")


def move_to_first(user_id:int, device_id: int, wallpaper_id: int) -> None:
	logger.info(f"Attempting to move {wallpaper_id} to front of queue")

	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	if not can_access_device(user_id, device_id):
		api_abort(ErrorCode.FORBIDDEN)
	
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
	
	try:
		db.session.commit()
	except Exception as ex:
		db.session.rollback()
		api_abort(ErrorCode.DATABASE_ERROR)
		
	logger.info(f"Moved {wallpaper_id} to front of queue")


def remove_from_queue(user_id: int, device_id: int, wallpaper_id: int) -> None:
	logger.info(f"Attempting to remove {wallpaper_id} from queue")

	device: DeviceModel | None = db.session.get(DeviceModel, device_id)

	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	if not can_access_device(user_id, device_id):
		api_abort(ErrorCode.FORBIDDEN)
	
	queue: list[int] = device.queue
	
	if wallpaper_id not in queue:
		logger.error(f"Unable to find {wallpaper_id} in queue")
		return
		
	size: int = len(queue)
	for x in range(size):
		if queue[x] == wallpaper_id:
			queue.pop(x)
			break
	
	db.session.commit();

	logger.info(f"Removed {wallpaper_id} from queue")
