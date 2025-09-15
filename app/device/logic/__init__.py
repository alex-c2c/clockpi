from csv import Error
import os

from logging import Logger, getLogger
from typing import Sequence

from sqlalchemy import delete, select

from app import db
from app.consts import DIR_APP_UPLOAD
from app.device.models import DeviceModel, DeviceOwnershipModel
from app.lib.errors import api_abort, ErrorCode
from app.schedule.models import ScheduleModel
from app.wallpaper.models import WallpaperModel

from ..consts import *
from ..utils import *


logger: Logger = getLogger(__name__)


"""""
LOGIC
"""""


def can_access_device(user_id:int, device_id: int) -> bool:
	stmt = select(DeviceOwnershipModel.owners).where(DeviceOwnershipModel.device_id == device_id)
	owners: list[int] | None = db.session.scalars(stmt).one_or_none()
	
	if owners is None or len(owners) == 0 or user_id not in owners:
		return False
	
	return True
	

def get_device(user_id: int, device_id: int) -> dict:
	model: DeviceModel | None = db.session.get(DeviceModel, device_id)
	
	if model is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	if not can_access_device(user_id, device_id):
		api_abort(ErrorCode.FORBIDDEN)
	
	return model.to_dict()
	

def get_devices(user_id: int) -> list[dict]:
	stmt = select(DeviceOwnershipModel)
	ownership_models: Sequence[DeviceOwnershipModel]= db.session.scalars(stmt).all()
	
	device_ids: list[int] = []
	for model in ownership_models:
		if user_id in model.owners:
			device_ids.append(model.device_id)
				
	stmt = select(DeviceModel).where(DeviceModel.id.in_(device_ids))
	device_models: Sequence[DeviceModel] = db.session.scalars(stmt).all()

	return [model.to_dict() for model in device_models]


def create_device(user_id: int, payload: dict) -> dict:
	failed_validations: dict = {}
	
	name: str | None = payload.get("name")
	if (err := is_name_valid(name)) is not None:
		failed_validations["name"] = err

	desc: str = payload.get("desc", "")
	if  (err := is_desc_valid(desc)) is not None:
		failed_validations["desc"] = err

	ipv4: str | None = payload.get("ipv4")
	if  (err := is_ipv4_valid(ipv4)) is not None:
		failed_validations["ipv4"] = err
	else:
		select_ip_stmt = select(DeviceModel).where(DeviceModel.ipv4 == ipv4)
		if db.session.execute(select_ip_stmt).scalar_one_or_none() is not None:
			failed_validations["ipv4"] = "'ipv4' already taken."

	type_str: str | None = payload.get("type")
	if (err := is_type_valid(type_str)) is not None:
		failed_validations["type"] = err

	orientation_str: str | None = payload.get("orientation")
	if (err := is_orientation_valid(orientation_str)) is not None:
		failed_validations["orientation"] = err
	
	if len(failed_validations.values()) > 0:
		api_abort(ErrorCode.VALIDATION_ERROR, errors=failed_validations)
	
	device_model: DeviceModel = DeviceModel(
		name, 									# type: ignore
		desc,
		ipv4, 									# type: ignore
		type_str, 								# type: ignore
		Orientation[orientation_str] 	# type: ignore
	)
	
	db.session.add(device_model)
	db.session.flush()
	
	device_ownership_model: DeviceOwnershipModel = DeviceOwnershipModel()
	device_ownership_model.device_id = device_model.id
	device_ownership_model.owners = [user_id]
	
	db.session.add(device_ownership_model)
	
	try:
		db.session.commit()
	except Exception as ex:
		db.session.rollback()
		logger.error(f"Unable to commit to database", ex)
		api_abort(ErrorCode.DATABASE_ERROR)
		
	return device_model.to_dict()


def update_device(user_id: int, device_id: int, payload: dict) -> dict:
	model: DeviceModel | None = db.session.get(DeviceModel, device_id)
	if model is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	if not can_access_device(user_id, device_id):
		api_abort(ErrorCode.FORBIDDEN)
	
	failed_validations: dict = {}
	
	name: str | None = payload.get("name")
	if name is not None:
		if (err := is_name_valid(name)) is not None:
			failed_validations["name"] = err
		else:
			model.name = name

	desc: str | None = payload.get("desc")
	if desc is not None:
		if (err := is_desc_valid(desc)) is not None:
			failed_validations["desc"] = err
		else:
			model.desc = desc
	
	ipv4: str | None = payload.get("ipv4")
	if ipv4 is not None:
		if (err := is_ipv4_valid(ipv4)) is not None:
			failed_validations["ipv4"] = err
		else:
			model.ipv4 = ipv4
	
	
	
	type: str | None = payload.get("type")
	if type is not None:
		if (err := is_type_valid(type)) is not None:
			failed_validations["type"] = err
		else:
			model.update_type(type)
			
	orientation: str | None = payload.get("orientation")
	if orientation is not None:
		if (err := is_orientation_valid(orientation)) is not None:
			failed_validations["orientation"] = err
		else:
			model.update_orientation(Orientation[orientation])
	
	is_draw_grid: bool | None = payload.get("isDrawGrid")
	if is_draw_grid is not None:
		model.is_draw_grid = is_draw_grid
	
	is_enabled: bool | None = payload.get("IsEnabled")
	if is_enabled is not None:
		model.is_enabled = is_enabled
		
	if len(failed_validations.values()) > 0:
		api_abort(ErrorCode.VALIDATION_ERROR, errors=failed_validations)
	
	try:
		db.session.commit()
	except Exception as ex:
		db.session.rollback()
		logger.error(f"Unable to update device ({device_id}): {ex}")
		api_abort(ErrorCode.DATABASE_ERROR)

	return model.to_dict()
	

def delete_device(user_id: int, device_id: int) -> None:
	if db.session.get(DeviceModel, device_id) is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	if not can_access_device(user_id, device_id):
		api_abort(ErrorCode.FORBIDDEN)
	
	# Delete wallpapers
	stmt = select(WallpaperModel.file_name).where(WallpaperModel.device_id == device_id)
	file_names: list[str] = list(db.session.scalars(stmt).all())

	stmt = delete(WallpaperModel).where(WallpaperModel.device_id == device_id)
	db.session.execute(stmt)
	
	# Delete schedules
	stmt = delete(ScheduleModel).where(ScheduleModel.device_id == device_id)
	db.session.execute(stmt)
	
	# Delete ownership
	stmt = delete(DeviceOwnershipModel).where(DeviceOwnershipModel.device_id == device_id)
	db.session.execute(stmt)
	
	# Delete device
	stmt = delete(DeviceModel).where(DeviceModel.id == device_id)
	db.session.execute(stmt)
	
	# Commit
	try:
		db.session.commit()
	except Exception as ex:
		db.session.rollback()
		logger.error(f"Unable to delete rows associated with device resource ({device_id})")
		api_abort(ErrorCode.DATABASE_ERROR)
	
	# Clean up associated files
	for file_name in file_names:
		file_path: str = os.path.join(DIR_APP_UPLOAD, file_name)
		if os.path.isfile(file_path):
			os.remove(file_path)
		else:
			logger.error(f"Unable to find wallpaper file {file_path}")
