from flask import Blueprint
from .config_firebase import firebase_db, firebase_rdb
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
    for i in logssheet:
        get = i['LinebotLog']
        print(type(get))
        get = json.load(get)
        print(get)
        #firebase_rdb.child("users").child(i["userId"]).set(data)

    return 'finish'    