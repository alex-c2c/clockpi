import getpass
import logging
from logging import Logger, getLogger

from app import create_app
from app.user.consts import UserRole
from app.user.logic import create_user
from app.user.models import UserModel

logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)

app = create_app()

@app.cli.command("create-superuser")
def cli_create_super_user() -> None:
	username: str = str(input(f"Username: "))
	disp_name: str = str(input(f"Display Name: "))
	password: str = getpass.getpass(f"Password: ")
	confirm_password: str = getpass.getpass(f"Confirm password: ")
	
	data: dict = {
		"username": username,
		"dispName": disp_name,
		"password": password,
		"confirmPassword": confirm_password
	}

	try:
		user: UserModel | None = create_user(data, UserRole.ADMIN)
		if user is None:
			logger.error("Unable to create superuser")
		else:
			logger.info(f"Created superuser {user.id}:{user.username}")
	except Exception as e:
		logger.error(f"Exception occured: {e}")
	
	
