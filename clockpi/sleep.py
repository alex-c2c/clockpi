from logging import Logger, getLogger
from typing import Any
from flask import (
    Blueprint,
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from clockpi.consts import *
from clockpi import db, job_scheduler


class sleep_schedule:
    days: tuple[bool, bool, bool, bool, bool, bool, bool]
    time: tuple[int, int, int, int]

    def __init__(
        self,
        days: tuple[bool, bool, bool, bool, bool, bool, bool],
        time: tuple[int, int, int, int],
    ) -> None:
        logger.debug(f"New sleep_schedule: {days=} {time=}")

        self.days = days
        self.time = time

    def update(
        self,
        days: tuple[bool, bool, bool, bool, bool, bool, bool] | None = None,
        time: tuple[int, int, int, int] | None = None,
    ) -> None:
        logger.debug(f"sleep_schedule update {days=} {time=}")
        if days is not None:
            self.days = days

        if time is not None:
            self.time = time


bp = Blueprint("sleep", __name__)
logger: Logger = getLogger(__name__)
schedules: list[sleep_schedule] = []
active: bool = False


def _validate(time: tuple[int, int, int, int]) -> int:
    if time[0] < 0 or time[0] > 23 or time[1] < 0 or time[1] > 59:
        logger.warning(f"Invalid {time[0]=} {time[1]=}")
        return ERR_SCH_INVALID_START

    if time[2] < 0 or time[2] > 23 or time[3] < 0 or time[3] > 59:
        logger.warning(f"Invalid {time[2]=} {time[3]=}")
        return ERR_SCH_INVALID_END

    return 0


def init(app: Flask) -> None:
    logger.info(f"Initializing sleep_schedules")

    with app.app_context():
        # Clear existing list
        global schedules
        schedules.clear()

        # Get from DB and check if empty
        data: list[Any] = db.get_sleep_schedules()
        if data is None or len(data) == 0:
            logger.debug(f"No sleep schedules")
            return

        # Initializing list
        for sch in data:
            days: tuple[bool, bool, bool, bool, bool, bool, bool] = tuple(
                True if day == "1" else False for day in sch["days"].split("^")
            )
            id: int = sch["id"]
            time: tuple[int, int, int, int] = tuple(
                int(t) for t in sch["time"].split("^")
            )
            sch_dict: dict = {"id": id, "days": days, "time": time}
            schedules.append(sch_dict)

            # Add cron jobs
            job_scheduler.add_or_update_cron_job(
                f"job_set_sleep_active_{id}",
                func=set_sleep_active,
                hr=time[0],
                min=time[1],
                days=days,
            )
            job_scheduler.add_or_update_cron_job(
                f"job_set_sleep_inactive_{id}",
                func=set_sleep_inactive,
                hr=time[2],
                min=time[3],
                days=days,
            )


def _add(
    days: tuple[bool, bool, bool, bool, bool, bool, bool],
    time: tuple[int, int, int, int],
    add_job: bool = False,
) -> int:
    logger.info(f"Add {days=} {time=}")

    # validate inputs
    result: int = _validate(time)
    if result != 0:
        return result

    # Add to DB
    id: int = db.add_sleep_schedule(days, time)

    # Add to list
    global schedules
    sch_dict: dict = {"id": id, "days": days, "time": time}
    schedules.append(sch_dict)

    if add_job:
        job_scheduler.add_or_update_cron_job(
            f"job_set_sleep_active_{id}",
            func=set_sleep_active,
            hr=time[0],
            min=time[1],
            days=days,
        )
        job_scheduler.add_or_update_cron_job(
            f"job_set_sleep_inactive_{id}",
            func=set_sleep_inactive,
            hr=time[2],
            min=time[3],
            days=days,
        )


def _remove(id: int) -> None:
    logger.info(f"Remove {id=}")

    # Remove from DB
    db.delete_sleep_schedule(id)

    # Remove from list
    global schedules
    for sch in schedules:
        if sch.id == id:
            schedules.remove(sch)
            return

    # Remove jobs
    job_scheduler.remove_job(f"job_make_sleep_active_{id}")
    job_scheduler.remove_job(f"job_make_sleep_inactive{id}")


def _update(
    id: int,
    days: tuple[bool, bool, bool, bool, bool, bool, bool],
    time: tuple[int, int, int, int],
) -> bool:
    logger.info(f"Update {id=} {days=} {time=}")

    # Validate inputs
    result: int = _validate(time)
    if result != 0:
        return result

    # Update DB
    db.update_sleep_schedule(id, days, time)

    # Update list
    global schedules
    for sch in schedules:
        if sch["id"] == id:
            sch["days"] = days
            sch["time"] = time
            break

    # Reschedule cron jobs
    job_scheduler.add_or_update_cron_job(
        f"job_set_sleep_active_{id}",
        func=set_sleep_active,
        hr=time[0],
        min=time[1],
        days=days,
    )
    job_scheduler.add_or_update_cron_job(
        f"job_set_sleep_inactive_{id}",
        func=set_sleep_inactive,
        hr=time[2],
        min=time[3],
        days=days,
    )

    return True


def set_sleep_active() -> None:
    global active
    active = True
    logger.debug(f"set_sleep_active")


def set_sleep_inactive() -> None:
    global active
    active = False
    logger.debug(f"set_sleep_inactive")


def is_active_now() -> bool:
    global active
    logger.debug(f"is_active_now: {active=}")
    return active


@bp.route("/sleep")
def index():
    global schedules
    return render_template(
        ("sleep/index.html"),
        schedules=schedules,
    )


@bp.route("/sleep/add", methods=["GET"])
def add():
    if request.method != "GET":
        flash(f"Invalid method")
        return redirect(location=url_for("sleep.index"))

    _add((False, False, False, False, False, False, False), (0, 0, 0, 0))

    return redirect(location=url_for("sleep.index"))


@bp.route("/sleep/remove/<int:id>", methods=["GET"])
def remove(id: int):
    if request.method != "GET":
        flash(f"Invalid method")
        return redirect(location=url_for("sleep.index"))

    _remove(id)

    return redirect(location=url_for("sleep.index"))


@bp.route("/sleep/update/<int:id>", methods=["POST"])
def update(id: int):
    if request.method != "POST":
        flash(f"Invalid method")
        return redirect(location=url_for("sleep.index"))

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

    _update(id, days, time)

    return redirect(location=url_for(endpoint="sleep.index"))
