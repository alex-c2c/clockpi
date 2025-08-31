from datetime import datetime
from pytz import timezone

from sqlalchemy import String, DateTime, Integer
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app import db

from .consts import UserRole

class UserModel(db.Model):
	__tablename__: str = "user"

	id: 		Mapped[int]			= mapped_column(Integer, primary_key=True)
	username: 	Mapped[str]	 		= mapped_column(String(), nullable=False, unique=True)
	password: 	Mapped[str]	 		= mapped_column(String(), nullable=False)
	disp_name: 	Mapped[str]	 		= mapped_column(String(), nullable=False)
	role: 		Mapped[UserRole] 	= mapped_column(ENUM(UserRole), nullable=False, default=UserRole.VIEWER)
	created_at:	Mapped[datetime]	= mapped_column(DateTime, nullable=False, default=datetime.now(timezone("Asia/Singapore")))
	updated_at:	Mapped[datetime] 	= mapped_column(DateTime, nullable=False, default=datetime.now(timezone("Asia/Singapore")))

	def __init__(self, username: str, password: str, disp_name: str, role: UserRole = UserRole.VIEWER) -> None:
		self.username = username
		self.password = password
		self.disp_name = disp_name
		self.role = role

	def __repr__(self) -> str:
		return f"<User - username:{self.username} | disp_name:{self.disp_name} | role:{self.role} | created_at:{self.created_at} | updated_at:{self.updated_at}>"

	def to_dict(self) -> dict:
		d: dict = {}
		d["id"] = self.id
		d["username"] = self.username
		d["dispName"] = self.disp_name
		d["role"] = self.role.value
		
		return d
