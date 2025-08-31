from datetime import datetime
from pytz import timezone
from sqlalchemy import Float, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app import db
from app.consts import *
from app.epd.consts import *

class WallpaperModel(db.Model):
	__tablename__: str = "wallpaper"

	'''
	xy: pixel position of label
	wh: width/height of label in percentage with respect to width/height of canvas
	'''
	id: 		Mapped[int] 		= mapped_column(Integer, primary_key=True)
	name:		Mapped[str] 		= mapped_column(String(), nullable=False)
	hash: 		Mapped[str] 		= mapped_column(String(), nullable=False)
	file_name:	Mapped[str] 		= mapped_column(String(), nullable=False)
	size: 		Mapped[int] 		= mapped_column(Integer, nullable=False)
	x:	 		Mapped[int] 		= mapped_column(Integer, nullable=False, default=0)
	y: 			Mapped[int] 		= mapped_column(Integer, nullable=False, default=0)
	w: 			Mapped[float] 		= mapped_column(Float(precision=1), nullable=False, default=30.0)
	h:			Mapped[float] 		= mapped_column(Float(precision=1), nullable=False, default=12.9)
	color: 		Mapped[Color] 		= mapped_column(ENUM(Color), nullable=False, default=Color.WHITE)
	shadow: 	Mapped[Color]		= mapped_column(ENUM(Color), nullable=False, default=Color.BLACK)
	created_at:	Mapped[datetime] 	= mapped_column(DateTime, nullable=False, default=datetime.now(timezone("Asia/Singapore")))
	updated_at:	Mapped[datetime] 	= mapped_column(DateTime, nullable=False, default=datetime.now(timezone("Asia/Singapore")))

	def __init__(
		self,
		name: str,
		hash: str,
		file_name: str,
		size: int,
		x: int = 0,
		y: int = 0,
		w: float = 30.0,
		h: float = 12.9,
		color: Color = Color.WHITE,
		shadow: Color = Color.BLACK,
	):
		self.name = name
		self.hash = hash
		self.file_name = file_name
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
		d["fileName"] = self.file_name
		d["size"] = self.size
		d["x"] = self.x
		d["y"] = self.y
		d["w"] = self.w
		d["h"] = self.h
		d["color"] = self.color.value
		d["shadow"] = self.shadow.value
		d["createdAt"] = self.created_at
		d["updatedAt"] = self.updated_at
		return d

	def __repr__(self):
		return f"<Wallpaper - \
			name:{self.name} \
			hash:{self.hash} \
			size:{self.size} \
			file_name:{self.file_name} \
			x:{self.x} \
			y:{self.y} \
			w:{self.w} \
			h:{self.h} \
			color:{self.color} \
			shadow:{self.shadow} \
			created_at:{self.created_at} \
			updated_at:{self.updated_at}\
			>"
