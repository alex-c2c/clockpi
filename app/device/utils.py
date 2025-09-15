import re
import sys

from logging import Logger, getLogger
from re import Pattern

from sqlalchemy import select

from app import db

from .consts import DEVICE_TYPES, Orientation
from .models import DeviceModel

logger: Logger = getLogger(__name__)


REGEX_IP: str = r"^(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$"


def is_name_valid(name: str | None) -> str | None:
	if name is None:
		return "This is a required property."
		
	return None


def is_desc_valid(desc: str | None) -> str | None:
	return None


def is_ipv4_valid(ipv4: str | None) -> str | None:
	if ipv4 is None:
		return "This is a required property."
		
	pattern: Pattern[str] = re.compile(REGEX_IP)
	if not bool(pattern.match(ipv4)):
		return "Invalid input."
		
	if db.session.scalars(select(DeviceModel).where(DeviceModel.ipv4 == ipv4)).one_or_none() is not None:
		return "Duplicate ipv4 address found."
		
	return None
	
	
def is_type_valid(type: str | None) -> str | None:
	if type is None:
		return "This is a required property."
	
	if type not in DEVICE_TYPES:
		return "Unsupported device type."
		
	return None


def is_orientation_valid(orientation_str: str | None) -> str | None:
	if orientation_str is None:
		return "This is a required property."
		
	if sys.version_info < (3, 13):
		orientations: list[str] = [str(o.value) for o in Orientation]
		if orientation_str not in orientations:
			return "Unsupported orientation."
	else:
		if orientation_str not in Orientation:
			return "Unsupported orientation."
			
	return None
