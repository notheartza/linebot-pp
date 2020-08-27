from flask import Flask, request, abort, render_template, url_for, jsonify
import time
import datetime

import json
from .exsheet import client
from gspread.models import Cell
from flask_httpauth import HTTPBasicAuth
from .firebase.config_firebase import firebase_db, firebase_rdb
from .firebase.myFirebase import firebase_api
from .linebotEvent.linebot import linebot_api




#<----TOP---->
app = Flask(__name__) 
#<----BEGIN----->

app.register_blueprint(firebase_api)
app.register_blueprint(linebot_api)


app.config['SECRET_KEY'] = 'my app in pp school'
auth = HTTPBasicAuth()
completetext1 = 'บันทึกเรียบร้อย'
waitingtext = 'กรุณารอสักครู่...'

@auth.verify_password
def verify_password(username, password):
    if username == 'ppAdmin' and password == 'pp2563':
        return username
    else:
        return False


@app.route('/Broadcast', methods=['GET', 'POST'])
@auth.login_required
def Broadcast():
    usersheet = clientgs('usersheet', client)        
    users = usersheet.get_all_records()
    gettype = request.args.get("gettype", default='3')
    
    choices = {'รายบุคคล': '1', 'มากว่า 1 คนขึ้นไป': '2', 'ทั้งหมด':'3'}
    for key, value in choices.items():
        if value == gettype:
            type = key
            break
    print(f"ประเภทข้อความ: {type}")
    if request.method == 'POST':
        if request.form.get('getname')!= "":
            toId = request.form.get('getname')
            text = request.form.get('gettext')
            print(gettype)
            if type == 'รายบุคคล':
                line_bot_api.push_message(toId, TextSendMessage(text=text))
            else:
                line_bot_api.broadcast(TextSendMessage(text=text))
    
    return render_template('Broadcast.html', typeText=type, userline=users)







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

@app.route('/updateProfile')
def upload_Profile():
    userresults = client.open("linebothistory").get_worksheet(0)
    userssheet = userresults.get_all_records()
    c = 2
    for i in userssheet:
        if i["pictureProfile"]=="":
            profile = line_bot_api.get_profile(i["userId"])
            userresults.update_cell( c, 6, f'=IMAGE("{profile.picture_url}", 4, 300, 250)')    

        c = c + 1

    return 'finish'






if __name__ == '__main__':
    app.run(debug=True)
