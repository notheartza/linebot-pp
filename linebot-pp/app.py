from flask import Flask, request, abort, render_template
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
import time
import datetime
import pytz
import json
import emoji
from .exsheet import client
from gspread.models import Cell


completetext1 = 'บันทึกเรียบร้อย'
waitingtext = 'กรุณารอสักครู่...'

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

app = Flask(__name__)


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


@app.route('/webhook', methods=['POST'])
def webhook():
    sheetlog = client.open("linebothistory").get_worksheet(2)
    logresults = sheetlog.get_all_records()
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    if len(logresults) > 0:
        sheetlog.insert_row([body, get_time()], len(logresults)+2)
    else:
        sheetlog.insert_row([body, get_time()], 2)
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        Error = "Got exception from LINE Messaging API: %s\n" % e.message
        sheetlog.insert_row([Error, get_time()], len(logresults)+2)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    text = event.message.text
    if text == 'profile':
        userresults = client.open("linebothistory").get_worksheet(0)
        users = userresults.get_all_records()
        for i in users:
            if i["userId"]==event.source.user_id:
                user = i
                break
        username = user["userName"]
        if user["room"] != "":
            room = user["room"]
            room = f"ม.4.{room}"
        else:
            room = 'ยังไม่ได้ระบุ'

        if user["number"] != "":
            number = user["number"]
        else:
            number = 'ยังไม่ได้ระบุ'
        
        text = f"ข้อมูลของคุณมีดังนี้\nID-Line : {username}\nชั้นเรียน : {room}\nเลขที่ : {number}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))
   

    elif 'ห้อง' in text:
        roomselect(event)
    
    elif "เลขที่" in text:
        userssheet = client.open("linebothistory").get_worksheet(0)
        users = userssheet.get_all_records()

        if text.startswith('เลขที่') and len(text.split(' '))>1:
                get_number = text.split(' ')
                #userssheet.update_cell( 2, 8, get_number[1])
                try:
                    number = int(get_number[1])
                    c = 0
                    for i in users:     
                        if i["userId"]==event.source.user_id:
                            userssheet.update_cell( c+2, 5, number)
                            break
                        c = c + 1
                    text = completetext1
                except Exception as e:
                    userssheet.update_cell( 2, 9, str(e))
                    text = 'กรุณากรอกเลขที่ของคุณให้ถูกต้อง[0]'
        
        elif 'เลขที่' in text and len(text)>6:
            splitIndex = text.rfind('เลขที่')
            number = text[splitIndex+6:]
            #userssheet.update_cell( 2, 8, number)
            try:
                number = int(number)
                c = 0
                for i in users:     
                    if i["userId"]==event.source.user_id:
                        userssheet.update_cell( c+2, 5, number)
                        break
                    c = c + 1
                text = completetext1
            except:
                text = 'กรุณากรอกเลขที่ของคุณให้ถูกต้อง[1]'
        
        else:
            text = 'โปรดพิมพ์ "เลขที่" และตามด้วย\nเลขที่ของคุณเช่น เลขที่ 1 หรือ เลขที่1'
            
            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))


  
    elif 'เมนู'in text or 'menu' in text: #เมนูเร่งด่วน
        mainMenu(event)
        
       


    elif 'งาน' in text or text == 'งาน':
        userssheet = client.open("linebothistory").get_worksheet(0)
        logsheet = clientgs('logsheet', client)        
        logs = logsheet.get_all_records()
        users = userssheet.get_all_records()
        c = 0
        
        for i in users:
            if i["userId"]==event.source.user_id:
                user = i
                break
        #userssheet.update_cell( 2, 10, str(user))    
        if user['room'] == "":
            text = 'กรุณาระบุห้องเรียนของคุณ'
        elif user['number'] == "":
            text = 'กรุณาระบบเลขที่ของคุณ'
        else:
            studentsheet = clientgs(f"คะแนนนักเรียน ม.4/{user['room']}", client)
            #logsheet.insert_row([getDataInRoom(user["room"]), get_time()], len(users)+2)
            #logsheet.insert_row([str(studentsheet.get_all_records()), get_time()], len(users)+2)
            getstudent = studentsheet.get_all_records()
            c = 0
            text = ''
            logsheet.insert_row([f"{getstudent[user['number']-1]}", get_time()], len(logs)+2)
            student = getstudent[user['number']-1]
            for key, value in student.items():
                if key=='ชื่อ':
                    text = value
                elif key=='นามสกุล':
                    text = text+" "+value+"\nรายละเอียดงานที่ส่ง\n"
                elif key!='เลขที่' and key!='เลขประจำตัว' and key!='คะแนนพิเศษ':
                   
                    if value =="":
                        x = "รอการตรวจสอบ"
                    elif int(value) < 0:
                        if int(value)  < -1:
                            x = "เกินกำหนดส่ง"
                        else:    
                            x = "ยังไม่ได้ทำ/เกินกำหนดส่งงาน"
                        
                    else:
                        x = "ทำเรียบร้อยแล้ว"
                    text = text + key+" : " + x + "\n"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))
    
    elif 'ช่วยเหลือ' in text or 'help' in text:
        text = "การใช้งานเบื้องต้นของlinebot-pp\n1.กำหนดห้องเรียนของตอนเอง \nโดยพิมพ์คำว่า 'ห้อง'\n2.กำหนดเลขที่ โดยพิมพ์คำว่า 'เลขที่'\n3.ตรวจสอบภาระงาน \nโดยพิมพ์คำว่า 'งาน'\n4.เมนูการใช้งาน โดยพิมพ์คำว่า 'เมนู'"
        line_bot_api.push_message(
            event.source.user_id, [
                TextSendMessage(text=text),
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


    else:
        if(text!='ม.4.2' and text!='ม.4.4' and text!='ม.4.7'and text!='ม.4.9' and text!='nemu' and text!='เมนู'):
            text = 'สงสัยตรงไหนสามารถพิมพ์ "ช่วยเหลือ" ได้เลย'
            line_bot_api.push_message(
            event.source.user_id, [
                TextSendMessage(text=text),
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


@handler.add(FollowEvent)
def handle_follow(event):
    logresults = client.open("linebothistory").get_worksheet(2)  
    userresults = client.open("linebothistory").get_worksheet(0)  
    logsheet = logresults.get_all_records()
    
    usersheet = userresults.get_all_records()
    profile = line_bot_api.get_profile(event.source.user_id)

    c = 0
    for i in usersheet:
        app.logger.info(i)       
        if i["userId"]==event.source.user_id:
            break
        elif c == len(usersheet)-1:
            userresults.insert_row([get_time(), event.source.user_id, profile.display_name,"","", profile.pictureUrl], len(usersheet)+2)
        c = c + 1

    if len(usersheet)==0:
        userresults.insert_row([get_time(), event.source.user_id, profile.display_name,"","", profile.pictureUrl], len(usersheet)+2)

    if(isinstance(event.source, SourceUser)):
        profile = line_bot_api.get_profile(event.source.user_id)
        helptext = "ถ้าต้องการความช่วยหลือ\nสามารถพิมพ์ 'ช่วยเหลือ' หรือ 'help' ได้เลยครับ"
        text = f"สวัสดี {profile.display_name} 😍😍😍\nขอบคุณที่เป็นเพื่อนกับ LineBot-PP\nระบบไลน์บอท(ระบบทดลองใช้งาน)\nของโรงเรียนพิษณุโลกพิทยาคม\nเพื่อติดตามกิจกรรมหรือภาระงาน\nของนักเรียนโรงเรียนพิษณุโลกพิทยาคม"
        line_bot_api.push_message(
            event.source.user_id, [
                TextSendMessage(text=text),
                TextSendMessage(text=helptext),
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

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Bot can't use profile API without user ID")
        )


    


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    app.logger.info("Got Unfollow event:" + event.source.user_id)


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")



@handler.add(PostbackEvent)
def handle_postback(event):
    if "ม.4" in event.postback.data:
        getroom = event.postback.data
        room = getroom.split('.')
        room = room[len(room)-1]
        confirm_template = ConfirmTemplate(text=f"คุณอยู่ ม.4.{room} ใช่ไหม?", 
        actions=[
            PostbackAction(label="ใช่", data=f"rcf4.{room}"),
            PostbackAction(label="ไม่ใช่", data="roomreset")
        ])

        template_message = TemplateSendMessage(
            alt_text='Confirm room', template=confirm_template)        
        line_bot_api.reply_message(event.reply_token, template_message)

    
    elif "rcf4" in event.postback.data:
        userresults = client.open("linebothistory").get_worksheet(0)
        users = userresults.get_all_records()
        getroom = event.postback.data
        room = getroom.split('.')
        room = room[len(room)-1]
        c = 0
        for i in users:     
            if i["userId"]==event.source.user_id:
                userresults.update_cell( c+2, 4 , room)
                userresults.update_cell( c+2, 5 , "")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=completetext1))
                break
            c = c + 1
    
    elif event.postback.data == 'menu':
        mainMenu(event)

    elif event.postback.data == 'roomreset':
        roomselect(event)

    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))


@app.route('/Broadcast')
def Broadcast():
    #line_bot_api.broadcast(TextSendMessage(text='นักเรียนคนไหนยังไม่ได้รับสมุดให้มารับสมุดที่ห้องพักครูคอมพิวเตอร์นะครับ'))
    return render_template('Broadcast.html')

@app.route('/Center')
def Broadcast():
    #line_bot_api.broadcast(TextSendMessage(text='นักเรียนคนไหนยังไม่ได้รับสมุดให้มารับสมุดที่ห้องพักครูคอมพิวเตอร์นะครับ'))
    return render_template('center.html')

if __name__ == '__main__':
    app.run(debug=True)
