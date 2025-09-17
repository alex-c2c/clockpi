from datetime import datetime
from pytz import timezone
from sqlalchemy import Float, ForeignKey, String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app import db
from app.consts import *
from app.epd7in3e.consts import *


class WallpaperModel(db.Model):
	__tablename__: str = "wallpaper"

	'''
	xy: pixel position of label
	wh: width/height of label in percentage with respect to width/height of canvas
	'''
	id: 			Mapped[int] 		= mapped_column(Integer, primary_key=True)
	name:			Mapped[str] 		= mapped_column(String(), nullable=False)
	hash: 			Mapped[str] 		= mapped_column(String(), nullable=False)
	file_name:		Mapped[str] 		= mapped_column(String(), nullable=False)
	size: 			Mapped[int] 		= mapped_column(Integer, nullable=False)
	label_x_per:	Mapped[float] 		= mapped_column(Float(precision=1), default=0.0, nullable=False)
	label_y_per: 	Mapped[float] 		= mapped_column(Float(precision=1), default=0.0, nullable=False)
	label_w_per: 	Mapped[float] 		= mapped_column(Float(precision=1), default=1.0, nullable=False)
	label_h_per:	Mapped[float] 		= mapped_column(Float(precision=1), default=0.5, nullable=False)
	color: 			Mapped[str] 		= mapped_column(String(), default="NONE", nullable=False)
	shadow: 		Mapped[str]			= mapped_column(String(), default="NONE", nullable=False)
	created_at:		Mapped[datetime] 	= mapped_column(DateTime, nullable=False, default=datetime.now(timezone("Asia/Singapore")))
	updated_at:		Mapped[datetime] 	= mapped_column(DateTime, nullable=True)

	def to_dict(self) -> dict:
		d: dict = {}
		d["id"] = self.id
		d["name"] = self.name
		d["hash"] = self.hash
		d["fileName"] = self.file_name
		d["size"] = self.size
		d["labelXPer"] = self.label_x_per
		d["labelYPer"] = self.label_y_per
		d["labelWPer"] = self.label_w_per
		d["labelHPer"] = self.label_h_per
		d["color"] = self.color
		d["shadow"] = self.shadow
		return d

	def __repr__(self):
		return f"<Wallpaper - \
			id:{self.id} \
			name:{self.name} \
			hash:{self.hash} \
			size:{self.size} \
			file_name:{self.file_name} \
			label_x_per:{self.label_x_per} \
			label_y_per:{self.label_y_per} \
			label_w_per:{self.label_w_per} \
			label_h_per:{self.label_h_per} \
			color:{self.color} \
			shadow:{self.shadow} \
			created_at:{self.created_at} \
			updated_at:{self.updated_at}\
			>"


class WallpaperOwnershipModel(db.Model):
	__tablename__: str = "wallpaper_ownership"
	
	id: 			Mapped[int] 		= mapped_column(Integer, primary_key=True)
	wallpaper_id:	Mapped[int]			= mapped_column(ForeignKey("wallpaper.id"), unique=True, nullable=False)
	user_id:		Mapped[int]			= mapped_column(ForeignKey("user.id"), nullable=False)
	device_id:		Mapped[int]			= mapped_column(ForeignKey("device.id"), nullable=False)
	created_at:		Mapped[datetime] 	= mapped_column(DateTime, nullable=False, default=datetime.now(timezone("Asia/Singapore")))
	updated_at:		Mapped[datetime] 	= mapped_column(DateTime, nullable=True)


	def __repr__(self) -> str:
		return f"<WallpaperOwnership - {self.id=} {self.user_id=} {self.device_id=} {self.wallpaper_id=} {self.created_at=} {self.updated_at=}>"
