from flask_restx import Api, Namespace

ns: Namespace = Namespace("wallpaper", description="Wallpaper operations", path="/1/wallpaper")

def append_namespace(api: Api) -> None:
	# This is to trigger the import of routes
	from . import routes
 
	api.add_namespace(ns)
