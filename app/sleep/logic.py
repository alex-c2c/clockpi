from dataclasses import dataclass
from datetime import datetime
from logging import Logger, getLogger


from app import db, redis_controller
from app.consts import *

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


def validate_duration(duration: int) -> bool:
	return duration >= 1 and duration <= 1440


def validate_days(days: tuple [str]) -> bool:
    if len(days) > 7:
        return False
    
    for day in days:
        if day.lower() not in DAYS_OF_WEEK:
            return False
    
    return True


def get_schedules() -> list[SleepSchedule]:
	schedules: list[SleepSchedule] = []
	data: list = SleepModel.query.all()

	for model in data:
		sch = SleepSchedule()
		sch.days = tuple(d for d in model.days.split(",") if len(d) != 0)
		sch.id = model.id
		sch.start_time = f"{model.hour:02}:{model.minute:02}"
		sch.duration = model.duration
		sch.enabled = model.enabled

		schedules.append(sch)

	return schedules


def add(
    start_time: str,
	duration: int,
	days: tuple[str],
) -> int:
	logger.info(f"Add {start_time=} {duration=} {days=}")
 
	# pre-validate start_time
	res, hour, minute = split_time(start_time)
	if not res:
		return ERR_SLEEP_INVALID_DATA

	# validate inputs
	if (
		not validate_hour(hour)
		or not validate_minute(minute)
		or not validate_duration(duration)
		or not validate_days(days)
	):
		return ERR_SLEEP_INVALID_DATA

	# Add to DB
	new_model: SleepModel = SleepModel(
		days=",".join(day.lower() for day in days),
		hour=hour,
		minute=minute,
		duration=duration,
		enabled=True
	)
	db.session.add(new_model)
	db.session.commit()

	return 0


def remove(id: int) -> int:
	logger.info(f"Remove {id=}")

	# Remove from DB
	model: SleepModel | None = SleepModel.query.get(id)
	if model is None:
		return ERR_SLEEP_INVALID_ID

	db.session.delete(model)
	db.session.commit()

	return 0


def update(
    id: int | None,
    start_time : str | None,
	duration: int | None,
	days: tuple[str] | None,
	enabled: bool | None,
) -> int:
	logger.info(
	logger.info(f"Update {id=} {start_time=} {duration=} {days=} {enabled=}")
	)

	if id is None:
		return ERR_QUEUE_INVALID_ID

	# Update DB
	model: SleepModel | None = SleepModel.query.get(id)
	if model is None:
		return ERR_SLEEP_INVALID_ID

	if start_time is not None:
		res, hour, minute = split_time(start_time)
		if not res:
			return ERR_SLEEP_INVALID_DATA

		if not validate_hour(hour) or not validate_minute(minute):
			return ERR_SLEEP_INVALID_DATA

		model.hour = hour
		model.minute = minute
  
	if duration is not None:
		if not validate_duration(duration):
			return ERR_SLEEP_INVALID_DATA

		model.duration = duration
  
	if days is not None:
		if not validate_days(days):
			return ERR_SLEEP_INVALID_DATA

		model.days = ",".join(day.lower() for day in days)
	
	if enabled is not None:
		model.enabled = enabled

	db.session.commit()

	return 0


def get_status() -> int:
	return int(redis_controller.rget(R_SLEEP_STATUS, str(SLEEP_STATUS_AWAKE)))


def set_status(status: int) -> None:
	logger.debug(f"set_status:{status=}")
	redis_controller.rset(R_SLEEP_STATUS, value=str(status))


def should_sleep_now() -> bool:
	minute_ranges: list = []
	schedules: list[SleepSchedule] = get_schedules()

	for sch in schedules:
		if not sch.enabled:
			continue
		
		hour: int = int(sch.start_time[0:2])
		minute: int = int(sch.start_time[3:5])

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
