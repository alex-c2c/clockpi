from dataclasses import dataclass
from datetime import datetime
from faulthandler import is_enabled
from logging import Logger, getLogger


from app import db, redis_controller
from app.consts import *

from . import ns
from .consts import DAYS_OF_WEEK
from .models import SleepModel

logger: Logger = getLogger(__name__)


"""""
LOGIC
"""""

@dataclass
class SleepSchedule:
	id: int
	days: tuple[str]
	start_time: str
	duration: int
	enabled: bool

	def __init__(self):
		self.id = 0
		self.days = tuple()
		self.start_time = "12:00"
		self.duration = 1
		self.enabled = False

	def to_dict(self) -> dict:
		d: dict = {}
		d["id"] = self.id
		d["days"] = self.days
		d["startTime"] = self.start_time
		d["duration"] = self.duration
		d["isEnabled"] = self.enabled
		return d


def split_time(time: str) -> tuple[bool, int, int]:
	if len(time) != 5:
		return True, 0, 0
	
	return True, int(time[0:2]), int(time[3:5])


def validate_hour(hour: int) -> bool:
	return hour >= 0 and hour < 24


def validate_minute(minute: int) -> bool:
	return minute >= 0 and minute < 60


def validate_time(time: str | None) -> bool:
	if time is None:
		return False
		
	if len(time) != 5:
		return False
	
	if time[2] != ":":
		return False
		
	try:
		hour: int = int(time[0:2])
		if hour < 0 or hour > 23:
			return False
	except Exception as e:
		return False
	
	try:
		minute: int = int(time[3:5])
		if minute < 0 or minute > 59:
			return False
	except Exception as e:
		return False
	
	return True


def validate_duration(duration: int | None) -> bool:
	if duration is None:
		return False
		
	return duration >= 1 and duration <= 1440


def validate_days_str(days_str: str | None) -> bool:
	if days_str is None:
		return False
		
	days: list[str] = days_str.split(",")
	return validate_days(days)


def validate_days(days: list[str] | None) -> bool:
	if days is None:
		return False
		
	if len(days) > 7:
		return False
	
	for day in days:
		if day.lower() not in DAYS_OF_WEEK:
			return False
	
	return True


def get_schedules() -> list[dict]:
	schedules: list[dict] = []
	data: list = SleepModel.query.all()

	for model in data:
		schedules.append(model.to_dict())

	return schedules


def create_schedule(data: dict) -> None:
	logger.info(f"Attempting to create new sleep schedule")
	
	days: list[str] = data.get("days", [])
	if not validate_days(days):
		ns.abort(400, "Invalid days")
		return
	
	start_time: str = data.get("startTime", "")
	if not validate_time(start_time):
		ns.abort(400, "Invalid startTime")
		return
		
	duration: int = data.get("duration", -1)
	if not validate_duration(duration):
		ns.abort(400, "Invalid duration")
		return
		
	is_enabled: bool | None = data.get("isEnabled")
	if is_enabled is None:
		ns.abort(400, "Invalid isEnabled")
		return
	
	new_schedule = SleepModel(
		days=",".join(day.lower() for day in days),
		start_time=start_time,
		duration=duration,
		is_enabled=is_enabled
	)
	
	try:
		db.session.add(new_schedule)
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to create new sleep schedule due to {e}")
		ns.abort(500, "Server error occured")
		return
	
	logger.info(f"Created new sleep schedule {new_schedule.id}")


def delete_schedule(id: int) -> None:
	logger.info(f"Attempting to delete schedule:{id}")
	
	schedule: SleepModel | None = db.session.get(SleepModel, id)
	if schedule is None:
		ns.abort(404, "Missing or invalid ID")
		return
	
	try:
		db.session.delete(schedule)
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to delete sleep schedule {id} due to {e}")
		ns.abort(500, "Server error occured")
		return
		
	logger.info(f"Deleted sleep schedule:{id}")


def update_schedule(id: int, data: dict) -> None:
	logger.info(f"Attempting to update sleep schedule")
	
	schedule: SleepModel | None = db.session.get(SleepModel, id)
	if schedule is None:
		ns.abort(404, "Missing or invalid ID")
		return
	
	days: list[str] | None = data.get("days", None)
	if days is not None:
		if not validate_days(days):
			ns.abort(400, "Invalid days")
			return
		schedule.days = ",".join(set(day.lower() for day in days))
			
	start_time: str | None = data.get("startTime")
	if start_time is not None:
		if not validate_time(start_time):
			ns.abort(400, "Invalid startTime")
			return
		
		schedule.start_time = start_time
		
	duration: int | None = data.get("duration")
	if duration is not None:
		if not validate_duration(duration):
			ns.abort(400, "Invalid duration")
			return
			
		schedule.duration = duration
		
	is_enabled: bool | None = data.get("isEnabled")
	if is_enabled is not None:
		schedule.is_enabled = is_enabled

	try:
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to update sleep schedule due to {e}")
		ns.abort(500, "Server error occured")
		return
	
	logger.info(f"Updated sleep schedule {id}")


def get_status() -> int:
	return int(redis_controller.rget(R_SLEEP_STATUS, str(SLEEP_STATUS_AWAKE)))


def set_status(status: int) -> None:
	logger.debug(f"set_status:{status=}")
	redis_controller.rset(R_SLEEP_STATUS, value=str(status))


def should_sleep_now() -> bool:
	minute_ranges: list = []
	schedules: list[SleepModel] = SleepModel.query.all()

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
