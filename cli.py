import os
import getpass
import logging
from logging import Logger, getLogger
import socket

from app import create_app
from app.device.consts import Orientation
from app.device.logic import create_device
from app.device.models import DeviceModel
from app.user.consts import UserRole
from app.user.logic import create_user
from app.user.models import UserModel

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s <%(levelname)s> %(name)s.%(funcName)s: %(message)s")
logger: Logger = getLogger(__name__)

app = create_app()


def _get_local_ip() -> str:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		# Doesn't have to be reachable — just used to determine the default interface
		s.connect(("8.8.8.8", 80))
		ip = s.getsockname()[0]
	finally:
		s.close()

	return str(ip)


def _create_superuser(data: dict) -> dict:
	user: dict = create_user(data)
	return user


def _create_default_device(user_id:int, data: dict) -> None:
	device: dict = create_device(user_id, data)
	logger.info(f"Created device {device}")
	

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
	

@app.cli.command("setup-default")
def cli_setup_default() -> None:
	user_payload: dict = {
		"username": os.environ.get("DEFAULT_SUPERUSER_USERNAME"),
		"dispName": os.environ.get("DEFAULT_SUPERUSER_DISPNAME"),
		"password": os.environ.get("DEFAULT_SUPERUSER_PASSWORD"),
		"confirmPassword": os.environ.get("DEFAULT_SUPERUSER_PASSWORD"),
		"role": UserRole.ADMIN.value
	}
	
	user: dict = _create_superuser(user_payload)
		
	device_payload: dict = {
		"name": os.environ.get("DEFAULT_DEVICE_NAME"),
		"desc": os.environ.get("DEFAULT_DEVICE_DESC"),
		"ipv4": _get_local_ip(),
		"type": os.environ.get("DEFAULT_DEVICE_TYPE"),
		"orientation": Orientation.HORIZONTAL.value
	}
	
	_create_default_device(user["id"], device_payload)
	