import gspread
from secret import gsheet_url

# Read google sheet
def googlesheet(sheet):
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open_by_url(gsheet_url)  # Open the file by url
    worksheet = sh.worksheet(sheet)  # Select the sheet inside the file
    worksheet = worksheet.get_all_records()
    return worksheet
