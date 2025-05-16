from logging import Logger, getLogger
from flask import Blueprint, redirect, request, url_for

from app.auth.logic import login_required
from app.queue.logic import shuffle_queue, move_to_first, shift_next


bp: Blueprint = Blueprint("queue", __name__, url_prefix="/queue")
logger: Logger = getLogger(__name__)


@bp.route("/shuffle", methods=["GET"])
@login_required
def view_shuffle():
	if request.method == "GET":
		shuffle_queue()

	return redirect(location=url_for("main.view_test"))


@bp.route("/next", methods=["GET"])
@login_required
def view_next():
	if request.method == "GET":
		shift_next()

	return redirect(location=url_for("main.view_test"))


@bp.route("/select", methods=["POST"])
@login_required
def view_select():
	if request.method == "POST":
		logger.debug(f"{request.form.get('id')=}")
		if request.form.get("id") is not None:
			image_id: int = int(request.form.get("id"))
			move_to_first(image_id)

	return redirect(url_for(endpoint="main.view_test"))
