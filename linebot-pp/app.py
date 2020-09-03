from flask import Flask, request, abort, render_template, url_for, jsonify
from .exsheet import client
from gspread.models import Cell
from .firebase.config_firebase import firebase_db, firebase_rdb
from .firebase.myFirebase import firebase_api
from .linebotEvent.linebot import linebot_api, clientgs
from .linebotview.admin import admin_page





#<----TOP---->
app = Flask(__name__) 
#<----BEGIN----->

app.register_blueprint(firebase_api)
app.register_blueprint(linebot_api)
app.register_blueprint(admin_page)


app.config['SECRET_KEY'] = 'my app in pp school'





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
    return 'Linebot-PP'



if __name__ == '__main__':
    app.run(debug=True)
