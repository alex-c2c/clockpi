from logging import Logger, getLogger
from typing import Sequence
from sqlalchemy import select

from app import db
from app.consts import SleepStatus
from app.device.logic.display import clear_display, update_display
from app.device.logic.queue import shift_next, shuffle_queue
from app.device.models import DeviceModel
from app.schedule.logic import get_status, set_status, should_sleep_now


logger: Logger = getLogger(__name__)


def _tick_device(device_id: int) -> None:
	sleep_status: SleepStatus = get_status(device_id)
	is_sleep: bool = should_sleep_now(device_id)

	if is_sleep:
		if sleep_status == SleepStatus.AWAKE:
			clear_display(device_id)
			set_status(device_id, SleepStatus.SLEEP)
	else:
		update_display(device_id)
		if sleep_status == SleepStatus.SLEEP:
			set_status(device_id, SleepStatus.SLEEP)
	

def tick_all() -> None:
	devices: Sequence[DeviceModel] = db.session.scalars(select(DeviceModel)).all()
	for device in devices:
		logger.info(f"ticking device ({device.id})")
		_tick_device(device.id)


def shuffle_all_queue() -> None:
	devices: Sequence[DeviceModel] = db.session.scalars(select(DeviceModel)).all()
	for device in devices:
		logger.info(f"shuffling device ({device.id}) queue")	
		shuffle_queue(device.id)
	

def next_all_queue() -> None:
	devices: Sequence[DeviceModel] = db.session.scalars(select(DeviceModel)).all()
	for device in devices:
		logger.info(f"shuffling device ({device.id}) queue")	
		shift_next(device.id)

