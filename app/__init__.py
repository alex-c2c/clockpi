import os
import logging

from dotenv import load_dotenv
from logging import Logger, getLogger

from flask import Blueprint, Flask
from flask_restx import Api
#from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s <%(levelname)s> %(name)s.%(funcName)s: %(message)s")
logger: Logger = getLogger(__name__)

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
session = Session()
#apscheduler = APScheduler()

api_bp = Blueprint(
	name="api",
	import_name=__name__,
	url_prefix="/api"
)

api = Api(
	app=api_bp,
	version="1.0",
	title="Clockpi API",
	description="Clockpi controls",
	doc="/docs"
)

def create_app(is_skip_scheduler: bool = False) -> Flask:
	app = Flask(__name__)
	app.config.from_object(os.getenv("APP_SETTING"))
	app.config["SESSION_SQLALCHEMY"] = db

	db.init_app(app)
	migrate.init_app(app, db)
	session.init_app(app)
	
	'''
	if not is_skip_scheduler:
		apscheduler.init_app(app)
		
		# importing them to trigger addition to scheduler jobs
		from app.background.logic import tick_all, next_all_queue, shuffle_all_queue
		
		apscheduler.start()
	'''
	
	return app
