from .consts import DAYS_OF_WEEK

def validate_time(time: str | None) -> str | None:
	if time is None:
		return "This is a required field"
		
	if len(time) != 5:
		return "Wrong format (HH:MM)"
	
	if time[2] != ":":
		return "Wrong format (HH:MM)"
		
	try:
		hour: int = int(time[0:2])
		if hour < 0 or hour > 23:
			return "Invalid hour (0 >= hour < 24)"
	except Exception as e:
		return "Invalid input (hour)"
	
	try:
		minute: int = int(time[3:5])
		if minute < 0 or minute > 59:
			return "Invalid minute (0 >= minute < 60)"
	except Exception as e:
		return "Invalid input (minute)"
	
	return None


def validate_duration(duration: int | None) -> str | None:
	if duration is None:
		return "This is a required field"
		
	if duration < 1 or duration > 1440:
		return "Invalid input (1 >= duration <= 1440)"
		
	return None


def validate_days(days: list[str] | None) -> str | None:
	if days is None:
		return "This is a required field"
		
	if len(days) > 7:
		return "Maximum of 7 days"
	
	for day in days:
		if day not in DAYS_OF_WEEK:
			return "Invalid day"
	
	return None
