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
		"confirmPassword": confirm_password,
		"role": UserRole.ADMIN.value
	}

	try:
		user: UserModel | None = create_user(data)
		if user is None:
			logger.error("Unable to create superuser")
		else:
			logger.info(f"Created superuser {user.id}:{user.username}")
	except Exception as e:
		logger.error(f"Exception occured: {e}")
	
	
@app.cli.command("create-queue")
def cli_create_queue() -> None:
	queue: QueueModel = QueueModel(queue="")
	db.session.add(queue)
	db.session.commit()
	logger.info("Created empty queue")
