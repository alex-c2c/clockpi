from app import db
from logging import Logger, getLogger
from flask import (
	Blueprint,
	render_template,
	request,
)

#from app.auth import login_required
from app.consts import *

#from werkzeug.utils import secure_filename
#from werkzeug.datastructures import FileStorage

from app.models import AccountModel


bp = Blueprint("clockpi", __name__)
logger: Logger = getLogger(__name__)


def allowed_file(filename) -> bool:
	return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/", methods=["GET"])
#@login_required
def index():

	return {"message": "index"}


@bp.route("/add_acct", methods=["POST"])
def add_acct():
	if request.method == "POST":
		data = request.get_json()
		new_acct: AccountModel = AccountModel(data["username"], data["password"])
  
		db.session.add(new_acct)
		db.session.commit()
		return {"message": f"Created new account {data["username"]}"}
	
	return {"message": "empty"}
	