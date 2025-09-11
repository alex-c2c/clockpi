import re
import sys
import logging

from logging import Logger, getLogger
from re import Pattern

from .consts import DEVICE_TYPES, Orientation

logger: Logger = getLogger(__name__)


REGEX_IP: str = r"^(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$"


def is_name_valid(name: str | None) -> str | None:
	if name is None:
		return "This is a required field"
		
	return None


def is_desc_valid(desc: str | None) -> str | None:
	return None


def is_ipv4_valid(ipv4: str | None) -> str | None:
	if ipv4 is None:
		return "This is a required field"
		
	pattern: Pattern[str] = re.compile(REGEX_IP)
	if not bool(pattern.match(ipv4)):
		return ""
		
	return None
	
	
def is_type_valid(type: str | None) -> str | None:
	if type is None:
		return "This is a required field"
	
	if type not in DEVICE_TYPES:
		return "Invalid input"
		
	return None


def is_orientation_valid(orientation_str: str | None) -> str | None:
	if orientation_str is None:
		return "This is a required field"
		
	if sys.version_info < (3, 13):
		orientations: list[str] = [str(o.value) for o in Orientation]
		if orientation_str is None or orientation_str not in orientations:
			return "Invalid input"
	else:
		if orientation_str is None or orientation_str not in Orientation:
			return "Invalid input"
			
	return None
