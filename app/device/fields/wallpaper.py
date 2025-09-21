from flask_restx import fields

from .. import ns


wallpaper_fields = ns.model("Wallpaper", {
	"id":			fields.Integer(),
	"name": 		fields.String(),
	"hash": 		fields.String(),
	"size": 		fields.Integer(),
	"fileName":		fields.String(),
	"labelXPer":	fields.Float(),
	"labelYPer":	fields.Float(),
	"labelWPer":	fields.Float(),
	"labelHPer":	fields.Float(),
	"color": 		fields.String(),
	"shadow": 		fields.String()
})


wallpaper_update_fields = ns.model("WallpaperUpdate", {
	"labelXPer":	fields.Float(),
	"labelYPer":	fields.Float(),
	"labelWPer":	fields.Float(),
	"labelHPer":	fields.Float(),
	"color": 		fields.String(),
	"shadow": 		fields.String()
})
