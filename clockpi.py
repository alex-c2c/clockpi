import atexit
import http.client
import traceback
from typing import Any
import uuid

from logging import Logger, getLogger

from flask import Flask, Response, g, jsonify, request
from flask_cors import CORS
import werkzeug
import werkzeug.exceptions

from app import api, api_bp, auth, device, session_pkg, user
from app import create_app, redis_controller


logger: Logger = getLogger(__name__)
logger.info("running clockpi.py")


def on_app_exit() -> None:
	logger.info(f"on_app_exit")


app: Flask = create_app()


# API Blueprint + namespaces
app.register_blueprint(api_bp)
auth.append_namespace(api)
device.append_namespace(api)
session_pkg.append_namespace(api)
user.append_namespace(api)


# Redis
redis_controller.init_app(app)
#redis_controller.sub_to_channel()


# Flask CORS x Nextjs
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])


# Register exit callback
atexit.register(on_app_exit)


#logger.debug(app.url_map)
	

@app.before_request
def attach_request_id() -> None:
	req_id = request.headers.get("X-Request-ID")
	g.request_id = req_id or str(uuid.uuid4())


# Handling all unhandled errors
@app.errorhandler(Exception)
def handle_generic_error(error: Exception) -> tuple[Response, int]:
	logger.debug(f"{type(error)} | {error}")
	if isinstance(error, werkzeug.exceptions.HTTPException) or isinstance(error, http.client.HTTPException):
		# HTTP errors
		status_code = getattr(error, "status_code", None) or getattr(error, "code", 500)
		message = getattr(error, "description", None) or str(error) or "HTTP error occurred"
	else:
		# Non-HTTP errors (ValueError, RuntimeError, etc.)
		stack_trace: str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
		logger.error(stack_trace)
		
		status_code = 500
		message = "Internal server error"
		
	response: dict[str, Any] = {
		"message": message,
		"requestId": getattr(g, "request_id", None),
	}
	
	return jsonify(response), status_code

