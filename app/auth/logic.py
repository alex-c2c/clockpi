from logging import Logger, getLogger

from werkzeug.security import check_password_hash

from app.lib.errors import api_abort, ErrorCode
from app.session_pkg.logic import init_session
from app.user.models import UserModel

logger: Logger = getLogger(__name__)

"""""
LOGIC
"""""


def login_user(data: dict) -> dict:
	username: str = data.get("username", "")
	password: str = data.get("password", "")
		
	user: UserModel | None = UserModel.query.filter_by(username=username).one_or_none()
	if user is None:
		#api_abort(401, "AUTHENTICATION_ERROR", "Invalid username or password")
		api_abort(ErrorCode.AUTHENTICATION_FAILED)
		
	if not check_password_hash(user.password, password):
		#api_abort(401, "AUTHENTICATION_ERROR", "Invalid username or password")
		api_abort(ErrorCode.AUTHENTICATION_FAILED)
	
	init_session(user)
	
	return user.to_dict()
