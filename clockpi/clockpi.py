import os
import tempfile
import shutil
import hashlib
import logging
import subprocess
from datetime import datetime
from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for, send_from_directory
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from clockpi.auth import login_required
from clockpi.db import get_db
from clockpi.image import procsess_image, validate_image
from clockpi.epd import clear_display, draw_image_with_time, TimeMode, COLOR_BLACK, COLOR_WHITE, COLOR_YELLOW, COLOR_RED, COLOR_BLUE, COLOR_GREEN

bp = Blueprint('clockpi', __name__)
logging.basicConfig(level=logging.DEBUG)

# E-Paper Display Width
EPD_WIDTH:int = 800

# E-Paper Display Height
EPD_HEIGHT:int = 480

# E-Paper Display color per channel
NC:int = 2

# Allowed upload file extensions
ALLOWED_EXTENSIONS : set[str] = ('png', 'jpg', 'jpeg', 'bmp')

# Directories
DIR_UPLOAD:str = "upload"
DIR_PROCESSED:str = "processed"

current_mode:int = TimeMode.SECT_4_BOTTOM_LEFT
current_color:int = COLOR_WHITE
current_shadow:int|None = COLOR_BLACK

def allowed_file(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            temp_dir:str = os.path.join(tempfile.gettempdir(), DIR_UPLOAD)
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
            proc_dir:str = os.path.join(temp_dir, DIR_PROCESSED)
            if not os.path.isdir(proc_dir):
                os.mkdir(proc_dir)
            processed_path:str = os.path.join(proc_dir, filename)
            process_result:bool = procsess_image(temp_path, processed_path, EPD_WIDTH, EPD_HEIGHT, NC)
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
                dest_path:str = os.path.join(DIR_UPLOAD, f"{hashname}.bmp")
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
            draw_image_with_time(dest_path, time, current_mode, current_color, current_shadow)
            
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
        file_path:str = os.path.join(DIR_UPLOAD, "01fe482628b58eb16f05fbb698063d652261a8ca79e3366d472f003c6168bbb3.bmp")
        time:str = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}"
        mode:TimeMode = TimeMode.OFF
        
        # Get Refresh flag
        if request.form.get("clear", ""):
            clear_display()
            return render_template(('clockpi/test.html'))
                
        # Get Draw Grids flag
        draw_grids:bool = request.form.get("draw_grids", "") == "true"
        
        # Get Color
        if request.form.get("color", "") == "black":
            current_color = COLOR_BLACK
        elif request.form.get("color", "") == "white":
            current_color = COLOR_WHITE
        elif request.form.get("color", "") == "yellow":
            current_color = COLOR_YELLOW
        elif request.form.get("color", "") == "red":
            current_color = COLOR_RED
        elif request.form.get("color", "") == "blue":
            ccurrent_colorlor = COLOR_BLUE
        elif request.form.get("color", "") == "green":
            current_color = COLOR_GREEN
        
        # Get Shadow
        if request.form.get("shadow", "") == "black":
            current_shadow = COLOR_BLACK
        elif request.form.get("shadow", "") == "white":
            current_shadow = COLOR_WHITE
        elif request.form.get("shadow", "") == "yellow":
            current_shadow = COLOR_YELLOW
        elif request.form.get("shadow", "") == "red":
            current_shadow = COLOR_RED
        elif request.form.get("shadow", "") == "blue":
            current_shadow = COLOR_BLUE
        elif request.form.get("shadow", "") == "green":
            current_shadow = COLOR_GREEN
        else:
            current_shadow = None
        
        # Get Position
        if request.form.get("btn_nine_section", "") == "Top Left":
            current_mode = TimeMode.SECT_9_TOP_LEFT
        elif request.form.get("btn_nine_section", "") == "Top Center":
            current_mode = TimeMode.SECT_9_TOP_CENTER
        elif request.form.get("btn_nine_section", "") == "Top Right":
            current_mode = TimeMode.SECT_9_TOP_RIGHT
        elif request.form.get("btn_nine_section", "") == "Middle Left":
            current_mode = TimeMode.SECT_9_MIDDLE_LEFT
        elif request.form.get("btn_nine_section", "") == "Middle Center":
            current_mode = TimeMode.SECT_9_MIDDLE_CENTER
        elif request.form.get("btn_nine_section", "") == "Middle Right":
            current_mode = TimeMode.SECT_9_MIDDLE_RIGHT
        elif request.form.get("btn_nine_section", "") == "Bottom Left":
            current_mode = TimeMode.SECT_9_BOTTOM_LEFT
        elif request.form.get("btn_nine_section", "") == "Bottom Center":
            current_mode = TimeMode.SECT_9_BOTTOM_CENTER
        elif request.form.get("btn_nine_section", "") == "Bottom Left":
            current_mode = TimeMode.SECT_9_BOTTOM_RIGHT
        elif request.form.get("btn_six_section", "") == "Top Left":
            current_mode = TimeMode.SECT_6_TOP_LEFT
        elif request.form.get("btn_six_section", "") == "Top Right":
            current_mode = TimeMode.SECT_6_TOP_RIGHT
        elif request.form.get("btn_six_section", "") == "Middle Left":
            current_mode = TimeMode.SECT_6_MIDDLE_LEFT
        elif request.form.get("btn_six_section", "") == "Middle Right":
            current_mode = TimeMode.SECT_6_MIDDLE_RIGHT
        elif request.form.get("btn_six_section", "") == "Bottom Left":
            current_mode = TimeMode.SECT_6_BOTTOM_LEFT
        elif request.form.get("btn_six_section", "") == "Bottom Right":
            current_mode = TimeMode.SECT_6_BOTTOM_RIGHT
        elif request.form.get("btn_four_section", "") == "Top Left":
            current_mode = TimeMode.SECT_4_TOP_LEFT
        elif request.form.get("btn_four_section", "") == "Top Right":
            current_mode = TimeMode.SECT_4_TOP_RIGHT
        elif request.form.get("btn_four_section", "") == "Bottom Left":
            current_mode = TimeMode.SECT_4_BOTTOM_LEFT
        elif request.form.get("btn_four_section", "") == "Bottom Right":
            current_mode = TimeMode.SECT_4_BOTTOM_RIGHT
        elif request.form.get("btn_full", "") == "Full Screen 1":
            current_mode = TimeMode.FULL_1
        elif request.form.get("btn_full", "") == "Full Screen 2":
            current_mode = TimeMode.FULL_2
        elif request.form.get("btn_full", "") == "Full Screen 3":
            current_mode = TimeMode.FULL_3

        logging.debug(f"pressed {current_mode=}")

        p= subprocess.run(['python', 'clockpi/epd.py'])
        logging.debug(f"{p.returncode=}")
        #draw_image_with_time(file_path, time, current_mode, current_color, current_shadow, draw_grids)
            
    return render_template(('clockpi/test.html'))
    
    
@bp.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(DIR_UPLOAD, name)
    

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
