from flask import Flask, request, abort, render_template, url_for, jsonify
import time
import datetime
import pytz
import json
from .exsheet import client
from gspread.models import Cell
from flask_httpauth import HTTPBasicAuth
from .firebase.config_firebase import firebase_db, firebase_rdb
from .firebase.myFirebase import firebase_api
from .linebotEvent.linebot import linebot_api
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError, LineBotApiError)
from linebot.models import ( MessageEvent, TextMessage, TextSendMessage,SourceUser, SourceGroup, SourceRoom,TemplateSendMessage, ConfirmTemplate, MessageAction, ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,PostbackAction, DatetimePickerAction,CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,SeparatorComponent, QuickReply, QuickReplyButton,ImageSendMessage
    ,ThingsEvent, ScenarioResult,BroadcastResponse,MessageDeliveryBroadcastResponse)




#<----TOP---->
app = Flask(__name__) 
#<----BEGIN----->

app.register_blueprint(firebase_api)
app.registor_blueprint()


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




def clientgs(nameclient, client):
    if nameclient=="usersheet":
        return client.open("linebothistory").get_worksheet(0)
    elif nameclient=="logsheet":
        return client.open("linebothistory").get_worksheet(2)
    else:

        return client.open(nameclient).get_worksheet(0)

def newhelp(event):
    text = "ถ้าต้องการความช่วยหลือสามารถพิมพ์ 'ช่วยเลือ' หรือ 'help' ได้เลยครับ"
    line_bot_api.push_message(
            event.reply_token, 
            TextSendMessage(text=text))

def get_time():
    timezone = pytz.timezone('Asia/Bangkok')
    now = datetime.datetime.now(timezone)
    month_name = 'x มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม กันยายน ตุลาคม พฤศจิกายน ธันวาคม'.split()[now.month]
    thai_year = now.year + 543
    timenow = now.strftime('%H:%M:%S')
    return  "%d %s %d %s"%(now.day, month_name, thai_year, timenow)

def roomselect(event):
    buttons_template = ButtonsTemplate(
        title='ห้องเรียนของคุณ', text='โปรดเลือกห้องของคุณ', 
        actions=[
            PostbackAction(label='ม.4.2', data='ม.4.2'),
            PostbackAction(label='ม.4.4', data='ม.4.4'),
            PostbackAction(label='ม.4.7', data='ม.4.7'),
            PostbackAction(label='ม.4.9', data='ม.4.9')
        ])
    template_message = TemplateSendMessage(
        alt_text='เลือกห้องเรียนของคุณ', template=buttons_template)
    return line_bot_api.reply_message(event.reply_token, template_message)    


def mainMenu(event):
    line_bot_api.push_message(
            event.source.user_id, [
                TextSendMessage(
                text='โปรดเลือเมนูด้านล่าง',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="ตรวจสอบภาระงาน", text="งาน")
                        ),
                       QuickReplyButton(
                            action=MessageAction(label="กำหนดเลขที่", text="เลขที่")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="กำหนดห้องเรียน", text="ห้อง")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="ช่วยเหลือ", text="ช่วยเหลือ")
                        ),
                    ]
                )
            )
            ]
        )
        

def getDataInRoom(room):
        return f"คะแนนนักเรียน ม.4/{room}"

        




line_bot_api = LineBotApi(
    'nMwl+f26OapSLijr4lrUrd9S7oV92Rp6uEj5EA6FiwuonmFIDO8yaFIpwa1xBygBUmi4ZDJ5JrzDEe3vilGB1PsjR+99dvvJt0QEJyVMWLHSlD9/epPR1xgQPssw7+tEDlwBOvbb8BO0jOVgja/Y4QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('da3242391b2f72d623b1fa0cb11288a1')


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
