import os
import tempfile
from clockpi import app

class BaseConfig:
    DEBUG = False
    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
    SCHEDULER_API_ENABLED = True
    DATABASE=os.path.join(app.instance_path, "clockpi.sqlite")
    CELERY=dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        task_ignore_result=True,
    )
    DIR_APP_UPLOAD=os.path.join(os.path.dirname(app.instance_path), "upload")
    DIR_TMP_UPLOAD=os.path.join(tempfile.gettempdir(), "upload")
    DIR_TMP_PROCESSED=os.path.join(tempfile.gettempdir(), "processed")
    
class DevConfig(BaseConfig):
    DEBUG = True
    SECRET_KEY = "dev"

    