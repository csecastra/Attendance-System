from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import logging
from config import SCOPES, SPREADSHEET_ID, RANGE_NAME, CHECK_RANGE, CREDENTIALS_FILE

def init_google_sheets():
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        logging.info("Google Sheets API initialized successfully")
        return service
    except Exception as e:
        logging.error(f"Failed to initialize Google Sheets API: {e}")
        return None

def check_duplicate_name(service, name):
    if service is None:
        logging.error("Google Sheets service not available - skipping duplicate check")
        return False
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=CHECK_RANGE
        ).execute()
        values = result.get('values', [])
        existing_names = [row[0].strip() for row in values if row]
        logging.debug(f"Existing names in sheet: {existing_names}")
        return name.strip() in existing_names
    except Exception as e:
        logging.error(f"Error checking duplicate name in Google Sheets: {e}")
        return False

def append_to_google_sheets(service, name, token):
    if service is None:
        logging.error("Google Sheets service not available - skipping append")
        return
    try:
        values = [[name, token]]
        body = {'values': values}
        logging.debug(f"Appending data to Google Sheets: {values}")
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()
        logging.info(f"Successfully appended {name}, {token} to Google Sheets: {result}")
    except Exception as e:
        logging.error(f"Error appending to Google Sheets: {e}")