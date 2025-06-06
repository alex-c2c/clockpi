from sqlalchemy import ForeignKey

from app.consts import *
from app.epd.consts import *
from . import db


class AccountModel(db.Model):
	__tablename__: str = "account"

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(), unique=True, nullable=False)
	password = db.Column(db.String(), nullable=False)

	def __init__(self, username, password) -> None:
		self.username = username
		self.password = password

	def __repr__(self) -> str:
		return f"<Account username:{self.username}>"


class ApiKeyModel(db.Model):
	__tablename__: str = "apikey"
	
	id = db.Column(db.Integer, primary_key=True)
	acct_id = db.Column(db.Integer, ForeignKey("account.id"), nullable=False)
	key = db.Column(db.String(), unique=True, nullable=False)
	comment = db.Column(db.String(), nullable=True)
	
	def __init__(self, acct_id: int, key: str, comment: str) -> None:
		self.acct_id = acct_id
		self.key = key
		self.comment = comment
  
	def __repr__(self) -> str:
		return f"<ApiKey key:{self.key}>"


class SleepScheduleModel(db.Model):
	__tablename__: str = "sleep_schedule"

	id = db.Column(db.Integer, primary_key=True)
	days = db.Column(db.String(), nullable=False)
	hour = db.Column(db.Integer, nullable=False)
	minute = db.Column(db.Integer, nullable=False)
	duration = db.Column(db.Integer, nullable=False)
	enabled = db.Column(db.Boolean, default=True)

	def __init__(self, days: int, hour: int, minute: int, duration: int, enabled: bool = True):
		self.days = days
		self.hour = hour
		self.minute = minute
		self.duration = duration
		self.enabled = enabled

	def __repr__(self):
		return f"<SleepSchedule days:{self.days} hour:{self.hour} minute:{self.minute} duration:{self.duration} enabled:{self.enabled}>"


class WallpaperModel(db.Model):
	__tablename__: str = "wallpaper"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(), nullable=False)
	hash = db.Column(db.String(), nullable=False)
	size = db.Column(db.Integer, nullable=False)
	mode = db.Column(db.Integer, nullable=False)
	color = db.Column(db.Integer, nullable=False)
	shadow = db.Column(db.Integer, nullable=False)

	def __init__(
		self,
		name: str,
		hash: str,
		size: int,
		mode: int | None = None,
		color: int | None = None,
		shadow: int | None = None,
	):
		self.name = name
		self.hash = hash
		self.size = size
		self.mode = TIMEMODE_FULL_3 if mode is None else mode
		self.color = COLOR_EPD_WHITE if color is None else color
		self.shadow = COLOR_EPD_BLACK if shadow is None else shadow
  
	def to_dict(self) -> dict:
		d: dict = {}
		d["id"] = self.id
		d["name"] = self.name
		d["hash"] = self.hash
		d["size"] = self.size
		d["mode"] = self.mode
		d["color"] = self.color
		d["shadow"] = self.shadow
		return d

	def __repr__(self):
		return f"<Wallpaper name:{self.name} hash:{self.hash} size:{self.size} mode:{self.mode} color:{self.color} shadow:{self.shadow}>"
