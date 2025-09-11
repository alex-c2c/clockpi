from datetime import datetime
from pytz import timezone

from sqlalchemy import Boolean, ForeignKey, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column

from app import db

class ScheduleModel(db.Model):
	__tablename__: str = "schedule"

	id: 		Mapped[int]			= mapped_column(Integer, primary_key=True)
	device_id:	Mapped[int]			= mapped_column(ForeignKey("device.id"), nullable=False)
	days: 		Mapped[list[str]]	= mapped_column(MutableList.as_mutable(JSONB), default=list, nullable=False, server_default="[]")
	start_time: Mapped[str] 		= mapped_column(String(), nullable=False)
	duration: 	Mapped[int] 		= mapped_column(Integer, nullable=False)
	is_enabled: Mapped[bool] 		= mapped_column(Boolean, nullable=False, default=True)
	created_at:	Mapped[datetime]	= mapped_column(DateTime, nullable=False, default=datetime.now(timezone("Asia/Singapore")))
	updated_at:	Mapped[datetime] 	= mapped_column(DateTime, nullable=False, default=datetime.now(timezone("Asia/Singapore")))

	def __repr__(self) -> str:
		return f"<Schedule - \
			id:{self.id} \
			device_id:{self.device_id} \
			days:{self.days} \
			start_time:{self.start_time} \
			duration:{self.duration} \
			is_enabled:{self.is_enabled} \
			created_at:{self.created_at} \
			updated_at:{self.updated_at}\
			>"
		
	def get_hour_minute(self) -> tuple[int, int]:
		return (int(self.start_time[0:2]), int(self.start_time[3:5]))

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"days": self.days,
			"startTime": self.start_time,
			"duration": self.duration,
			"isEnabled": self.is_enabled,
		}
