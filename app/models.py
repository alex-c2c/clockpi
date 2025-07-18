from sqlalchemy import ForeignKey

from app.consts import *
from app.epd.consts import *
from . import db


class AccountModel(db.Model):
	__tablename__: str = "account"

	id: int = db.Column(db.Integer, primary_key=True)
	username: str = db.Column(db.String(), unique=True, nullable=False)
	password: str = db.Column(db.String(), nullable=False)
	display_name: str = db.Column(db.String(), nullable=False, server_default="User")

	def __init__(self, username: str, password: str, display_name: str) -> None:
		self.username = username
		self.password = password
		self.display_name = display_name

	def __repr__(self) -> str:
		return f"<Account username:{self.username} | display_name:{self.display_name}>"


class ApiKeyModel(db.Model):
	__tablename__: str = "apikey"
	
	id: int = db.Column(db.Integer, primary_key=True)
	acct_id: int = db.Column(db.Integer, ForeignKey("account.id"), nullable=False)
	key: str = db.Column(db.String(), unique=True, nullable=False)
	comment:str = db.Column(db.String(), nullable=True)
	
	def __init__(self, acct_id: int, key: str, comment: str) -> None:
		self.acct_id = acct_id
		self.key = key
		self.comment = comment
  
	def __repr__(self) -> str:
		return f"<ApiKey key:{self.key}>"


class SleepScheduleModel(db.Model):
	__tablename__: str = "sleep_schedule"

	id: int = db.Column(db.Integer, primary_key=True)
	days: int = db.Column(db.String(), nullable=False)
	hour: int = db.Column(db.Integer, nullable=False)
	minute: int = db.Column(db.Integer, nullable=False)
	duration: int = db.Column(db.Integer, nullable=False)
	enabled: bool = db.Column(db.Boolean, default=True)

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

	id: int = db.Column(db.Integer, primary_key=True)
	name: str = db.Column(db.String(), nullable=False)
	hash: str = db.Column(db.String(), nullable=False)
	size: int = db.Column(db.Integer, nullable=False)
	mode: int = db.Column(db.Integer, nullable=False)
	color: int = db.Column(db.Integer, nullable=False)
	shadow: int = db.Column(db.Integer, nullable=False)

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
