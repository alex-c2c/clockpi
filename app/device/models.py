from datetime import datetime
from pytz import timezone

from sqlalchemy import ARRAY, Boolean, ForeignKey, Integer, String, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column

from app import db

from .consts import Orientation


class DeviceModel(db.Model):
	__tablename__: str = "device"

	id:	Mapped[int]						= mapped_column(Integer, primary_key=True)
	name: Mapped[str]					= mapped_column(String(), nullable=False)
	desc: Mapped[str]					= mapped_column(String())
	ipv4: Mapped[str]					= mapped_column(String(), nullable=False, unique=True)
	type: Mapped[str]					= mapped_column(String(), nullable=False)
	supported_colors: Mapped[list[str]] = mapped_column(MutableList.as_mutable(ARRAY(String)), default=list, nullable=False, server_default="{}")
	default_label_color: Mapped[str]	= mapped_column(String(), nullable=False)
	default_label_shadow: Mapped[str] 	= mapped_column(String(), nullable=False)
	orientation: Mapped[Orientation] 	= mapped_column(ENUM(Orientation), nullable=False, server_default=Orientation.HORIZONTAL.value)
	width: Mapped[int]					= mapped_column(Integer, nullable=False)
	height: Mapped[int]					= mapped_column(Integer, nullable=False)
	queue: Mapped[list[int]]			= mapped_column(MutableList.as_mutable(ARRAY(Integer)), default=list, nullable=False, server_default="{}")
	is_draw_grid: Mapped[bool]			= mapped_column(Boolean, nullable=False, default=False, server_default="f")
	is_show_time: Mapped[bool]			= mapped_column(Boolean, nullable=False, default=True, server_default="t")
	is_enabled: Mapped[bool]			= mapped_column(Boolean, nullable=False, default=True, server_default="t")
	created_at:	Mapped[datetime]		= mapped_column(DateTime, nullable=False, default=datetime.now(timezone("Asia/Singapore")))
	updated_at:	Mapped[datetime] 		= mapped_column(DateTime, nullable=True)

	def __init__(self,
	name: str,
	desc: str,
	ipv4: str,
	type: str,
	orientation: Orientation
	) -> None:
		self.name = name
		self.desc = desc
		self.ipv4 = ipv4
		self.type = type
		self.queue = []
		self.is_draw_grid = False
		self.is_enabled = True
		self.is_show_time = True
		
		self.update_orientation(orientation)
		self.update_colors()
		
	def __repr__(self) -> str:
		return f"<Device - \
			name:{self.name} \
			desc:{self.desc} \
			ipv4:{self.ipv4} \
			type:{self.type} \
			supported_colors:{self.supported_colors} \
			orientation:{self.orientation.value} \
			width:{self.width} \
			height:{self.height} \
			queue:{self.queue} \
			is_draw_grid:{self.is_draw_grid} \
			is_enabled:{self.is_enabled} \
			is_show_time:{self.is_show_time} \
			created_at:{self.created_at} \
			updated_at:{self.updated_at} \
			>"

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"name": self.name,
			"desc": self.desc,
			"ipv4": self.ipv4,
			"type": self.type,
			"supportedColors": self.supported_colors,
			"orientation": self.orientation.value,
			"width": self.width,
			"height": self.height,
			"queue": self.queue,
			"isDrawGrid": self.is_draw_grid,
			"isEnabled": self.is_enabled,
			"isShowTime": self.is_show_time,
		}
	
	def update_orientation(self, orientation: Orientation) -> None:
		self.orientation = orientation
		
		if self.type == "epd7in3e":
			from app.epd7in3e.consts import EPD_DIMENSIONS
			if self.orientation == Orientation.HORIZONTAL:
				self.width = EPD_DIMENSIONS[0]
				self.height = EPD_DIMENSIONS[1]
			else:
				self.width = EPD_DIMENSIONS[1]
				self.height = EPD_DIMENSIONS[0]
		else:
			# TODO: add other EPD types
			...
	
	def update_type(self, type: str) -> None:
		self.type = type
		self.update_orientation(self.orientation)
		self.update_colors()
	
	def update_colors(self) -> None:
		if self.type == "epd7in3e":
			from app.epd7in3e.consts import SupportedColors, DEFAULT_LABEL_COLOR, DEFAULT_LABEL_SHADOW
			self.supported_colors = [sc.value for sc in SupportedColors]
			self.default_label_color = DEFAULT_LABEL_COLOR
			self.default_label_shadow = DEFAULT_LABEL_SHADOW
		else:
			self.supported_colors = []
			


class DeviceOwnershipModel(db.Model):
	__tablename__: str = "device_ownership"
	
	id: Mapped[int]					= mapped_column(Integer, primary_key=True)
	device_id: Mapped[int]			= mapped_column(ForeignKey("device.id"), nullable=False)
	user_id: Mapped[int]			= mapped_column(ForeignKey("user.id"), nullable=False)
	created_at:	Mapped[datetime]	= mapped_column(DateTime, nullable=False, default=datetime.now(timezone("Asia/Singapore")))
	updated_at:	Mapped[datetime]	= mapped_column(DateTime, nullable=True)

	__table_args__ = (
		UniqueConstraint("device_id", "user_id", name="uq_device_ownership"),
	)

	def __repr__(self) -> str:
		return f"<DeviceOwnership - \
			id:{self.id} \
			device_id:{self.device_id} \
			owners:{self.user_id} \
			created_at:{self.created_at} \
			updated_at:{self.updated_at} \
		>"

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"deviceId": self.device_id,
			"userId": self.user_id,
		}
