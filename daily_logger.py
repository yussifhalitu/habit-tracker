import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import sys


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
def get_active_habits(client):
    """Reads Habits Config sheet, returns only habits marked Active."""
    spreadsheet = client.open(SPREADSHEET_NAME)
    config_sheet = spreadsheet.worksheet("Habits Config")
    records = config_sheet.get_all_records()

    active_habits = [
        row for row in records
        if str(row["Active"]).strip().lower() == "yes"
    ]
    return active_habits


def already_logged_today(sheet, today_str):
    """Checks if today's date already exists in the Daily Log."""
    try:
        date_column = sheet.col_values(1)
    except gspread.exceptions.APIError as e:
        print(f"Error reading sheet: {e}")
        sys.exit(1)

    return today_str in date_column


# ============================================
# CORE LOGIC
# ============================================
def get_first_empty_row(sheet):
    """Returns the row number of the first empty row after existing data."""
    all_values = sheet.get("A:A")
    return len(all_values) + 1

def log_habits(client):
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    day_of_week = today.strftime("%A")
    week_number = today.isocalendar()[1]

    spreadsheet = client.open(SPREADSHEET_NAME)
    daily_sheet = spreadsheet.worksheet("Daily Log")
    habits = get_active_habits(client)

    print(f"Found {len(habits)} active habits.")

    if already_logged_today(daily_sheet, today_str):
        print(f"Habits already logged for {today_str}. Skipping.")
        return

    # Find exact row to start writing from
    first_empty_row = get_first_empty_row(daily_sheet)

    rows_to_append = []
    for habit in habits:
        row = [
            today_str,
            day_of_week,
            week_number,
            habit["Habit Name"],
            habit["Category"],
            "FALSE",
            ""
        ]
        rows_to_append.append(row)

    if rows_to_append:
        # Write to exact range instead of blindly appending
        end_row = first_empty_row + len(rows_to_append) - 1
        cell_range = f"A{first_empty_row}:G{end_row}"
        daily_sheet.update(range_name=cell_range, values=rows_to_append, value_input_option="USER_ENTERED")
        print(f"Logged {len(rows_to_append)} habits for {today_str} (Week {week_number})")

# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    client = authenticate()
    log_habits(client)