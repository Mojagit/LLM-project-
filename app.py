# app_streamlit.py
import streamlit as st
from datetime import datetime

from calendar_fetcher import get_calendar_events
from scheduler import generate_schedule
from push_to_calendar import push_events
from models import Event
from streamlit_calendar import calendar

# --- Streamlit Page Config ---
st.set_page_config(page_title="Gemini Calendar Planner", page_icon="📅", layout="centered")
st.title("📅 Gemini Calendar Planner")

# --- Session state ---
if "planned_events" not in st.session_state:
    st.session_state.planned_events = []

if "user_input" not in st.session_state:
    st.session_state.user_input = []

if "preference" not in st.session_state:
    st.session_state.preference = "neither"

if "activities" not in st.session_state:
    st.session_state.activities = []

if "source_events" not in st.session_state:
    st.session_state.source_events = []

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Existing Calendar"

# --- Sidebar Preferences ---
st.sidebar.header("🧭 Weekly Planning Settings")
st.sidebar.radio(
    "What type of person are you?",
    ["morning", "night", "neither"],
    key = "preference"
)
# --- Constant activities ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 📆 Constant Activities")

with st.sidebar.form("constant_activity_form"):
    const_name = st.text_input("Activity name", placeholder="e.g. Gym, Piano practice")
    const_day = st.selectbox("Day of week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    const_start_time = st.time_input("Start time")
    const_end_time = st.time_input("End time")
    const_location = st.text_input("Location (optional)")
    submitted = st.form_submit_button("➕ Add Constant Activity")

    if submitted and const_name and const_start_time < const_end_time:
        # Calculate date for next occurrence of the chosen weekday
        from datetime import datetime, timedelta
        today = datetime.now()
        days_ahead = (["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].index(const_day) - today.weekday()) % 7
        next_date = today + timedelta(days=days_ahead)

        start_dt = datetime.combine(next_date.date(), const_start_time)
        end_dt = datetime.combine(next_date.date(), const_end_time)

        new_event = Event(
            summary=const_name,
            start=start_dt,
            end=end_dt,
            location=const_location,
            type="constant"
        )

        # Push to Google Calendar
        push_events([new_event])

        # Add to session + refresh
        st.session_state.source_events.append(new_event)
        st.success(f"✅ Added {const_name} on {const_day} to your calendar!")

        st.rerun()

# --- Activities --- 
st.sidebar.markdown("---")
st.sidebar.markdown("### Activities")

st.session_state.activities = []

st.session_state.exercise = st.sidebar.checkbox("Exercise")
if st.session_state.exercise:
    st.session_state.exercise_freq = st.sidebar.slider(
        "How many times per week?", 1, 7, 3
    )
    st.session_state.activities.append(f"I want to exercise {st.session_state.exercise_freq} times a week.")
else:
    st.session_state.exercise_freq = 0

st.session_state.social = st.sidebar.checkbox("Friends & Social Time")
if st.session_state.social:
    st.session_state.activities.append("I want to include time for friends and social activities.")

st.session_state.gaming = st.sidebar.checkbox("Gaming")
if st.session_state.gaming:
    st.session_state.gaming_freq = st.sidebar.radio(
        "How often do you game?",
        ['Daily', 'Few times a week', 'Once a week', 'Few times a month', 'Rarely']
    )
    st.session_state.activities.append(f"I want include time for gaming. I play {st.session_state.gaming_freq}, so please allocate appropriate time slots.")
else:
    st.session_state.gaming_freq = None

st.session_state.study = st.sidebar.checkbox("Studying")
if st.session_state.study:
    st.session_state.activities.append("I want to include time for study sessions.")

# --- User Input ---
user_input = st.sidebar.text_area("Additional input (one per line):")
st.session_state.user_input = [g.strip() for g in user_input.split("\n") if g.strip()]

# --- Current Settings ---
st.sidebar.markdown("### Current Settings")
activities_summary = [
    f"**Preference:** {st.session_state.preference}",
    f"**Exercise:** {st.session_state.exercise_freq} times/week" if st.session_state.exercise else "**Exercise:** No",
    f"**Social Time:** {'Yes' if st.session_state.social else 'No'}",
    f"**Gaming:** {st.session_state.gaming_freq}" if st.session_state.gaming else "**Gaming:** No",
    f"**Studying:** {'Yes' if st.session_state.study else 'No'}",
    ]
st.sidebar.markdown("  \n".join(activities_summary))

st.sidebar.write(f"**Additional Input:** {', '.join(st.session_state.user_input) if st.session_state.user_input else 'None'}")

# --- Calendar / Planner Toggle ---
source_calendar_id = "dtrmhtfin13lgn4q1cav2534l81nhg8j@import.calendar.google.com"

st.sidebar.markdown("---")
st.sidebar.subheader("📅 View Mode")

# Sidebar symbols: ✅ if AI schedule exists, ❌ if not
ai_status = "✅" if st.session_state.planned_events else "❌"
view_mode = st.sidebar.radio(
    "Choose view:",
    [f"Existing Calendar", f"AI Planned Schedule {ai_status}"],
    index=0 if st.session_state.view_mode == "Existing Calendar" else 1,
)
# Normalize view_mode
st.session_state.view_mode = "Existing Calendar" if "Existing" in view_mode else "AI Planned Schedule"

# --- EXISTING GOOGLE CALENDAR VIEW ---
if st.session_state.view_mode == "Existing Calendar":
    if not st.session_state.source_events:
        with st.spinner("Fetching your next week’s events..."):
            st.session_state.source_events = get_calendar_events(source_calendar_id)

    events = st.session_state.source_events
    if not events:
        st.warning("No events found in your Google Calendar.")
    else:
        st.subheader("📅 Upcoming Week (from Google Calendar)")

        calendar_events = [
            {
                "title": e.summary,
                "start": e.start.isoformat(),
                "end": e.end.isoformat(),
                "color": "#1a73e8",
            }
            for e in events
        ]

        calendar_options = {
            "initialView": "timeGridWeek",
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay",
            },
            "slotMinTime": "00:00:00",
            "slotMaxTime": "24:00:00",
            "slotLabelFormat": {
                "hour": "2-digit",
                "minute": "2-digit",
                "hour12": False  # 24-hour format
            },
        }

        calendar(events=calendar_events, options=calendar_options, key="existing_calendar")

        # --- Generate Schedule Button ---
        st.markdown("---")
        st.markdown("### 🧠 Generate Your AI Weekly Plan")
        if st.button("🧠 Generate Weekly Plan"):
            with st.spinner("Generating your personalized schedule..."):
                plan = generate_schedule(events, st.session_state.preference, st.session_state.user_input, st.session_state.activities)
                st.session_state.planned_events = plan
                st.session_state.view_mode = "AI Planned Schedule"
                st.rerun()

# --- AI GENERATED PLANNED SCHEDULE VIEW ---
elif st.session_state.view_mode == "AI Planned Schedule":
    if not st.session_state.planned_events:
        st.info("❌ No AI-generated schedule yet. Switch to 'Existing Calendar' to generate it.")
    else:
        st.subheader("🤖 AI-Planned Weekly Schedule")

        EVENT_COLORS = {
            "study": "#4285F4",
            "exercise": "#34A853",
            "leisure": "#A142F4",
            "meeting": "#F4B400",
            "routine": "#FB8C00",
            "meal": "#EA4335",
        }

        planned_calendar_events = [
            {
                "title": ev.summary,
                "start": ev.start.isoformat(),
                "end": ev.end.isoformat(),
                "color": EVENT_COLORS.get(ev.type, "#9E9E9E"),
            }
            for ev in st.session_state.planned_events
        ]


        planned_calendar_options = {
            "initialView": "timeGridWeek",
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay",
            },
            "slotMinTime": "00:00:00",
            "slotMaxTime": "24:00:00",
            "slotLabelFormat": {
                "hour": "2-digit",
                "minute": "2-digit",
                "hour12": False  # 24-hour format
            },
        }

        calendar(events=planned_calendar_events, options=planned_calendar_options, key="planned_calendar")

        # --- Action buttons ---
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔁 Regenerate Schedule"):
                with st.spinner("Regenerating your schedule..."):
                    plan = generate_schedule(st.session_state.source_events, st.session_state.preference, st.session_state.user_input, st.session_state.activities)
                    st.session_state.planned_events = plan
                    st.rerun()
        with col2:
            if st.button("✅ Confirm & Push to Google Calendar"):
                with st.spinner("Pushing events to your Gemini calendar..."):
                    push_events(st.session_state.planned_events)
                st.success("✅ Successfully pushed your schedule to Google Calendar!")
