from app import db

class SleepModel(db.Model):
	__tablename__: str = "sleep"

	id: int = db.Column(db.Integer, primary_key=True)
	days: str = db.Column(db.String(), nullable=False)
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
		return f"<Sleep - days:{self.days} hour:{self.hour} minute:{self.minute} duration:{self.duration} enabled:{self.enabled}>"
