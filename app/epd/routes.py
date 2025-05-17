from flask import Blueprint, redirect, url_for

from app.auth.logic import login_required
from . import logger
from .logic import clear_display, update_display


bp: Blueprint = Blueprint("epd", __name__, url_prefix="/epd")


@bp.route("/clear", methods=["GET"])
@login_required
def view_clear():
	clear_display()

	return redirect(location=url_for("main.view_test"))


@bp.route("/refresh", methods=["GET"])
@login_required
def view_refresh():
	update_display()

	return redirect(location=url_for("main.view_test"))
