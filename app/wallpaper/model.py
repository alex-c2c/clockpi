from app import db
from app.consts import *
from app.epd.consts import *

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
		return f"<Wallpaper - name:{self.name} hash:{self.hash} size:{self.size} mode:{self.mode} color:{self.color} shadow:{self.shadow}>"
