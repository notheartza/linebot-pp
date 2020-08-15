from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
pathname = 'linebot-pp/linebot.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(pathname, scope)
client = gspread.authorize(credentials)

