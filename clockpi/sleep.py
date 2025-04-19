from logging import Logger, getLogger
from typing import Any
from flask import (
    Blueprint,
    app,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
import flask

from clockpi.consts import *
import clockpi.db as db


bp = Blueprint("sleep", __name__)
logger: Logger = getLogger(__name__)
active: bool = False


class schedule:
    days: tuple[bool, bool, bool, bool, bool, bool, bool]
    time: tuple[int, int, int, int]

    def __init__(
        self,
        days: tuple[bool, bool, bool, bool, bool, bool, bool],
        time: tuple[int, int, int, int],
    ) -> None:
        logger.debug(f"New schedule: {days=} {time=}")

        self.days = days
        self.time = time

    def update(
        self,
        days: tuple[bool, bool, bool, bool, bool, bool, bool] | None = None,
        time: tuple[int, int, int, int] | None = None,
    ) -> None:
        logger.debug(f"schedule update {days=} {time=}")
        if days is not None:
            self.days = days

        if time is not None:
            self.time = time


schedules: dict[int, schedule] = {}


def _validate(time: tuple[int, int, int, int]) -> int:
    if time[0] < 0 or time[0] > 23 or time[1] < 0 or time[1] > 59:
        logger.warning(f"Invalid {time[0]=} {time[1]=}")
        return ERR_SCH_INVALID_START

    if time[2] < 0 or time[2] > 23 or time[3] < 0 or time[3] > 59:
        logger.warning(f"Invalid {time[2]=} {time[3]=}")
        return ERR_SCH_INVALID_END

    return 0


def init() -> None:
    logger.info(f"Initializing schedules")
    data: list[Any] = db.get_sleep_schedules()
    if data is None or len(data) == 0:
        logger.debug(f"No sleep schedules")
        return

    global schedules
    schedules.clear()

    for sch in data:
        id: int = int(sch["id"])
        days: tuple[bool, bool, bool, bool, bool, bool, bool] = tuple(
            True if day == "1" else False for day in sch["days"].split("^")
        )
        time: tuple[int, int, int, int] = tuple(int(t) for t in sch["time"].split("^"))
        schedules[id] = schedule(days, time)


def add(
    days: tuple[bool, bool, bool, bool, bool, bool, bool],
    time: tuple[int, int, int, int],
) -> int:
    logger.info(f"Add {days=} {time=}")

    result: int = _validate(time)
    if result != 0:
        return result

    id: int = db.add_sleep_schedule(days, time)

    global schedules
    schedules[id] = schedule(days, time)


def remove(id: int) -> None:
    logger.info(f"Remove {id=}")

    db.delete_sleep_schedule(id)

    global schedules
    for sch in schedules:
        if sch.id == id:
            schedules.remove(sch)
            return


def update(
    id: int,
    days: tuple[bool, bool, bool, bool, bool, bool, bool],
    time: tuple[int, int, int, int],
) -> None:
    logger.info(f"Update {id=} {days=} {time=}")

    result: int = _validate(time)
    if result != 0:
        return result

    db.update_sleep_schedule(id, days, time)

    global schedules
    schedule = schedules.get(id)
    schedule.update(days, time)


def is_active_now() -> bool:
    global active
    return active


def get_list() -> list:
    schedules = db.get_sleep_schedules()
    sch_list: list = []
    
    for sch in schedules:
        days: tuple[bool, bool, bool, bool, bool, bool, bool] = tuple(
            True if day == "1" else False for day in sch["days"].split("^")
        )
        time: tuple[int, int, int, int] = tuple(int(t) for t in sch["time"].split("^"))
        d: dict = {
            "id": sch["id"],
            "days": days,
            "time": time
        }
        sch_list.append(d)
        
    return sch_list


@bp.route("/sleep")
def index():
    schedules: list = get_list()
    return render_template(
        ("sleep/index.html"),
        schedules=schedules,
    )


@bp.route("/sleep/add", methods=["GET"])
def add():
    db.add_sleep_schedule((False, False, False, False, False, False, False), (0, 0, 0, 0))
    return redirect(location=url_for("sleep.index"))


@bp.route("/sleep/update/<int:id>", methods=["POST"])
def update(id: int):
    mon: bool = True if request.form.get("mon") is not None else False
    tue: bool = True if request.form.get("tue") is not None else False
    wed: bool = True if request.form.get("wed") is not None else False
    thu: bool = True if request.form.get("thu") is not None else False
    fri: bool = True if request.form.get("fri") is not None else False
    sat: bool = True if request.form.get("sat") is not None else False
    sun: bool = True if request.form.get("sun") is not None else False
    
    invalid_data: bool = False
    if request.form.get("start_hr") is None:
        flash(f"Missing starting hours")
        invalid_data = True
            
    if request.form.get("start_min") is None:
        flash(f"Missing starting minutes")
        invalid_data = True
        
    if request.form.get("end_hr") is None:
        flash(f"Missing ending hours")
        invalid_data = True
        
    if request.form.get("end_min") is None:
        flash(f"Missing ending minutes")
        invalid_data = True
    
    if invalid_data:
        return redirect(location=url_for(endpoint="sleep.index"))

    start_hr: int = int(request.form.get("start_hr"))
    start_min: int = int(request.form.get("start_min"))
    end_hr: int = int(request.form.get("end_hr"))
    end_min: int = int(request.form.get("end_min"))
    
    days: tuple[bool, ...] = (mon, tue, wed, thu, fri, sat, sun)
    time: tuple[int, ...] = (start_hr, start_min, end_hr, end_min)
    
    db.update_sleep_schedule(id, days, time)
    
    return redirect(location=url_for(endpoint="sleep.index"))


