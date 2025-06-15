import os

class Config:
	MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024 # 16 MB
	SCHEDULER_API_ENABLED: bool = True
	SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


class DevConfig(Config):
	DEBUG: bool = True
	SECRET_KEY: str = "dev"
	SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "postgresql://localhost/clockpi")
	REDIS_URL: str = os.getenv("REDIS_URL", "redis://:@localhost/0")


class ProdConfig(Config):
	DEBUG: bool = False
	SECRET_KEY: str = os.getenv("SECRET_KEY")
	SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL")
	REDIS_URL: str = os.getenv("REDIS_URL")
