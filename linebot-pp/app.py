from flask import Flask, request, abort, render_template, url_for, jsonify
from .exsheet import client
from gspread.models import Cell
from .firebase.config_firebase import firebase_db, firebase_rdb
from .firebase.myFirebase import firebase_api
from .linebotEvent.linebot import linebot_api, clientgs





#<----TOP---->
app = Flask(__name__) 
#<----BEGIN----->

app.register_blueprint(firebase_api)
app.register_blueprint(linebot_api)


app.config['SECRET_KEY'] = 'my app in pp school'
auth = HTTPBasicAuth()
completetext1 = 'บันทึกเรียบร้อย'
waitingtext = 'กรุณารอสักครู่...'











@app.route('/test')
def mytest():
    sheet = client.open("linebothistory").get_worksheet(2)
    results = sheet.get_all_records()
    print(results)
    print(len(results))
    row = ['สวัสดี']
    sheet.insert_row(row, 2)
    return 'finish'





@app.route('/')
def hello_world():
    return 'Hello World!'








if __name__ == '__main__':
    app.run(debug=True)
