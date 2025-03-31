import os
import tempfile
import shutil
import hashlib
import logging
from . import consts as c
from datetime import datetime
from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for, send_from_directory
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from clockpi.auth import login_required
from clockpi.db import get_db
from clockpi.image import procsess_image, validate_image
from clockpi.epd import draw_image, draw_image_with_time, TimePos

bp = Blueprint('clockpi', __name__)
logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in c.ALLOWED_EXTENSIONS


@bp.route('/')
def index():
    db = get_db()
    '''
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('clockpi/index.html', posts=posts)
    '''
    return render_template(('clockpi/index.html'))


@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
         # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # secure file name
            filename = secure_filename(file.filename)
            
            # save file to temp dir
            # TODO: improve location of "uploaded" files so that it doesn't get
            # overwritten by someone else uploading the files with same file name at the same time
            temp_dir:str = os.path.join(tempfile.gettempdir(), c.DIR_UPLOAD)
            if not os.path.isdir(temp_dir):
                os.mkdir(temp_dir)
            temp_path:str = os.path.join(temp_dir, filename)
            file.save(temp_path)
            
            # validate image
            if not validate_image(temp_path):
                flash("Uploaded invalid image file")
                os.remove(temp_path)
                return redirect(request.url)
            
            # process image
            proc_dir:str = os.path.join(temp_dir, c.DIR_PROCESSED)
            if not os.path.isdir(proc_dir):
                os.mkdir(proc_dir)
            processed_path:str = os.path.join(proc_dir, filename)
            process_result:bool = procsess_image(temp_path, processed_path)
            if not process_result:
                flash("Unable to post process uploaded image")
                if os.path.isfile(temp_path):
                    os.remove(temp_path)
                if os.path.isfile(processed_path):
                    os.remove(processed_path)
                return redirect(request.url)
            
            # get hash of processed image
            try:
                h = hashlib.sha256()
                with open(processed_path, 'rb') as f:
                    while True:
                        chunk = f.read(h.block_size)
                        if not chunk:
                            break
                        h.update(chunk)
                hashname:str = h.hexdigest()
            except OSError as error:
                flash("Unable to get hash of processed file")
                if os.path.isfile(temp_path):
                    os.remove(temp_path)
                if os.path.isfile(processed_path):
                    os.remove(processed_path)
                return redirect(request.url)
            
            # copy processed image to upload dir
            try:
                dest_path:str = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{hashname}.bmp")
                shutil.copy2(processed_path, dest_path)
                os.remove(processed_path)
            except OSError as error:
                flash("Unable to copy file")
                if os.path.isfile(temp_path):
                    os.remove(temp_path)
                if os.path.isfile(processed_path):
                    os.remove(processed_path)
                return redirect(request.url)
            
            # draw the image on display
            #draw_image(dest_path)
            time:str = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}"
            draw_image_with_time(dest_path, time, TimePos.TOP_LEFT)
            
            #return redirect(url_for('clockpi.index'))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
    
@bp.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        logging.debug(f"{request.form=}")                
        file_path:str = os.path.join(current_app.config["UPLOAD_FOLDER"], "01fe482628b58eb16f05fbb698063d652261a8ca79e3366d472f003c6168bbb3.bmp")
        time:str = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}"
        time_pos:TimePos = TimePos.OFF
        
        # Get Refresh flag
        refresh:bool = request.form.get("refresh", "") == "true"
        
        # Get Color
        color:int = c.COLOR_BLACK
        if request.form.get("color", "") == "black":
            color = c.COLOR_BLACK
        elif request.form.get("color", "") == "white":
            color = c.COLOR_WHITE
        elif request.form.get("color", "") == "yellow":
            color = c.COLOR_YELLOW
        elif request.form.get("color", "") == "red":
            color = c.COLOR_RED
        elif request.form.get("color", "") == "blue":
            color = c.COLOR_BLUE
        elif request.form.get("color", "") == "green":
            color = c.COLOR_GREEN
        
        # Get Position
        if request.form.get("btn_nine_section", "") == "Top Left":
            time_pos = TimePos.SECT_9_TOP_LEFT
        elif request.form.get("btn_nine_section", "") == "Top Center":
            time_pos = TimePos.SECT_9_TOP_CENTER
        elif request.form.get("btn_nine_section", "") == "Top Right":
            time_pos = TimePos.SECT_9_TOP_RIGHT
        elif request.form.get("btn_nine_section", "") == "Middle Left":
            time_pos = TimePos.SECT_9_MIDDLE_LEFT
        elif request.form.get("btn_nine_section", "") == "Middle Center":
            time_pos = TimePos.SECT_9_MIDDLE_CENTER
        elif request.form.get("btn_nine_section", "") == "Middle Right":
            time_pos = TimePos.SECT_9_MIDDLE_RIGHT
        elif request.form.get("btn_nine_section", "") == "Bottom Left":
            time_pos = TimePos.SECT_9_BOTTOM_LEFT
        elif request.form.get("btn_nine_section", "") == "Bottom Center":
            time_pos = TimePos.SECT_9_BOTTOM_CENTER
        elif request.form.get("btn_nine_section", "") == "Bottom Left":
            time_pos = TimePos.SECT_9_BOTTOM_RIGHT
        elif request.form.get("btn_six_section", "") == "Top Left":
            time_pos = TimePos.SECT_6_TOP_LEFT
        elif request.form.get("btn_six_section", "") == "Top Right":
            time_pos = TimePos.SECT_6_TOP_Right
        elif request.form.get("btn_six_section", "") == "Middle Left":
            time_pos = TimePos.SECT_6_MIDDLE_LEFT
        elif request.form.get("btn_six_section", "") == "Middle Right":
            time_pos = TimePos.SECT_6_MIDDLE_RIGHT
        elif request.form.get("btn_six_section", "") == "Bottom Left":
            time_pos = TimePos.SECT_6_BOTTOM_LEFT
        elif request.form.get("btn_six_section", "") == "Bottom Right":
            time_pos = TimePos.SECT_6_BOTTOM_RIGHT
        elif request.form.get("btn_four_section", "") == "Top Left":
            time_pos = TimePos.SECT_4_TOP_LEFT
        elif request.form.get("btn_four_section", "") == "Top Right":
            time_pos = TimePos.SECT_4_TOP_RIGHT
        elif request.form.get("btn_four_section", "") == "Bottom Left":
            time_pos = TimePos.SECT_4_BOTTOM_LEFT
        elif request.form.get("btn_four_section", "") == "Bottom Right":
            time_pos = TimePos.SECT_4_BOTTOM_RIGHT
        elif request.form.get("btn_full", "") == "Full Screen 1":
            time_pos = TimePos.FULL_1
        elif request.form.get("btn_full", "") == "Full Screen 2":
            time_pos = TimePos.FULL_2
        elif request.form.get("btn_full", "") == "Full Screen 3":
            time_pos = TimePos.FULL_3

        logging.debug(f"pressed {time_pos=}")

        draw_image_with_time(file_path, time, time_pos, True, color, True)
            
    return render_template(('clockpi/test.html'))
    
    
@bp.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name)
    

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