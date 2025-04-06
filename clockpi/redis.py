'''
from doctest import debug
import logging
from typing import Any
from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for, send_from_directory
from redis import Redis

bp = Blueprint('redis', __name__)
logging.basicConfig(level=logging.DEBUG)

@bp.route('/redis/get', methods=['GET'])
def redis_get():
    if request.method != 'GET':
        return redirect(url_for('clockpi.test'))

    r:Redis = current_app.extensions["redis"]
    busy:bool = r.get('busy')
    logging.debug(f"{busy=}")
    
    test:Any = r.get('newnew')
    logging.debug(f"{test=}")
    
    return redirect(url_for('clockpi.test'))

@bp.route('/redis/set/<int:busy>', methods=['GET'])
def redis_set(busy:int):
    if request.method != 'GET':
        return redirect(url_for('clockpi.test'))
    
    r:Redis = current_app.extensions["redis"]
    r.set('busy', 0 if busy == 0 else 1)

    return redirect(url_for('clockpi.test'))
'''