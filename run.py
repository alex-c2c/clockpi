from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app import create_app


app = create_app()


if __name__ == '__main__':
	app.run()
