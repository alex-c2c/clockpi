from enum import Enum

class UserRole(Enum):
	ADMIN = "ADMIN",
	USER = "USER",
	VIEWER = "VIEWER"
	

# Validity regex for username
# Alphanumeric
# Allowed special characters: dash(-), underscore(_), period(.)
# Must start with alphabet
# Must end with alphabet or number
# Cannot contain 2 or more special characters in a row
# Cannot must start or end with special character
USERNAME_REGEX: str = r"^(?=.{6,32}$)[a-zA-Z](?!.*[._-]{2})[a-zA-Z0-9._-]*[a-zA-Z0-9]$"

# Validity regex for passwords
# At least 1 lowercase letter
# At least 1 uppercase letter
# At least 1 number
# At least 1 special character
# 8 to 64 characters
PASSWORD_REGEX: str = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"


# Validity regex for display name
# Allowed special characters: dash(-), apostrophes(')
# 2 to 64 characters
DISP_NAME_REGEX: str = r"^(?=.{2,64}$)[A-Za-z]+([ '-][A-Za-z]+)*$"

