import os
import queue
import shutil
import hashlib
import logging
from datetime import datetime
from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    send_from_directory,
)
from werkzeug import Response
from clockpi.auth import login_required
from clockpi.db import get_db, add_image, get_image, get_images
from clockpi.queue import get_queue, shuffle_queue
from clockpi.consts import *
from clockpi.redis_controller import (
    get_settings,
    rset,
    rget,
    reset_settings,
)
from clockpi.logic import epd_update, epd_clear, process_uploaded_file


bp = Blueprint("clockpi", __name__)
LOGGER = logging.getLogger(name="clockpi")


def allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/")
def index():
    db = get_db()
    """
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('clockpi/index.html', posts=posts)
    """
    return render_template(("clockpi/index.html"))


@bp.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        result: int = process_uploaded_file(file)
                
        if result == ERR_UPLOAD_NO_FILE:
            flash("No selected file")
        elif result == ERR_UPLOAD_INVALID_EXT:
            flash("Uploaded image file with invalid extension")
        elif result == ERR_UPLOAD_INVALID_IMAGE:
            flash("Uploaded invalid image file")
        elif result == ERR_UPLOAD_POST_PROC:
            flash("Unable to post process uploaded image")
        elif result == ERR_UPLOAD_HASH:
            flash("Unable to get hash of processed file")
        elif result == ERR_UPLOAD_COPY:
            flash("Unable to copy file")
        elif result == ERR_UPLOAD_SAVE:
            flash("Unable to save entry of upload")

    return redirect(url_for("clockpi.test"))


@bp.route("/test", methods=["GET"])
def test():
    # Get settings from Redis
    image_id, mode, color, shadow, draw_grids = get_settings()
    epd_busy: bool = False if rget(SETTINGS_EPD_BUSY, "0") == "0" else True

    # Get all images
    images = get_images()
    
    # Get Image Queue
    image_queue: tuple[int] = get_queue()

    return render_template(
        "clockpi/test.html",
        draw_grids=draw_grids,
        current_color=color,
        current_shadow=shadow,
        current_mode=mode,
        current_image_id=image_id,
        images=images,
        epd_busy=epd_busy,
        image_queue=image_queue
    )


@bp.route("/reset", methods=["GET"])
def reset():
    reset_settings()

    return redirect(location=url_for("clockpi.test"))


@bp.route("/shuffle", methods=["GET"])
def shuffle():
    shuffle_queue()

    return redirect(location=url_for("clockpi.test"))


@bp.route("/clear", methods=["GET"])
def clear():
    epd_clear()

    return redirect(location=url_for("clockpi.test"))


@bp.route("/refresh", methods=["GET"])
def refresh():
    epd_update()

    return redirect(location=url_for("clockpi.test"))


@bp.route("/draw_grids", methods=["POST"])
def set_draw_grids():
    if request.method == "POST":
        draw_grids: bool = request.form.get("draw_grids", "") == "true"

        # Update Redis
        rset(SETTINGS_DRAW_GRIDS, "1" if draw_grids else "0")

    return redirect(url_for(endpoint="clockpi.test"))


@bp.route("/update_image/<int:id>", methods=["POST"])
def update_image(id: int):
    if request.method == "POST":
        mode: str = request.form.get("mode", "")
        color: str = request.form.get("color", "")
        shadow: str = request.form.get("shadow", "")
        
        LOGGER.debug(f"{id=} {mode=} {color=} {shadow=}")
        
    return redirect(url_for(endpoint="clockpi.test"))


