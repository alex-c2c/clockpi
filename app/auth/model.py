from app import db

class UserModel(db.Model):
	__tablename__: str = "user"

	id: int = db.Column(db.Integer, primary_key=True)
	username: str = db.Column(db.String(), unique=True, nullable=False)
	password: str = db.Column(db.String(), nullable=False)
	disp_name: str = db.Column(db.String(), nullable=False)

	def __init__(self, username: str, password: str, disp_name: str) -> None:
		self.username = username
		self.password = password
		self.disp_name = disp_name

	def __repr__(self) -> str:
		return f"<User - username:{self.username} | disp_name:{self.display_name}>"
