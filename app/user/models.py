from sqlalchemy.dialects.postgresql import ENUM

from app import db

from .consts import UserRole

class UserModel(db.Model):
	__tablename__: str = "user"

	id: int = db.Column(db.Integer, primary_key=True)
	username: str = db.Column(db.String(), unique=True, nullable=False)
	password: str = db.Column(db.String(), nullable=False)
	disp_name: str = db.Column(db.String(), nullable=False)
	role: UserRole = db.Column(ENUM(UserRole), nullable=False, default=UserRole.VIEWER)

	def __init__(self, username: str, password: str, disp_name: str, role: UserRole) -> None:
		self.username = username
		self.password = password
		self.disp_name = disp_name
		self.role = role

	def __repr__(self) -> str:
		return f"<User - username:{self.username} | disp_name:{self.disp_name} | role:{self.role}>"

	def to_dict(self) -> dict:
		d: dict = {}
		d["id"] = self.id
		d["username"] = self.username
		d["dispName"] = self.disp_name
		d["role"] = self.role.value
		
		return d
