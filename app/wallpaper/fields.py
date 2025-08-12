from flask_restx import fields

from . import ns

wallpaper_model = ns.model("Wallpaper", {
	"name": fields.String(required=True),
	"hash": fields.String(required=True),
	"size": fields.Integer(required=True),
	"mode": fields.Integer(required=True),
	"color": fields.String(required=True),
	"shadow": fields.String(required=True)
})

wallpaper_update_model = ns.model("WallpaperUpdate", {
	"mode": fields.Integer(),
	"color": fields.String(),
	"shadow": fields.String()
})
