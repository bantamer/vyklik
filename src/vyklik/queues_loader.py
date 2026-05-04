from dataclasses import dataclass
from pathlib import Path

import yaml

QUEUES_YML_DEFAULT = Path("/app/queues.yml")


@dataclass(slots=True, frozen=True)
class QueueDisplay:
    id: int
    display_pl: str
    display_ru: str


def load(path: Path | None = None) -> dict[int, QueueDisplay]:
    p = path or QUEUES_YML_DEFAULT
    if not p.exists():
        return {}
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    out: dict[int, QueueDisplay] = {}
    for entry in raw.get("queues", []) or []:
        try:
            qid = int(entry["id"])
        except (KeyError, TypeError, ValueError):
            continue
        out[qid] = QueueDisplay(
            id=qid,
            display_pl=str(entry.get("display_pl") or "").strip() or f"queue {qid}",
            display_ru=str(entry.get("display_ru") or "").strip() or f"очередь {qid}",
        )
    return out


def display_for(
    qid: int, raw_name: str, catalog: dict[int, QueueDisplay]
) -> tuple[str, str]:
    """Return (display_pl, display_ru), falling back to raw_name if not curated."""
    if qid in catalog:
        d = catalog[qid]
        return d.display_pl, d.display_ru
    return raw_name, raw_name
