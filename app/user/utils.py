import re, sys

from .consts import UserRole, REGEX_USERNAME, REGEX_PASSWORD, REGEX_DISP_NAME


def is_username_valid(username: str | None) -> str | None:
	if username is None:
		return "This is a required property"
	
	regex = re.compile(REGEX_USERNAME)
	if not bool(regex.match(username)):
		return "Does not meet the minimum requirements"
		
	return None


def is_password_valid(password: str | None) -> str | None:
	if password is None:
		return "This is a required property"
	
	regex = re.compile((REGEX_PASSWORD))
	if not bool(regex.match(password)):
		return "Does not meet the minimum requirements"
	
	return None


def is_disp_name_valid(disp_name: str | None) -> str | None:
	if disp_name is None:
		return "This is a required property"
		
	regex = re.compile(REGEX_DISP_NAME)
	if not bool(regex.match(disp_name)):
		return "Does not meet the minimum requirements"
		
	return None


def is_role_valid(role: str | None) -> str | None:
	if role is None:
		return "This is a required property"
		
	if sys.version_info < (3, 13):
		roles: list[str] = [str(ur.value) for ur in UserRole]
		if role_str not in roles:
			return "Invalid input"
	else:
		if role not in UserRole:
			return "Invalid input"
	
	return None
