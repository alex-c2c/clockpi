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

	def __init__(self):
		self.id = 0
		self.days = (False, False, False, False, False, False, False)
		self.hour = 0
		self.minute = 0
		self.duration = 0


def validate(hour: int, minute: int, duration: int) -> int:
	invalid: bool = False

	if hour < 0 or hour > 23:
		logger.error(f"Invalid hour, {hour=}")
		invalid = True

	if minute < 0 or minute > 59:
		logger.error(f"Invalid minute, {minute=}")
		invalid = True

	if duration < 0:
		logger.error(f"Invalid duration, {duration=}")
		invalid = True

	if invalid:
		return ERR_SCH_INVALID_DATA

	return 0


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

		schedules.append(sch)

	return schedules


def add(
	days: tuple[bool, bool, bool, bool, bool, bool, bool],
	hour: int,
	minute: int,
	duration: int,
) -> int:
	logger.info(f"Add {days=} {hour=} {minute=} {duration=}")

	# validate inputs
	result: int = validate(hour, minute, duration)
	if result != 0:
		return result

	# Add to DB
	new_model: SleepScheduleModel = SleepScheduleModel(
		days=days, hour=hour, minute=minute, duration=duration
	)
	db.session.add(new_model)
	db.session.commit()


def remove(id: int) -> None:
	logger.info(f"Remove {id=}")

	# Remove from DB
	model: SleepScheduleModel = SleepScheduleModel.query.get(id)
	db.session.delete(model)
	db.session.commit()


def update(
	id: int,
	days: tuple[bool, bool, bool, bool, bool, bool, bool],
	hour: int,
	minute: int,
	duration: int,
) -> bool:
	logger.info(f"Update {id=} {days=} {hour=} {minute=} {duration=}")

	# Validate inputs
	result: int = validate(hour, minute, duration)
	if result != 0:
		return result

	# Update DB
	model: SleepScheduleModel = SleepScheduleModel.query.get(id)
	if model is not None:
		model.days = "^".join("1" if d else "0" for d in days)
		model.hour = hour
		model.minute = minute
		model.duration = duration
		db.session.commit()

	return True


def get_status() -> SleepStatus:
	return SleepStatus(
		int(redis_controller.rget(R_SLEEP_STATUS, str(SleepStatus.AWAKE.value)))
	)


def set_status(status: SleepStatus) -> None:
	logger.debug(f"set_status:{status=}")
	redis_controller.rset(R_SLEEP_STATUS, value=str(status.value))


def should_sleep_now() -> bool:
	minute_ranges: list = []
	schedules: list[SleepSchedule] = get_schedules()

	for sch in schedules:
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
