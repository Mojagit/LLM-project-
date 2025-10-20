# calendar_fetcher.py
import datetime as dt
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_creds
from models import Event, LOCAL_TZ

SCOPES = ['https://www.googleapis.com/auth/calendar']  # read + write access

def get_week_date_range():
    today = dt.datetime.now(LOCAL_TZ)
    week_end = today + dt.timedelta(days=6)
    return today, week_end

def get_calendar_events(calendar_id, max_results=30):
    creds = get_creds(SCOPES)
    try:
        service = build("calendar", "v3", credentials=creds)
        start_time, end_time = get_week_date_range()

        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_time.isoformat(),
            timeMax=end_time.isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = []
        for ev in events_result.get("items", []):
            start_str = ev["start"].get("dateTime", ev["start"].get("date"))
            end_str = ev["end"].get("dateTime", ev["end"].get("date"))
            start_dt = dt.datetime.fromisoformat(start_str.replace("Z", "+00:00")).astimezone(LOCAL_TZ)
            end_dt = dt.datetime.fromisoformat(end_str.replace("Z", "+00:00")).astimezone(LOCAL_TZ)

            events.append(Event(
                summary=ev.get("summary", "No title"),
                start=start_dt,
                end=end_dt,
                location=ev.get("location")
            ))

        return events

    except HttpError as err:
        print(f"❌ Calendar API error: {err}")
        return []
