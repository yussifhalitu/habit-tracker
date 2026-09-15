import gspread
from google.oauth2.service_account import Credentials
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
def get_daily_records(client):
    """Reads all rows from Daily Log."""
    spreadsheet = client.open(SPREADSHEET_NAME)
    daily_sheet = spreadsheet.worksheet("Daily Log")
    return daily_sheet.get_all_records(expected_headers=[
        "Date", "Day of Week", "Week Number",
        "Habit Name", "Category", "Completed", "Notes"
    ])


# ============================================
# CORE LOGIC
# ============================================
def get_unique_weeks(records):
    """Returns sorted list of unique week numbers from Daily Log."""
    return sorted(set(
        int(row["Week Number"]) for row in records
        if row["Week Number"]
    ))


def calculate_week_stats(records, week_number):
    """
    For a given week number, calculates:
    - total habit entries
    - completed habits
    - missed habits
    - completion percentage
    """
    week_rows = [
        row for row in records
        if row["Week Number"] and int(row["Week Number"]) == week_number
    ]

    total = len(week_rows)
    completed = sum(
        1 for row in week_rows
        if row["Completed"] is True
        or str(row["Completed"]).upper() == "TRUE"
    )
    missed = total - completed
    percentage = round((completed / total * 100), 1) if total > 0 else 0

    return {
        "week": week_number,
        "total": total,
        "completed": completed,
        "missed": missed,
        "percentage": f"{percentage}%"
    }


def build_weekly_summary(records):
    """Builds a list of stats dictionaries, one per week."""
    unique_weeks = get_unique_weeks(records)
    weekly_data = []

    for week in unique_weeks:
        stats = calculate_week_stats(records, week)
        weekly_data.append(stats)
        print(f"Week {week}: {stats['completed']}/{stats['total']} ({stats['percentage']})")

    return weekly_data


# ============================================
# SHEET WRITING
# ============================================
def update_weekly_summary(client, weekly_data):
    """Clears Weekly Summary and rewrites it with fresh calculated data."""
    spreadsheet = client.open(SPREADSHEET_NAME)
    weekly_sheet = spreadsheet.worksheet("Weekly Summary")

    # Clear existing data below header
    weekly_sheet.clear()

    # Write header row
    headers = ["Week Number", "Total Habits", "Completed", "Missed", "Completion %"]
    weekly_sheet.update(
        range_name="A1:E1",
        values=[headers]
    )

    # Build rows from weekly data
    rows = []
    for stats in weekly_data:
        row = [
            stats["week"],
            stats["total"],
            stats["completed"],
            stats["missed"],
            stats["percentage"]
        ]
        rows.append(row)

    # Write all rows starting from row 2
    if rows:
        end_row = 1 + len(rows)
        weekly_sheet.update(
            range_name=f"A2:E{end_row}",
            values=rows
        )
        print(f"\nWeekly Summary updated — {len(rows)} weeks written.")


# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    client = authenticate()
    records = get_daily_records(client)
    weekly_data = build_weekly_summary(records)
    update_weekly_summary(client, weekly_data)