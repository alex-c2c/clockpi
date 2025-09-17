from datetime import datetime
from logging import Logger, getLogger

from pytz import timezone
from sqlalchemy import and_, delete, select

from app import db, redis_controller
from app.consts import *
from app.device.logic import can_access_device
from app.device.models import DeviceModel
from app.lib.errors import api_abort, ErrorCode

from .models import ScheduleModel, ScheduleOwnershipModel
from .utils import *

logger: Logger = getLogger(__name__)


"""""
LOGIC
"""""


def can_access_schedule(user_id: int, device_id: int, schedule_id: int) -> bool:
	stmt = select(ScheduleOwnershipModel).where(
		and_(
			ScheduleOwnershipModel.user_id == user_id,
			ScheduleOwnershipModel.device_id == device_id,
			ScheduleOwnershipModel.schedule_id == schedule_id
			))
	
	if db.session.scalars(stmt).one_or_none() is None:
		return False
		
	return True


def get_schedules(device_id: int) -> list[dict]:
	stmt = select(ScheduleModel).where(ScheduleModel.device_id == device_id)
	models: list[ScheduleModel] = list(db.session.scalars(stmt).all())

	return [model.to_dict() for model in models]


def create_schedule(user_id:int, device_id:int, payload: dict) -> None:
	logger.info(f"Attempting to create new schedule")
		
	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
			
	failed_validations: dict = {}
			
	days: list[str] | None = payload.get("days")
	if  (err := validate_days(days)) is not None:
		failed_validations["days"] = err
	
	start_time: str | None = payload.get("startTime")
	if (err := validate_time(start_time)) is not None:
		failed_validations["startTime"] = err
		
	duration: int | None = payload.get("duration")
	if (err := validate_duration(duration)) is not None:
		failed_validations["duration"] = err
		
	is_enabled: bool | None = payload.get("isEnabled")
	if is_enabled is None:
		failed_validations["isEnabled"] = "This is a required property"
	
	if len(failed_validations.values()) > 0:
		api_abort(ErrorCode.VALIDATION_ERROR, errors=failed_validations)
	
	sm = ScheduleModel()
	sm.device_id = device_id
	sm.days = days				# type: ignore
	sm.start_time = start_time	# type: ignore
	sm.duration = duration		# type: ignore
	sm.is_enabled = is_enabled # type: ignore
	
	db.session.add(sm)
	db.session.flush()
	
	som = ScheduleOwnershipModel()
	som.schedule_id = sm.id
	som.user_id = user_id
	som.device_id = device_id
	
	db.session.add(som)
	db.session.flush()
	
	try:
		db.session.commit()
	except Exception as ex:
		logger.error(f"DB commit failed: {ex}")
		api_abort(ErrorCode.DATABASE_ERROR)
	
	logger.info(f"Created new schedule {sm.id}")


def delete_schedule(schedule_id: int) -> None:
	logger.info(f"Attempting to delete schedule:{schedule_id}")
	
	# Delete ownership first due to ForeignKey
	db.session.execute(delete(ScheduleOwnershipModel).where(ScheduleOwnershipModel.schedule_id == schedule_id))
	db.session.flush()
	
	# Delete schedule
	db.session.execute(delete(ScheduleModel).where(ScheduleModel.id == schedule_id))
	db.session.flush()
	
	try:
		db.session.commit()
	except Exception as ex:
		db.session.rollback()
		logger.error(f"DB commit failed: {ex}")
		api_abort(ErrorCode.DATABASE_ERROR)
		
	logger.info(f"Deleted schedule:{schedule_id}")


def update_schedule(schedule_id: int, payload: dict) -> None:
	logger.info(f"Attempting to update schedule")
	
	schedule: ScheduleModel | None = db.session.get(ScheduleModel, schedule_id)
	if schedule is None:
		api_abort(ErrorCode.SCHEDULE_NOT_FOUND)
			
	failed_validations: dict = {}
	
	days: list[str] | None = payload.get("days", None)
	if days is not None:
		if (err := validate_days(days)) is not None:
			failed_validations["days"] = err
		else:
			schedule.days = days
			
	start_time: str | None = payload.get("startTime")
	if start_time is not None:
		if  (err := validate_time(start_time)) is not None:
			failed_validations["startTime"] = err
		else:
			schedule.start_time = start_time
		
	duration: int | None = payload.get("duration")
	if duration is not None:
		if (err := validate_duration(duration)) is not None:
			failed_validations["duration"] = err
		else:
			schedule.duration = duration
		
	is_enabled: bool | None = payload.get("isEnabled")
	if is_enabled is not None:
		schedule.is_enabled = is_enabled
		
	if len(failed_validations.values()) > 0:
		api_abort(ErrorCode.VALIDATION_ERROR, errors=failed_validations)

	schedule.updated_at = datetime.now(timezone("Asia/Singapore"))

	try:
		db.session.commit()
	except Exception as ex:
		logger.error(f"DB commit failed: {ex}")
		api_abort(ErrorCode.DATABASE_ERROR)
	
	logger.info(f"Updated schedule {schedule_id}")


def get_status(device_id: int) -> SleepStatus:
	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	key: str = f"{R_SLEEP_STATUS}_{device.ipv4}"
	value: str = redis_controller.rget(key, SleepStatus.AWAKE.value)
	
	return SleepStatus[value]


def set_status(device_id:int, status: SleepStatus) -> None:
	logger.debug(f"set_status:{status=}")

	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	key:str = f"{R_SLEEP_STATUS}_{device.ipv4}"
	
	redis_controller.rset(key, value=status.value)


def should_sleep_now(device_id: int) -> bool:
	stmt = select(ScheduleModel).where(ScheduleModel.device_id == device_id)
	schedules: list[ScheduleModel] = list(db.session.scalars(stmt).all())
	minute_ranges: list = []

	for sch in schedules:
		if not sch.is_enabled:
			continue
		
		hour, minute = sch.get_hour_minute()

		for x in range(len(sch.days)):
			if sch.days[x]:
				s: int = (x * 1440) + (hour * 60) + minute
				e: int = s + sch.duration
				if e > 10080:
					e = 10080
					minute_ranges.append((0, e % 10080))
				minute_ranges.append((s, e))

	minute_ranges.sort(key=lambda x: (x[0], x[1]))

	minute_now: int = (
		datetime.now().today().weekday() * 1440
		+ datetime.now().hour * 60
		+ datetime.now().minute
	)

	for minute_range in minute_ranges:
		if minute_now < minute_range[0]:
			return False
		elif minute_range[0] <= minute_now < minute_range[1]:
			return True
		else:
			pass

	return False
