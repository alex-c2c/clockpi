from flask import Blueprint, jsonify
from .models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
	return jsonify(message="Welcome to the Flask + PostgreSQL app")
