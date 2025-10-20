The program is run by streamlit running the 'app.py' file (enter the prompt "streamlit run app.py" into the terminal while inside the project).

Missing for proper running: 
- .env file containing GEMINI_API_KEY
- credentials.json obtained by completing this quick guide: https://developers.google.com/workspace/calendar/api/quickstart/python
- On line 131 in app.py (should translate directly but could be on a line close by), under the comment "# --- Calendar / Planner Toggle ---" , the string saved as source_calendar_id shoulde be changed to the calendar-id of a relevant schedule that the user wants to integrate into the generated schedule


