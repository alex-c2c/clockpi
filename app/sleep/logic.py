from dataclasses import dataclass
from datetime import datetime
from logging import Logger, getLogger


from app.consts import *
from app import db, redis_controller
from app.models import SleepScheduleModel


logger: Logger = getLogger(__name__)


@dataclass
class SleepSchedule:
	id: int
	days: tuple
	hour: int
	minute: int
	duration: int
	enabled: bool

	def __init__(self):
		self.id = 0
		self.days = (False, False, False, False, False, False, False)
		self.hour = 0
		self.minute = 0
		self.duration = 0
		self.enabled = True

	def to_dict(self) -> dict:
		d: dict = {}
		d["id"] = self.id
		d["days"] = self.days
		d["hour"] = self.hour
		d["minute"] = self.minute
		d["duration"] = self.duration
		d["enabled"] = self.enabled
		return d


def validate_hour(hour: int) -> bool:
	return hour >= 0 and hour < 24


def validate_minute(minute: int) -> int:
	return minute >= 0 and minute < 60


def validate_duration(duration: int) -> int:
	return duration >= 0 and duration <= 1440


def get_schedules() -> list[SleepSchedule]:
	schedules: list[SleepSchedule] = []
	data: list = SleepScheduleModel.query.order_by(SleepScheduleModel.id).all()

	for model in data:
		sch = SleepSchedule()
		sch.days = tuple(True if day == "1" else False for day in model.days.split("^"))
		sch.id = model.id
		sch.hour = model.hour
		sch.minute = model.minute
		sch.duration = model.duration
		sch.enabled = model.enabled

		schedules.append(sch)

	return schedules


def add(
	mon: bool,
	tue: bool,
	wed: bool,
	thu: bool,
	fri: bool,
	sat: bool,
	sun: bool,
	hour: int,
	minute: int,
	duration: int,
	enabled: bool = True,
) -> int:
	logger.info(
		f"Add {mon=} {tue=} {wed=} {thu=} {fri=} {sat=} {sun=} {hour=} {minute=} {duration=} {enabled=}"
	)

	# validate inputs
	if (
		not validate_hour(hour)
		or not validate_minute(minute)
		or not validate_duration(duration)
	):
		return ERR_SLEEP_INVALID_DATA

	# Add to DB
	days: tuple = (mon, tue, wed, thu, fri, sat, sun)
	new_model: SleepScheduleModel = SleepScheduleModel(
		days="^".join("1" if d else "0" for d in days),
		hour=hour,
		minute=minute,
		duration=duration,
	)
	db.session.add(new_model)
	db.session.commit()

	return 0


def remove(id: int) -> int:
	logger.info(f"Remove {id=}")

	# Remove from DB
	model: SleepScheduleModel | None = SleepScheduleModel.query.get(id)
	if model is None:
		return ERR_SLEEP_INVALID_ID

	db.session.delete(model)
	db.session.commit()

	return 0


def update(
	id: int,
	mon: bool | None,
	tue: bool | None,
	wed: bool | None,
	thu: bool | None,
	fri: bool | None,
	sat: bool | None,
	sun: bool | None,
	hour: int | None,
	minute: int | None,
	duration: int | None,
	enabled: bool | None,
) -> int:
	logger.info(
		f"Update {id=} {mon=} {tue=} {wed=} {thu=} {fri=} {sat=} {sun=} {hour=} {minute=} {duration=} {enabled=}"
	)

	# Update DB
	model: SleepScheduleModel = SleepScheduleModel.query.get(id)
	if model is None:
		return ERR_SLEEP_INVALID_ID

	days: list = [True if d == "1" else False for d in model.days.split("^")]
	if mon is not None:
		days[0] = mon
	if tue is not None:
		days[1] = tue
	if wed is not None:
		days[2] = wed
	if thu is not None:
		days[3] = thu
	if fri is not None:
		days[4] = fri
	if sat is not None:
		days[5] = sat
	if sun is not None:
		days[6] = sun

	model.days = "^".join("1" if d else "0" for d in days)

	if hour is not None:
		if validate_hour(hour):
			model.hour = hour
		else:
			return ERR_SLEEP_INVALID_DATA

	if minute is not None:
		if validate_minute(minute):
			model.minute = minute
		else:
			return ERR_SLEEP_INVALID_DATA

	if duration is not None:
		if validate_duration(duration):
			model.duration = duration
		else:
			return ERR_SLEEP_INVALID_DATA

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

		for x in range(len(sch.days)):
			if sch.days[x]:
				s: int = (x * 1440) + (sch.hour * 60) + sch.minute
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
