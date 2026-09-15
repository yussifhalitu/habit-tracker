import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from collections import defaultdict


# ============================================
# CONFIGURATION
# ============================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDENTIALS_FILE = "credentials.json"
SPREADSHEET_NAME = "Habit Tracker"
THRESHOLD = 0.70


# ============================================
# AUTHENTICATION
# ============================================
def authenticate():
    """Connects to Google Sheets API and returns an authorized client."""
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client


# ============================================
# DATA RETRIEVAL
# ============================================
def get_all_daily_records(client):
    """Reads all rows from Daily Log and returns them as a list of dicts."""
    spreadsheet = client.open(SPREADSHEET_NAME)
    daily_sheet = spreadsheet.worksheet("Daily Log")
    return daily_sheet.get_all_records(expected_headers=[
        "Date", "Day of Week", "Week Number",
        "Habit Name", "Category", "Completed", "Notes"
    ])


# ============================================
# CORE LOGIC
# ============================================
def group_by_date(records):
    """Groups all habit rows by date into a dictionary."""
    daily_habits = defaultdict(list)
    for row in records:
        if row["Date"]:  # Skip empty rows
            daily_habits[row["Date"]].append(row)
    return daily_habits


def is_successful_day(rows, threshold=THRESHOLD):
    """Returns True if the day's completion rate meets the threshold."""
    total = len(rows)
    if total == 0:
        return False

    completed = sum(
        1 for row in rows
        if row["Completed"] is True
        or str(row["Completed"]).upper() == "TRUE"
    )
    percentage = completed / total
    return percentage >= threshold


def calculate_streaks(daily_habits):
    """
    Calculates current streak and longest streak
    from grouped daily habit data.
    """
    # Sort dates chronologically
    sorted_dates = sorted(
        daily_habits.keys(),
        key=lambda d: datetime.strptime(d, "%Y-%m-%d")
    )

    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    for date_str in sorted_dates:
        rows = daily_habits[date_str]

        if is_successful_day(rows):
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0

    current_streak = temp_streak
    return current_streak, longest_streak

def write_streaks_to_sheet(client, current_streak, longest_streak):
    """Writes current and longest streak to Global Tracker sheet."""
    spreadsheet = client.open(SPREADSHEET_NAME)
    global_tracker = spreadsheet.worksheet("Global Tracker")
    global_tracker.update_acell("G2", current_streak)
    global_tracker.update_acell("H2", longest_streak)
    print(f"Streaks written to Global Tracker — Current: {current_streak}, Longest: {longest_streak}")


def print_streak_report(daily_habits, current_streak, longest_streak):
    """Prints a summary report of streaks and daily performance."""
    sorted_dates = sorted(
        daily_habits.keys(),
        key=lambda d: datetime.strptime(d, "%Y-%m-%d")
    )

    print("\n" + "="*40)
    print("       HABIT STREAK REPORT")
    print("="*40)

    for date_str in sorted_dates:
        rows = daily_habits[date_str]
        total = len(rows)
        completed = sum(
            1 for row in rows
            if row["Completed"] is True
            or str(row["Completed"]).upper() == "TRUE"
        )
        percentage = completed / total if total > 0 else 0
        status = "✅" if is_successful_day(rows) else "❌"
        print(f"{status} {date_str}  {completed}/{total} habits  ({percentage:.0%})")

    print("="*40)
    print(f"🔥 Current Streak : {current_streak} day(s)")
    print(f"🏆 Longest Streak : {longest_streak} day(s)")
    print("="*40 + "\n")


# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    client = authenticate()
    records = get_all_daily_records(client)
    daily_habits = group_by_date(records)
    current_streak, longest_streak = calculate_streaks(daily_habits)
    write_streaks_to_sheet(client, current_streak, longest_streak)
    print_streak_report(daily_habits, current_streak, longest_streak)