import queue
import os

import clockpi.db as db
import clockpi.logic as logic
import clockpi.queue as queue
from datetime import datetime
from logging import Logger, getLogger
from threading import Thread
from flask import (
    Blueprint,
    app,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug import Response
from clockpi.auth import login_required
from clockpi.db import delete_image, get_db, get_image, get_images, update_image
from clockpi.queue import get_queue, move_to_first, shuffle_queue
from clockpi.consts import *
from clockpi.redis_controller import rset,rget
from clockpi.logic import epd_update, epd_clear, process_uploaded_file

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


bp = Blueprint("clockpi", __name__)
logger: Logger = getLogger(__name__)


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


@bp.route("/upload_file", methods=["POST"])
def upload_file():
    if request.method == "POST" and "file" in request.files:
        if "file" not in request.files:
            flash("No file part")
            return redirect(url_for("clockpi.test"))
        
        files: list[FileStorage] = request.files.getlist('file')
        
        for file in files:
            # secure file name
            file_name = secure_filename(file.filename)
            
            if file_name == "":
                flash("No file part")
                continue
            
            if "." not in file_name or file_name.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS:
                flash(f"Uploaded image {file_name=} with invalid extension")
                continue
            
            # save file to temp dir
            # TODO: improve location of "uploaded" files so that it doesn't get
            # overwritten by someone else uploading the files with same file name at the same time
            if not os.path.isdir(current_app.config["DIR_TMP_UPLOAD"]):
                os.mkdir(current_app.config["DIR_TMP_UPLOAD"])

            temp_path: str = os.path.join(current_app.config["DIR_TMP_UPLOAD"], file_name)
            file.save(temp_path)
            
            t: Thread = Thread(target=process_uploaded_file, args=(current_app.app_context(), file_name,))
            t.start()

    return redirect(url_for("clockpi.test"))


@bp.route("/test", methods=["GET"])
def test():
    # Get settings from Redis
    draw_grids: bool = True if rget(SETTINGS_DRAW_GRIDS, "1") == "1" else False
    epd_busy: bool = False if rget(SETTINGS_EPD_BUSY, "0") == "0" else True

    # Get all images
    images = get_images()

    # Get Image Queue
    image_queue: tuple[int] = get_queue()

    # Text Color
    text_color: dict[str, int] = TEXT_COLOR_DICT

    # Time Modes
    mode: dict[str, int] = TIME_MODE_DICT
    
    # Sleep Schedules
    now_hr: int = datetime.now().hour
    now_min: int = datetime.now().minute
    

    return render_template(
        "clockpi/test.html",
        draw_grids=draw_grids,
        epd_busy=epd_busy,
        images=images,
        image_queue=image_queue,
        text_color=text_color,
        mode=mode,
    )


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

        logger.info(f"set draw grids {draw_grids=}")

        # Update Redis
        rset(SETTINGS_DRAW_GRIDS, "1" if draw_grids else "0")

    return redirect(url_for(endpoint="clockpi.test"))


@bp.route("/update/<int:id>", methods=["POST"])
def update(id: int):
    if request.method == "POST":
        is_select: bool = request.form.get("select") is not None
        is_delete: bool = request.form.get("delete") is not None
        mode: int = int(request.form.get("mode", TimeMode.FULL_3))
        color: int = int(request.form.get("color", TextColor.NONE))
        shadow: int = int(request.form.get("shadow", TextColor.NONE))
        logger.info(f"update image {id=} {mode=} {color=} {shadow=} {is_select=} {is_delete=}")
        
        if is_delete:
            logic.delete_image(id)
            
        else:
            update_image(id, mode, color, shadow)

            if is_select:
                move_to_first(id)

    return redirect(url_for(endpoint="clockpi.test"))


@bp.route("/select", methods=["POST"])
def select():
    if request.method == "POST":
        if request.form.get("id") is not None:
            image_id: int = int(request.form.get("id"))
            move_to_first(image_id)

    return redirect(url_for(endpoint="clockpi.test"))


@bp.route("/delete", methods=["POST"])
def delete():
    if request.method == "POST":
        if request.form.get("id") is not None:
            image_id: int = int(request.form.get("id"))
            logic.delete_image(id)


            image = get_image(id)
            if image is not None:
                db.delete_image(image_id)
                logic.delete_image(image_id)
                queue.remove_id(image_id)

    return redirect(url_for(endpoint="clockpi.test"))


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
