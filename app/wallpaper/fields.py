from flask_restx import fields

from . import ns

wallpaper_fields = ns.model("Wallpaper", {
	"id":			fields.Integer(),
	"name": 		fields.String(),
	"hash": 		fields.String(),
	"size": 		fields.Integer(),
	"x":	 		fields.Integer(),
	"y":			fields.Integer(),
	"w":	 		fields.Integer(),
	"h":			fields.Integer(),
	"color": 		fields.String(),
	"shadow": 		fields.String()
})

wallpaper_update_model = ns.model("WallpaperUpdate", {
	"x":		fields.Integer(),
	"y":		fields.Integer(),
	"w":		fields.Integer(),
	"h":		fields.Integer(),
	"color": 	fields.String(),
	"shadow": 	fields.String()
})
