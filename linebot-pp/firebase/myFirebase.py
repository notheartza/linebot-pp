from flask import Blueprint
from .config_firebase import firebase_db, firebase_rdb
from ..linebotEvent.linebot import get_time, line_bot_api, clientgs
from ..exsheet import client
from gspread.models import Cell
import json


firebase_api = Blueprint('firebase_api', __name__)


@firebase_api.route('/firebase')
def testfirebase():
    doc_ref = firebase_db.collection(u'users').document(u'BPablo')
    doc_ref.set({
        u'first': u'Boyce',
        u'last': u'Pablo',
        u'born': 1996
    })
    return 'finish'

@firebase_api.route('/firebase/realtime/getUser')
def realtimebase():
    userresults = client.open("linebothistory").get_worksheet(0)
    userssheet = userresults.get_all_records()
    for i in userssheet:
        data = {
            "date": i["date"],
            "userName": i["userName"],
            "pictureProfile": i["pictureProfile"],
            "status": i["สถานะ"],
            "room": i['room'],
            "number": i['number']
        }

        firebase_rdb.child("users").child(i["userId"]).set(data)

    return 'finish'

@firebase_api.route('/firebase/realtime/getlog')
def getLog():
    logresults = client.open("linebothistory").get_worksheet(2)
    logssheet = logresults.get_all_records()
    num = 0
    for i in logssheet:
        get = i['LinebotLog']
        if get is not "" and get[2:8]=='events':
            get_json = json.loads(get)
            userid = get_json['events'][0]['source']['userId']
            firebase_rdb.child("users").child(userid).child("chat").child(num).set({'destination': get_json["destination"], 'events': get_json['events'][0]})
            num = num+1
        #firebase_rdb.child("users").child(i["userId"]).set(data)
            

    return 'finish'   

@firebase_api.route('/firebase/realtime/repair')
def repair():
    user =  firebase_rdb.child('users').get()
    check = user.val()
    for i in check:
        profile = line_bot_api.get_profile(i)
        if firebase_rdb.child('users').child(i).child('userName').get().val() is None:   
            firebase_rdb.child('users').child(i).update({
                'date': get_time(), 
                'userName': profile.display_name, 
                'pictureProfile': profile.picture_url, 
                'statusMessage': profile.status_message,
                'รหัสประจำตัว': "" ,
                'number': "", 
                'room':""     
            })
        else:
            firebase_rdb.child('users').child(i).update({ 
                'pictureProfile': profile.picture_url, 
                'statusMessage': profile.status_message,         
            })
    return 'finish'

@firebase_api.route('/firebase/realtime/userExam/<room>')
def adduser(room):
    print(room)
    studentsheet = clientgs(f"คะแนนนักเรียน ม.4/{room}", client)
    getstudent = studentsheet.get_all_records()
    for i in getstudent:
        if i['ชื่อ']!= "" and i['เลขประจำตัว']!= "":
            firebase_rdb.child('exam').child('user').child(i['เลขประจำตัว']).set({"ชื่อ": i['ชื่อ'], "นามสกุล": i['นามสกุล'], "password": i['เลขประจำตัว'], "เลขที่": i['เลขที่'], "ห้อง": f"ม.4/{room}", "permission": False, 'score': 0 })
    return 'finish'

@firebase_api.route('/firebase/realtime/userPermission/<room>/<sec>')
def adduserwithsec(room, sec):
    print(f"{room} : {sec}")
    print(f" con is {sec is '2'}")
    studentsheet = clientgs(f"คะแนนนักเรียน ม.4/{room}", client)
    getstudent = studentsheet.get_all_records()
    for i in getstudent:
        if i['ชื่อ']!= "" and i['เลขประจำตัว']!= "":
            if sec is '2':
                if int(i['เลขที่']) > 20:
                    firebase_rdb.child('exam').child('user').child(i['เลขประจำตัว']).set({"ชื่อ": i['ชื่อ'], "นามสกุล": i['นามสกุล'], "password": i['เลขประจำตัว'], "เลขที่": i['เลขที่'], "ห้อง": f"ม.4/{room}", "permission": True, 'score': 0 })
            else:
                if int(i['เลขที่']) <= 20:
                    firebase_rdb.child('exam').child('user').child(i['เลขประจำตัว']).set({"ชื่อ": i['ชื่อ'], "นามสกุล": i['นามสกุล'], "password": i['เลขประจำตัว'], "เลขที่": i['เลขที่'], "ห้อง": f"ม.4/{room}", "permission": True, 'score': 0 })
 

 
    return 'finish'

@firebase_api.route('/firebase/realtime/exam')
def addexam():
    for c in range(4):
        sheet = client.open("ข้อสอบกลางภาครายวิชาเทคโนโลยี1/2563").get_worksheet(c)
        getsheet = sheet.get_all_records()
        count = 0
        for i in getsheet:
            chice = {"0": i['1'], "1": i['2'], "2": i['3'], "3": i['4']}
            firebase_rdb.child('exam').child('examinations').child(c).child(count).set({"หน่วย": i['หน่วย'], "หัวข้อ": i['หัวข้อ'], "หัวข้อ": i['หัวข้อ'], "ข้อ": i["ข้อ"], "คำถาม": i['คำถาม'], "เฉลย": i['เฉลย'], "ตัวเลือก": chice})
            count = count + 1
    """
    sheet = client.open("ข้อสอบกลางภาครายวิชาเทคโนโลยี1/2563").get_worksheet(1)
    getsheet = sheet.get_all_records()
    firebase_rdb.child('exam').child('examinations').child('2').set(getsheet)
    sheet = client.open("ข้อสอบกลางภาครายวิชาเทคโนโลยี1/2563").get_worksheet(2)
    getsheet = sheet.get_all_records()
    firebase_rdb.child('exam').child('examinations').child('3').set(getsheet)
    sheet = client.open("ข้อสอบกลางภาครายวิชาเทคโนโลยี1/2563").get_worksheet(3)
    getsheet = sheet.get_all_records()
    firebase_rdb.child('exam').child('examinations').child('4').set(getsheet) 
    """
    return 'finish'


   