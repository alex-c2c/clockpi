import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


def create_app():
	app = Flask(__name__)
	app.config.from_object(os.getenv("APP_SETTING", "config.DevConfig"))

	db.init_app(app)
	migrate.init_app(app, db)

	return app
