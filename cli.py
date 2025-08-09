import getpass
import logging

from logging import Logger, getLogger

from app import create_app, db
from app.auth.models import UserModel
from app.auth.logic import is_password_valid, is_username_valid

from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)

app = create_app()

@app.cli.command("create-superuser")
def cli_create_super_user() -> None:
	username: str = str(input(f"Username: "))
	if not is_username_valid(username):
		logger.error("Unable to create superuser")
		return

	disp_name: str = str(input(f"Display Name: "))

	password: str = getpass.getpass(f"Password: ")
	if not is_password_valid(password):
		logger.error("Unable to create superuser")
		return

	user: UserModel = UserModel(username,generate_password_hash(password),disp_name)
	db.session.add(user)
	db.session.commit()

	logger.info(f"Created superuser {user.id}:{user.username}")
