from logging import Logger, getLogger

from werkzeug.security import check_password_hash

from app.session_pkg.logic import init_session
from app.user.models import UserModel

from . import ns

logger: Logger = getLogger(__name__)


"""""
LOGIC
"""""


def login_user(data: dict) -> UserModel | None:
	username: str = data.get("username", "")
	password: str = data.get("password", "")
	
	user: UserModel | None = UserModel.query.filter_by(username=username).one_or_none()
	if user is None:
		ns.abort(400, "Invalid username or password")
		return
		
	if not check_password_hash(user.password, password):
		ns.abort(400, "Invalid username or password")
		return
	
	init_session(user)
	
	return user
