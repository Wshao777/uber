import openpyxl
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

def main():
    """
    Generates an Excel and CSV roster of the Goddesses from the core JSON data
    and optionally syncs it with Google Sheets.
    """
    # --- Configuration ---
    json_file = 'goddess_truecodes.json'
    filename_xlsx = "goddess_roster_v7.xlsx"
    filename_csv = "goddess_roster_v7.csv"
    sheets_credentials_file = os.getenv('SHEETS_CREDENTIALS', 'your-credentials.json')
    google_sheet_name = "女神軍團幹部名單"

    # --- Load data from JSON ---
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            goddesses = json.load(f)['goddesses']
    except FileNotFoundError:
        print(f"🔥 Error: Core data file '{json_file}' not found. Cannot generate roster.")
        return
    except (KeyError, json.JSONDecodeError) as e:
        print(f"🔥 Error: Could not parse '{json_file}'. Invalid format. Details: {e}")
        return

    # --- Prepare data for export ---
    header = ["階層 (Role)", "名稱 (Name)", "信箱 (Email)", "G-ID", "TrueCode", "等級 (Level)"]

    # Create a list of lists for the data rows
    data_rows = []
    for goddess in goddesses:
        # Generate a dummy email address
        dummy_email = f"{goddess.get('g_id', '').lower()}@lightning-empire.com"
        row = [
            goddess.get('role', 'N/A'),
            goddess.get('name', 'N/A'),
            dummy_email,
            goddess.get('g_id', 'N/A'),
            goddess.get('truecode', 'N/A'),
            goddess.get('level', 'N/A')
        ]
        data_rows.append(row)

    # --- Generate Excel File ---
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "幹部名單_v7"
        ws.append(header)
        for row in data_rows:
            ws.append(row)
        wb.save(filename_xlsx)
        print(f"✅ Successfully generated Excel file: {filename_xlsx}")
    except Exception as e:
        print(f"🔥 Error generating Excel file: {e}")

    # --- Generate CSV File ---
    try:
        with open(filename_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data_rows)
        print(f"✅ Successfully generated CSV file: {filename_csv}")
    except Exception as e:
        print(f"🔥 Error generating CSV file: {e}")

    # --- Sync with Google Sheets ---
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(sheets_credentials_file, scope)
        client = gspread.authorize(creds)
        sheet = client.open(google_sheet_name).sheet1
        sheet.clear()
        sheet.update([header] + data_rows)
        print(f"✅ Successfully synced data with Google Sheet: '{google_sheet_name}'")
    except FileNotFoundError:
        print(f"⚠️ Google Sheets credentials not found at '{sheets_credentials_file}'. Sync skipped.")
    except Exception as e:
        print(f"🔥 Error syncing with Google Sheets: {e}")

if __name__ == '__main__':
    main()
