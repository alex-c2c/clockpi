import os
from flask import Blueprint, Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
session = Session()

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(
	api_bp, version="1.0", title="Clockpi API", description="Clockpi controls", doc="/docs"
)

def create_app():
	app = Flask(__name__)
	app.config.from_object(os.getenv("APP_SETTING"))

	db.init_app(app)
	migrate.init_app(app, db)
	session.init_app(app)

	return app
