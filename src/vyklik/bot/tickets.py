import re

_TICKET_RE = re.compile(r"^[A-Za-z]\d{1,4}$")


def normalize(value: str) -> str:
    return value.strip().upper()


def is_valid(value: str) -> bool:
    return bool(_TICKET_RE.match(value))


def parse(value: str) -> tuple[str, int] | None:
    v = normalize(value)
    if not is_valid(v):
        return None
    return v[0], int(v[1:])


def distance(my: str | None, current: str | None) -> int | None:
    """Tickets remaining before `my` is called. None if either is unparseable
    or the series differ. Negative means we've already been passed."""
    if not my or not current:
        return None
    p_my = parse(my)
    p_cur = parse(current)
    if p_my is None or p_cur is None or p_my[0] != p_cur[0]:
        return None
    return p_my[1] - p_cur[1]
