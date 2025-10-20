# scheduler.py
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from models import Event
from calendar_fetcher import get_week_date_range

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
default_model = "gemini-2.5-flash"

SYSTEM_PROMPT = (
    "You are a helpful AI schedule planner. "
    "Create a balanced weekly schedule for the user from wake-up to bedtime each day. "
    "Include: wake-up, morning routine, breakfast, focused study/work sessions, "
    "physical exercise, lunch, hobbies, relaxation, dinner, and evening wind-down. "
    "Integrate the user's existing calendar events and goals. "
    "Respect the user's energy preference (morning/night). "
    "Return ONLY a JSON array of events. "
    "Each event must have: summary, start (ISO string), end (ISO string), type (study | exercise | leisure | meeting | etc.). "
    "Do NOT include any extra text, explanations, or markdown. "
    "Output strictly as JSON."
)

def generate_schedule(existing_events, preferences, user_input, activiites):
    week_start, week_end = get_week_date_range()

    # Convert existing events to JSON-friendly dicts
    calendar_events_json = [
        {
            "summary": e.summary,
            "start": e.start.isoformat(),
            "end": e.end.isoformat(),
            "type": "meeting"
        }
        for e in existing_events
    ]

    prompt = SYSTEM_PROMPT
    prompt += f"\nUser preference: {preferences}"
    prompt += f"\nUser activities: {activiites}"
    prompt += f"\nUser input: {user_input}"
    prompt += f"\nExisting calendar events: {json.dumps(calendar_events_json)}"
    prompt += f"\nPlan strictly from {week_start.strftime('%A, %B %d, %Y')} to {week_end.strftime('%A, %B %d, %Y')}."
    prompt += "\nDo NOT schedule outside this range. Respond with valid JSON only."

    try:
        result = client.models.generate_content(
            model=default_model,
            contents=prompt
        ).text.strip()

        # Extract JSON using regex (in case Gemini prepends text)
        match = re.search(r"\[.*\]", result, re.DOTALL)
        if not match:
            print("❌ Failed to parse Gemini schedule JSON")
            return []

        events_list = json.loads(match.group(0))

        # Convert to Event objects
        planned_events = []
        for ev in events_list:
            try:
                planned_events.append(
                    Event(
                        summary=ev.get("summary", "No title"),
                        start=datetime.fromisoformat(ev.get("start")),
                        end=datetime.fromisoformat(ev.get("end")),
                        type=ev.get("type", "general")
                    )
                )
            except Exception as e:
                print(f"⚠️ Skipping invalid event: {ev} ({e})")

        return planned_events

    except Exception as e:
        print(f"❌ Schedule generation failed: {str(e)}")
        return []
