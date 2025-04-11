from logging import Logger, getLogger
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug import Response
from clockpi.auth import login_required
from clockpi.db import get_db, get_images, update_image
from clockpi.queue import get_queue, move_to_first, shuffle_queue
from clockpi.consts import *
from clockpi.redis_controller import (
    rset,
    rget,
)
from clockpi.logic import epd_update, epd_clear, process_uploaded_file


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
        select: bool = request.form.get("select") is not None
        mode: int = int(request.form.get("mode", TimeMode.FULL_3))
        color: int = int(request.form.get("color", TextColor.NONE))
        shadow: int = int(request.form.get("shadow", TextColor.NONE))
        logger.info(f"update image {id=} {mode=} {color=} {shadow=} {select=}")

        update_image(id, mode, color, shadow)

        if select:
            move_to_first(id)

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
