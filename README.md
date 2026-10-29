# Habit Tracker: Python & Google Sheets Automation

A personal habit tracking system that automatically logs daily habits, tracks completion rates, calculates streaks, and displays progress through a live Google Sheets dashboard.

Built with Python and the Google Sheets API. Runs automatically at login via Windows Task Scheduler.

## Features
- Auto-logs daily habits from a master config sheet
- Marks habits complete interactively from the terminal, including past dates
- Calculates current and longest streaks at a 70% daily threshold
- Auto-generates weekly performance summaries
- Live dashboard with progress bars, weekly trend chart, and streak display

## Tech Used
Python, Google Sheets API, gspread, google-auth, Windows Task Scheduler

Add three sections:
Setup: create the Google Cloud service account, share the sheet with its email, and run pip install -r requirements.txt.
Daily usage: the four scripts and when to run each. daily_logger.py runs automatically at login. Run habit_marker.py in the evening, and streak_calculator.py and weekly_updater.py when you want fresh numbers.
Limitations: it needs an internet connection, because every script calls the Google Sheets API.

Setup: create the Google Cloud service account, share the sheet with its email, and run pip install -r requirements.txt.
Daily usage: the four scripts and when to run each. daily_logger.py runs automatically at login. Run habit_marker.py in the evening, and streak_calculator.py and weekly_updater.py when you want fresh numbers.
Limitations: it needs an internet connection, because every script calls the Google Sheets API.