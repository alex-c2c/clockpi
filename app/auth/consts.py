USERNAME_MIN_LEN: int = 4
USERNAME_MAX_LEN: int = 32
USERNAME_REGEX: str = r"^[A-Za-z][A-Za-z0-9_]*$"
PASSWORD_REGEX: str = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
PASSWORD_MIN_LEN: int = 16
