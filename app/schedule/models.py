from sqlalchemy.orm import Mapped

from app import db

class ScheduleModel(db.Model):
	__tablename__: str = "schedule"

	id: Mapped[int]				= db.Column(db.Integer, primary_key=True)
	days: Mapped[str]			= db.Column(db.String(), nullable=False)
	start_time: Mapped[str] 	= db.Column(db.String(), nullable=False)
	duration: Mapped[int] 		= db.Column(db.Integer, nullable=False)
	is_enabled: Mapped[bool] 	= db.Column(db.Boolean, default=True)

	def __init__(self, days: str, start_time: str, duration: int, is_enabled: bool = True):
		self.days		= days
		self.start_time = start_time
		self.duration 	= duration
		self.is_enabled = is_enabled

	def __repr__(self) -> str:
		return f"<Schedule - id:{self.id} days:{self.days} start_time:{self.start_time} duration:{self.duration} is_enabled:{self.is_enabled}>"
		
	def get_hour_minute(self) -> tuple[int, int]:
		return (int(self.start_time[0:2]), int(self.start_time[3:5]))

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"days": [day.lower() for day in self.days.split(",") if len(self.days) > 0],
			"startTime": self.start_time,
			"duration": self.duration,
			"isEnabled": self.is_enabled,
		}
