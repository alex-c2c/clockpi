from . import db


class AccountModel(db.Model):
	__tablename__: str = "account"
 
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(), unique=True, nullable=False)
	password = db.Column(db.String(), nullable=False)
	
	def __init__(self, username, password):
		self.username = username
		self.password = password

	def __repr__(self):
		return f"<Account username:{self.username}>"


class SleepScheduleModel(db.Model):
	__tablename__: str = "sleep_schedule"
	
	id = db.Column(db.Integer, primary_key=True)
	days = db.Column(db.String(), nullable=False)
	hour = db.Column(db.Integer, nullable=False)
	minute = db.Column(db.Integer, nullable=False)
	duration = db.Column(db.Integer, nullable=False)

	def __init__(self, days, hour, minute, duration):
		self.days = days
		self.hour = hour
		self.minute = minute
		self.duration = duration

	def __repr__(self):
		return f"<SleepSchedule days:{self.days} hour:{self.hour} minute:{self.minute} duration:{self.duration}>"
	

class WallpaperModel(db.Model):
	__tablename__: str = "wallpaper"
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(), nullable=False)
	hash = db.Column(db.String(), nullable=False)
	size = db.Column(db.Integer, nullable=False)
	mode = db.Column(db.Integer, nullable=False)
	color = db.Column(db.Integer, nullable=False)
	shadow = db.Column(db.Integer, nullable=False)
	
	def __init__(self, name, hash, size, mode, color, shadow):
		self.name = name
		self.hash = hash
		self.size = size
		self.mode = mode
		self.color = color
		self.shadow = shadow
	
	def __repr__(self):
		return f"<Wallpaper name:{self.name} hash:{self.hash} size:{self.size} mode:{self.mode} color:{self.color} shadow:{self.shadow}>"