@bp.route("/set_mode", methods=["POST"])
def set_mode():
    if request.method == "POST":
        mode: TimeMode = TimeMode.OFF

        # Get Mode
        if request.form.get("btn_nine_section", "") == "Top Left":
            mode = TimeMode.SECT_9_TOP_LEFT
        elif request.form.get("btn_nine_section", "") == "Top Center":
            mode = TimeMode.SECT_9_TOP_CENTER
        elif request.form.get("btn_nine_section", "") == "Top Right":
            mode = TimeMode.SECT_9_TOP_RIGHT
        elif request.form.get("btn_nine_section", "") == "Middle Left":
            mode = TimeMode.SECT_9_MIDDLE_LEFT
        elif request.form.get("btn_nine_section", "") == "Middle Center":
            mode = TimeMode.SECT_9_MIDDLE_CENTER
        elif request.form.get("btn_nine_section", "") == "Middle Right":
            mode = TimeMode.SECT_9_MIDDLE_RIGHT
        elif request.form.get("btn_nine_section", "") == "Bottom Left":
            mode = TimeMode.SECT_9_BOTTOM_LEFT
        elif request.form.get("btn_nine_section", "") == "Bottom Center":
            mode = TimeMode.SECT_9_BOTTOM_CENTER
        elif request.form.get("btn_nine_section", "") == "Bottom Left":
            mode = TimeMode.SECT_9_BOTTOM_RIGHT
        elif request.form.get("btn_six_section", "") == "Top Left":
            mode = TimeMode.SECT_6_TOP_LEFT
        elif request.form.get("btn_six_section", "") == "Top Right":
            mode = TimeMode.SECT_6_TOP_RIGHT
        elif request.form.get("btn_six_section", "") == "Middle Left":
            mode = TimeMode.SECT_6_MIDDLE_LEFT
        elif request.form.get("btn_six_section", "") == "Middle Right":
            mode = TimeMode.SECT_6_MIDDLE_RIGHT
        elif request.form.get("btn_six_section", "") == "Bottom Left":
            mode = TimeMode.SECT_6_BOTTOM_LEFT
        elif request.form.get("btn_six_section", "") == "Bottom Right":
            mode = TimeMode.SECT_6_BOTTOM_RIGHT
        elif request.form.get("btn_four_section", "") == "Top Left":
            mode = TimeMode.SECT_4_TOP_LEFT
        elif request.form.get("btn_four_section", "") == "Top Right":
            mode = TimeMode.SECT_4_TOP_RIGHT
        elif request.form.get("btn_four_section", "") == "Bottom Left":
            mode = TimeMode.SECT_4_BOTTOM_LEFT
        elif request.form.get("btn_four_section", "") == "Bottom Right":
            mode = TimeMode.SECT_4_BOTTOM_RIGHT
        elif request.form.get("btn_full", "") == "Full Screen 1":
            mode = TimeMode.FULL_1
        elif request.form.get("btn_full", "") == "Full Screen 2":
            mode = TimeMode.FULL_2
        elif request.form.get("btn_full", "") == "Full Screen 3":
            mode = TimeMode.FULL_3

        # Update Redis
        rset(SETTINGS_MODE, str(mode.value))

    return redirect(url_for("clockpi.test"))


@bp.route("/set_color", methods=["POST"])
def set_color():
    if request.method == "POST":
        color: int = COLOR_WHITE

        if request.form.get("color", "") == "black":
            color = COLOR_BLACK
        elif request.form.get("color", "") == "white":
            color = COLOR_WHITE
        elif request.form.get("color", "") == "yellow":
            color = COLOR_YELLOW
        elif request.form.get("color", "") == "red":
            color = COLOR_RED
        elif request.form.get("color", "") == "blue":
            color = COLOR_BLUE
        elif request.form.get("color", "") == "green":
            color = COLOR_GREEN

        # Update Redis
        rset(SETTINGS_COLOR, str(color))

    return redirect(url_for("clockpi.test"))


@bp.route("/set_shadow", methods=["POST"])
def set_shadow():
    if request.method == "POST":
        shadow: int = COLOR_NONE

        if request.form.get("shadow", "") == "black":
            shadow = COLOR_BLACK
        elif request.form.get("shadow", "") == "white":
            shadow = COLOR_WHITE
        elif request.form.get("shadow", "") == "yellow":
            shadow = COLOR_YELLOW
        elif request.form.get("shadow", "") == "red":
            shadow = COLOR_RED
        elif request.form.get("shadow", "") == "blue":
            shadow = COLOR_BLUE
        elif request.form.get("shadow", "") == "green":
            shadow = COLOR_GREEN

        # Update Redis
        rset(SETTINGS_SHADOW, str(shadow))

    return redirect(url_for("clockpi.test"))


@bp.route("/select/<int:id>", methods=["GET"])
def select(id: int):
    if request.method == "GET":
        if id == 0:
            # Update Redis
            rset(SETTINGS_IMAGE_ID, "0")

        else:
            # Get image with ID
            image = get_image(id)
            if upload is None:
                flash(f"Selected invalid {id=}")
                return redirect(location=url_for("clockpi.test"))

            # Update Redis
            rset(SETTINGS_IMAGE_ID, str(id))

    return redirect(url_for("clockpi.test"))


"""
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('clockpi.index'))

    return render_template('clockpi/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('clockpi.index'))

    return render_template('clockpi/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('clockpi.index'))
"""
