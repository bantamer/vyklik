from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Warsaw")
_DOW = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


def parse_schedule(spec: str) -> dict[int, tuple[int, int]]:
    """Parse 'mon=8-16,tue=8-16,...' into {dow: (start_hour, end_hour)}.

    end_hour is exclusive: '8-16' means [8:00, 16:00).
    """
    result: dict[int, tuple[int, int]] = {}
    for chunk in (spec or "").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            day, hours = chunk.split("=", 1)
            start, end = hours.split("-", 1)
            result[_DOW[day.strip().lower()]] = (int(start), int(end))
        except (KeyError, ValueError) as exc:
            raise ValueError(f"bad WORK_HOURS chunk {chunk!r}: {exc}") from exc
    return result


def is_working(now_utc: datetime, schedule: dict[int, tuple[int, int]]) -> bool:
    local = now_utc.astimezone(TZ)
    window = schedule.get(local.weekday())
    if window is None:
        return False
    start, end = window
    return start <= local.hour < end
