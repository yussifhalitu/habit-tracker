import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime


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
def get_todays_habits(sheet, today_str):
    """Returns list of habit names logged for today."""
    all_records = sheet.get_all_records(expected_headers=[
        "Date", "Day of Week", "Week Number",
        "Habit Name", "Category", "Completed"
    ])

    todays_habits = [
        row["Habit Name"] for row in all_records
        if str(row["Date"]) == today_str
    ]
    return todays_habits


def find_habit_row(sheet, today_str, habit_name):
    """
    Finds the exact row number where Date = today AND
    Habit Name = habit_name. Returns row number (1-indexed).

    """
    all_records = sheet.get_all_records(expected_headers=[
        "Date", "Day of Week", "Week Number",
        "Habit Name", "Category", "Completed"
    ])

    for index, row in enumerate(all_records):
        date_match = str(row["Date"]) == today_str
        name_match = row["Habit Name"].strip().lower() == habit_name.strip().lower()

        if date_match and name_match:
            # +2 because enumerate starts at 0, and row 1 is the header
            return index + 2

    return None


# ============================================
# CORE LOGIC
# ============================================
def mark_habit(client):
    """Shows today's habits and lets the user mark multiple habits complete."""
    default_date = date.today().strftime("%Y-%m-%d")
    date_input = input(f"Which date? (press Enter for today {default_date}): ").strip()

    if not date_input:
        today_str = default_date
    else:
        try:
            # Validate the date format is correct
            datetime.strptime(date_input, "%Y-%m-%d")
            today_str = date_input
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD (e.g. 2026-08-10)")
            return

    spreadsheet = client.open(SPREADSHEET_NAME)
    daily_sheet = spreadsheet.worksheet("Daily Log")

    # Step 1: Get and display today's habits
    todays_habits = get_todays_habits(daily_sheet, today_str)

    if not todays_habits:
        print(f"No habits logged for {today_str}. Run daily_logger.py first.")
        return

    print(f"\nToday's habits ({today_str}):")
    for habit in todays_habits:
        print(f"  - {habit}")

    print("\nEnter each completed habit one at a time.")
    print("Type 'done' when you're finished.\n")

    # Step 2: Keep asking until the user types "done"
    while True:
        habit_input = input("Which habit did you complete? ").strip()

        # Exit the loop
        if habit_input.lower() == "done":
            print("\nDone marking habits. ✅")
            break

        # Prevent empty input
        if not habit_input:
            print("Please enter a habit name or type 'done'.")
            continue

        # Step 3: Validate input (case-insensitive)
        matched_habit = None

        for habit in todays_habits:
            if habit.strip().lower() == habit_input.lower():
                matched_habit = habit
                break

        if not matched_habit:
            print(
                f"Habit '{habit_input}' not found in today's list. "
                "Check spelling."
            )
            continue

        # Step 4: Find the exact row
        row_number = find_habit_row(
            daily_sheet,
            today_str,
            matched_habit
        )

        if row_number is None:
            print(
                f"Could not locate row for "
                f"'{matched_habit}' on {today_str}."
            )
            continue

        # Check if already marked complete
        current_value = daily_sheet.cell(row_number, 6).value

        if current_value == "TRUE" or current_value is True:
            print(f"'{matched_habit}' is already marked complete.")
            continue

        # Step 5: Update column F (column 6) to TRUE
        daily_sheet.update_cell(row_number, 6, True)

        print(f"✅ '{matched_habit}' marked as complete.")

# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    client = authenticate()
    mark_habit(client)