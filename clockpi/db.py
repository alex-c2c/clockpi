import logging
import sqlite3
from datetime import datetime

import click
from flask import current_app, g
 
 
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    
        
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        
        
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
    

def get_settings():
    db = get_db()
    settings = db.execute(
        'SELECT * FROM settings where id = 0'
    ).fetchone()
    return settings
    

def update_settings_image(id:int) -> None:
    db = get_db()
    db.execute(
        'UPDATE settings SET image_id = ? WHERE id = 0', (id,)
    )
    db.commit()
    
    
def update_settings_mode(mode:int) -> None:
    db = get_db()
    db.execute(
        'UPDATE settings SET mode = ? WHERE id = 0', (mode,)
    )
    db.commit()
    

def update_settings_color(color:int) -> None:
    db = get_db()
    db.execute(
        'UPDATE settings SET color = ? WHERE id = 0', (color,)
    )
    db.commit()
    

def update_settings_shadow(shadow:int) -> None:
    db = get_db()
    db.execute(
        'UPDATE settings SET shadow = ? WHERE id = 0', (shadow,)
    )
    db.commit()
    

def update_settings_draw_grids(draw:bool) -> None:
    db = get_db()
    db.execute(
        'UPDATE settings SET draw_grids = ? WHERE id = 0', (1 if draw else 0,)
    )
    db.commit()
    
    
def update_settings_image(id:int) -> None:
    db = get_db()
    db.execute(
        'UPDATE settings SET image_id = ? WHERE id = 0', (id,)
    )
    db.commit()


def update_settings(image_id:int, mode:int, color:int, shadow:int, draw_grids:bool) -> None:
    db = get_db()
    db.execute(
        'UPDATE settings SET image_id = ?, mode = ?, color = ?, shadow = ?, draw_grids = ? WHERE id = 0',
        (image_id, mode, color, shadow, 1 if draw_grids else 0)
    )
    db.commit()


def get_uploads():
    db = get_db()
    uploads = db.execute(
        'SELECT id, name, hash, size, created'
        ' FROM upload'
        ' ORDER BY created DESC'
    ).fetchall() 
    return uploads


def get_upload(id:int):
    db = get_db()
    upload = db.execute(
        'SELECT id, name, hash, size, created'
        ' FROM upload'
        ' WHERE id = ?', (id,)
    ).fetchone() 
    return upload


def add_upload(name:str, hash:str, filesize:int) -> None:
    db = get_db()
    db.execute(
        'INSERT INTO upload (name, hash, size)'
        ' VALUES (?, ?, ?)',
        (name, hash, filesize)
    )
    db.commit()


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)