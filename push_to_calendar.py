# push_to_calendar.py
from googleapiclient.discovery import build
from auth import get_creds
from models import Event, LOCAL_TZ

SCOPES = ['https://www.googleapis.com/auth/calendar']
GEMINI_CALENDAR_NAME = "Gemini Schedule"

# Map event types to Google Calendar color IDs
EVENT_COLORS = {
    "study": "2",      # blue
    "exercise": "6",   # green
    "leisure": "7",    # purple
    "meeting": "9",    # yellow
    "routine": "10",   # orange
    "meal": "5",       # pink
}

DEFAULT_COLOR_ID = "1"  # gray for unknown types

def get_or_create_gemini_calendar(service):
    calendar_list = service.calendarList().list().execute()
    for cal in calendar_list.get("items", []):
        if cal.get("summary") == GEMINI_CALENDAR_NAME:
            return cal["id"]

    created = service.calendars().insert(body={
        "summary": GEMINI_CALENDAR_NAME,
        "timeZone": "Europe/Stockholm"
    }).execute()
    print(f"✅ Created new calendar '{GEMINI_CALENDAR_NAME}'")
    return created["id"]

def clear_calendar(service, calendar_id):
    total_deleted = 0
    page_token = None

    while True:
        events_result = service.events().list(
            calendarId=calendar_id,
            pageToken=page_token
        ).execute()

        events = events_result.get("items", [])
        for ev in events:
            service.events().delete(
                calendarId=calendar_id,
                eventId=ev["id"]
            ).execute()
            total_deleted += 1

        page_token = events_result.get("nextPageToken")
        if not page_token:
            break

    print(f"🧹 Cleared {total_deleted} events from '{GEMINI_CALENDAR_NAME}'")


def push_events(planned_events):
    creds = get_creds(SCOPES)
    service = build("calendar", "v3", credentials=creds)
    calendar_id = get_or_create_gemini_calendar(service)

    clear_calendar(service, calendar_id)

    for ev in planned_events:
        color_id = EVENT_COLORS.get(ev.type, DEFAULT_COLOR_ID)
        service.events().insert(
            calendarId=calendar_id,
            body={
                "summary": ev.summary,
                "start": {"dateTime": ev.start_iso(), "timeZone": "Europe/Stockholm"},
                "end": {"dateTime": ev.end_iso(), "timeZone": "Europe/Stockholm"},
                "description": f"Type: {ev.type}" if ev.type else None,
                "location": ev.location,
                "colorId": color_id
            }
        ).execute()

    print(f"✅ Pushed {len(planned_events)} events to '{GEMINI_CALENDAR_NAME}'")
