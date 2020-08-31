from flask import Flask, request, abort, render_template, url_for, Blueprint
from flask_httpauth import HTTPBasicAuth
from ..linebotEvent.linebot import line_bot_api, clientgs
from ..exsheet import client
from linebot.models import ( MessageEvent, TextMessage, TextSendMessage,SourceUser, SourceGroup, SourceRoom,TemplateSendMessage, ConfirmTemplate, MessageAction, ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,PostbackAction, DatetimePickerAction,CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,ImageMessage, VideoMessage, AudioMessage, FileMessage,UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,TextComponent, SpacerComponent, IconComponent, ButtonComponent,SeparatorComponent, QuickReply, QuickReplyButton,ImageSendMessage,ThingsEvent, ScenarioResult,BroadcastResponse,MessageDeliveryBroadcastResponse)
from ..firebase.config_firebase import firebase_db, firebase_rdb
import json

admin_page = Blueprint('admin_page', __name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == 'ppAdmin' and password == 'pp2563':
        return username
    else:
        return False

@admin_page.route('/admin/announce', methods=['GET', 'POST'])
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
    
    return render_template('announce.html', typeText=type, userline=users)


@admin_page.route('/admin/Broadcast', methods=['GET', 'POST'])
@auth.login_required
def page_admin():
    select = ''
    users_rdb = firebase_rdb.child('users').get()
    select = request.args.get("getidname")
    print(f"log_select: {select}")
    if select:
        chat_rdb = firebase_rdb.child('users').child(select).get()
        test = chat_rdb.each()
        print(chat_rdb.val())
        for i in chat_rdb.val():
              print(i['events'])

    else:
        chat_rdb = []
    
    return render_template('admin.html' , userlist=users_rdb, chatlist=chat_rdb, select=select)