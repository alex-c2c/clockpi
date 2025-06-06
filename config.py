import os
import tempfile

class Config:
	DEBUG: bool = False
	MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024 # 16 MB
	SCHEDULER_API_ENABLED: bool = True
	SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "postgresql://localhost/clockpi")
	SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
	CELERY = dict(
		broker_url="redis://localhost",
		result_backend="redis://localhost",
		task_ignore_result=True,
	)
 
 
class DevConfig(Config):
	DEBUG: bool = True
	SECRET_KEY: str = "dev"


class ProdConfig(Config):
    DEBUG: bool = False
    SECRET_KEY: str = os.getenv("SECRET_KEY")
