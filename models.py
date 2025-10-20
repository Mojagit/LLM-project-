# models.py
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Europe/Stockholm")  # change if needed

@dataclass
class Event:
    summary: str
    start: datetime
    end: datetime
    location: str = None
    type: str = None  # optional, useful for planned events

    def start_iso(self):
        return self.start.astimezone(LOCAL_TZ).isoformat()

    def end_iso(self):
        return self.end.astimezone(LOCAL_TZ).isoformat()
