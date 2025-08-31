import os
import getpass
import logging
from logging import Logger, getLogger

from app import create_app, db
from app.queue.models import QueueModel
from app.user.consts import UserRole
from app.user.logic import create_user
from app.user.models import UserModel

logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)

app = create_app()


def _create_superuser(data: dict) -> None:
	try:
		user: UserModel | None = create_user(data)
		if user is None:
			logger.error("Unable to create superuser")
		else:
			logger.info(f"Created superuser {user.id}:{user.username}")
	except Exception as e:
		logger.error(f"Exception occured: {e}")
		

def _create_empty_queue() -> None:
	queue: QueueModel = QueueModel(queue="")
	db.session.add(queue)
	db.session.commit()
	logger.info("Created empty queue")


@app.cli.command("create-superuser")
def cli_create_superuser() -> None:
	username: str = str(input(f"Username: "))
	disp_name: str = str(input(f"Display Name: "))
	password: str = getpass.getpass(f"Password: ")
	confirm_password: str = getpass.getpass(f"Confirm password: ")
	
	data: dict = {
		"username": username,
		"dispName": disp_name,
		"password": password,
		"confirmPassword": confirm_password,
		"role": UserRole.ADMIN.value
	}

	_create_superuser(data)
	
	
@app.cli.command("create-queue")
def cli_create_queue() -> None:
	_create_empty_queue()


@app.cli.command("setup-default")
def cli_setup_default() -> None:
	data: dict = {
		"username": os.environ.get("DEFAULT_SUPERUSER_USERNAME"),
		"dispName": os.environ.get("DEFAULT_SUPERUSER_DISPNAME"),
		"password": os.environ.get("DEFAULT_SUPERUSER_PASSWORD"),
		"confirmPassword": os.environ.get("DEFAULT_SUPERUSER_PASSWORD"),
		"role": UserRole.ADMIN.value
	}
	
	_create_superuser(data)
	_create_empty_queue()
	
	