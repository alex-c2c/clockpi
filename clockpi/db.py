import sqlite3
from datetime import datetime
from typing import Any

import click
from flask import current_app, g
from logging import Logger, getLogger


logger: Logger = getLogger(__name__)


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def get_images():
    db = get_db()
    images = db.execute("SELECT * FROM image ORDER BY created ASC").fetchall()
    return images


def get_image(id: int):
    db = get_db()
    image = db.execute("SELECT * FROM image WHERE id = ?", (id,)).fetchone()
    return image


def add_image(name: str, hash: str, filesize: int) -> int:
    db = get_db()
    cursor = db.execute(
        "INSERT INTO image (name, hash, size) VALUES (?, ?, ?)",
        (name, hash, filesize),
    )
    db.commit()

    return cursor.lastrowid


def remove_image(id: int) -> None:
    db = get_db()
    db.execute("DELETE FROM image WHERE id = ?", (id,))
    db.commit()


def update_image(id: int, mode: int, color: int, shadow: int) -> None:
    db = get_db()
    db.execute(
        "UPDATE image SET mode = ?, color = ?, shadow = ? WHERE id = ?",
        (mode, color, shadow, id),
    )
    db.commit()


def get_sleep_schedules() -> list[Any]:
    db = get_db()
    sleep_schdedules = db.execute("SELECT * FROM sleep_schedule ORDER BY id").fetchall()
    return sleep_schdedules


def remove_sleep_schedule(id: int) -> None:
    db = get_db()
    db.execute("DELETE FROM sleep_schedule WHERE id = ?", (id,))
    db.commit()


def add_sleep_schedule(
    days: tuple[bool, bool, bool, bool, bool, bool, bool],
    time: tuple[int, int, int, int],
) -> int:
    db = get_db()
    cursor = db.execute(
        "INSERT INTO sleep_schedule (days, time) VALUES (?, ?)",
        ("^".join("1" if d else "0" for d in days), "^".join(str(t) for t in time)),
    )
    db.commit()

    return cursor.lastrowid


def update_sleep_schedule(
    id: int,
    days: tuple[bool, bool, bool, bool, bool, bool, bool],
    time: tuple[int, int, int, int],
) -> None:
    db = get_db()
    db.execute(
        "UPDATE sleep_schedule SET days = ?, time = ? WHERE id = ?",
        ("^".join("1" if d else "0" for d in days), "^".join(str(t) for t in time), id),
    )
    db.commit()


sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))
