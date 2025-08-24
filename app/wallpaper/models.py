from sqlalchemy import Float
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped

from app import db
from app.consts import *
from app.epd.consts import *

class WallpaperModel(db.Model):
	__tablename__: str = "wallpaper"

	id: 			Mapped[int] = db.Column(db.Integer, primary_key=True)
	name:			Mapped[str] = db.Column(db.String(), nullable=False)
	hash: 			Mapped[str] = db.Column(db.String(), nullable=False)
	size: 			Mapped[int] = db.Column(db.Integer, nullable=False)
	x:	 			Mapped[int] = db.Column(db.Integer, nullable=False, default=0)
	y: 				Mapped[int] = db.Column(db.Integer, nullable=False, default=0)
	w: 				Mapped[float] = db.Column(Float(precision=1), nullable=False, default=9)
	h:				Mapped[float] = db.Column(Float(precision=1), nullable=False, default=5)
	color: 			Mapped[Color] = db.Column(ENUM(Color), nullable=False, default=Color.WHITE)
	shadow: 		Mapped[Color] = db.Column(ENUM(Color), nullable=False, default=Color.BLACK)

	def __init__(
		self,
		name: str,
		hash: str,
		size: int,
		x: int = 0,
		y: int = 0,
		w: float = 9,
		h: float = 5,
		color: Color | None = None,
		shadow: Color | None = None,
	):
		self.name = name
		self.hash = hash
		self.size = size
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.color = Color.WHITE if color is None else color
		self.shadow = Color.BLACK if shadow is None else shadow
  
	def to_dict(self) -> dict:
		d: dict = {}
		d["id"] = self.id
		d["name"] = self.name
		d["hash"] = self.hash
		d["size"] = self.size
		d["x"] = self.x
		d["y"] = self.y
		d["w"] = self.w
		d["h"] = self.h
		d["color"] = self.color.value
		d["shadow"] = self.shadow.value
		return d

	def __repr__(self):
		return f"<Wallpaper - name:{self.name} hash:{self.hash} size:{self.size} x:{self.x} y:{self.y} w:{self.w} h:{self.h} color:{self.color} shadow:{self.shadow}>"
