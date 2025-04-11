import hashlib
import os
from datetime import datetime
import shutil
from flask import current_app
from logging import Logger, getLogger
from clockpi.consts import *
from clockpi.db import add_image, get_image
from clockpi.consts import *
from clockpi.image import procsess_image, validate_image
from clockpi.redis_controller import rpublish, rget
from clockpi.queue import get_queue
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


logger: Logger = getLogger(__name__)


def epd_update() -> None:
    logger.debug(f"epd_update")

    draw_grids: bool = True if rget(SETTINGS_DRAW_GRIDS, "1") == "1" else False
    image_queue: tuple[int] = get_queue()

    if len(image_queue) == 0:
        return

    image = get_image(image_queue[0])
    hash: str = image["hash"] if image is not None else ""

    if len(hash) > 0:
        file_path: str = os.path.join(
            current_app.config["DIR_APP_UPLOAD"], f"{hash}.bmp"
        )
        if not os.path.isfile(file_path):
            file_path = ""

    time: str = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}"

    rpublish(
        f"{MSG_DRAW}^{file_path}^{time}^{image["mode"]}^{image["color"]}^{image["shadow"]}^{'1' if draw_grids else '0'}"
    )


def epd_clear() -> None:
    logger.debug(f"epd_clear")
    rpublish(MSG_CLEAR)


def process_uploaded_file(file: FileStorage) -> int:
    filename: str = file.filename

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if filename == "":
        return ERR_UPLOAD_NO_FILE

    if (
        "." not in filename
        or filename.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS
    ):
        return ERR_UPLOAD_INVALID_EXT

    # secure file name
    filename = secure_filename(file.filename)

    # save file to temp dir
    # TODO: improve location of "uploaded" files so that it doesn't get
    # overwritten by someone else uploading the files with same file name at the same time
    if not os.path.isdir(current_app.config["DIR_TMP_UPLOAD"]):
        os.mkdir(current_app.config["DIR_TMP_UPLOAD"])
    temp_path: str = os.path.join(current_app.config["DIR_TMP_UPLOAD"], filename)
    file.save(temp_path)

    # validate image
    if not validate_image(temp_path):
        os.remove(temp_path)
        return ERR_UPLOAD_INVALID_IMAGE

    # process image
    if not os.path.isdir(current_app.config["DIR_TMP_PROCESSED"]):
        os.mkdir(current_app.config["DIR_TMP_PROCESSED"])

    processed_path: str = os.path.join(
        current_app.config["DIR_TMP_PROCESSED"], filename
    )
    process_result: bool = procsess_image(
        temp_path, processed_path, EPD_WIDTH, EPD_HEIGHT, EPD_NC
    )

    if not process_result:
        if os.path.isfile(temp_path):
            os.remove(temp_path)
        if os.path.isfile(processed_path):
            os.remove(processed_path)
        return ERR_UPLOAD_POST_PROC

    # get hash of processed image
    try:
        h = hashlib.sha256()
        with open(processed_path, "rb") as f:
            while True:
                chunk = f.read(h.block_size)
                if not chunk:
                    break
                h.update(chunk)
        hash: str = h.hexdigest()

    except OSError as error:
        if os.path.isfile(temp_path):
            os.remove(temp_path)
        if os.path.isfile(processed_path):
            os.remove(processed_path)
        return ERR_UPLOAD_HASH

    # copy processed image to upload dir
    try:
        hashname: str = f"{hash}.bmp"
        dest_path: str = os.path.join(current_app.config["DIR_APP_UPLOAD"], hashname)
        shutil.copy2(processed_path, dest_path)
        os.remove(processed_path)

    except OSError as error:
        if os.path.isfile(temp_path):
            os.remove(temp_path)
        if os.path.isfile(processed_path):
            os.remove(processed_path)
        return ERR_UPLOAD_COPY

    # Save upload entry to DB
    try:
        filename_no_ext: str = filename.rsplit(".", 1)[0]
        filesize: int = os.path.getsize(dest_path)

        # Insert to DB
        add_image(filename_no_ext, hash, filesize)

    except OSError as error:
        return ERR_UPLOAD_SAVE

    return 0


def convert_string_to_color(value: str) -> TextColor:
    color: TextColor = TextColor.COLOR_NONE

    if value == "black":
        color = TextColor.COLOR_BLACK
    elif value == "white":
        color = TextColor.COLOR_WHITE
    elif value == "yellow":
        color = TextColor.COLOR_YELLOW
    elif value == "red":
        color = TextColor.COLOR_RED
    elif value == "blue":
        color = TextColor.COLOR_BLUE
    elif value == "green":
        color = TextColor.COLOR_GREEN

    return color


def convert_string_to_mode(value: str) -> TimeMode:
    mode: TimeMode = TimeMode.FULL_3

    if value == "":
        mode = TimeMode.SECT_9_TOP_LEFT
