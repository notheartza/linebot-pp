from flask import Flask,request,abort,render_template,url_for,make_response,redirect,Blueprint,session,flash 
from ..firebase.config_firebase import firebase_db, firebase_rdb
from functools import wraps
from ..exsheet import client
from ..linebotEvent.linebot import clientgs
import jwt
import json
from datetime import datetime, date, time, timedelta
import time
import random
import linecache
import sys

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print (f'EXCEPTION IN ({filename}, LINE {lineno} "{line.strip()}"): {exc_obj}')



exam_page = Blueprint("exam_page", __name__)


@exam_page.route("/exam", methods=["GET", "POST"])
def exam():
    
    if request.args.get("token") is None:
        print("no data")
        return redirect(f"/exam/login")
    else:
        if request.method == "POST":
            try:
                header = request.form['header']
                if  'optradio' in request.form:
                    get_choice = request.form['optradio']
                else:
                    get_choice = ""

                #print(f"{header} : {get_choice}")
                token = request.args.get("token")
                try:
                    get_token = jwt.decode(token, 'pp-exam')
                    user = (
                        firebase_rdb.child("exam")
                        .child("user")
                        .child(get_token["user"])
                        .get()
                        .val()
                    )
                    exam = user['exam']
                    count = len(exam)
                    check_exam = exam[count-1]['เฉลย']
                    #print(f"{check_exam} : {get_choice}")
                    if check_exam == get_choice:
                        #print('ถูก')
                        firebase_rdb.child('exam').child('user').child(get_token['user']).update({ 'score' : user['score'] + 1 })
                    firebase_rdb.child('exam').child('user').child(get_token['user']).child('exam').child(count-1).update({"คำตอบ" : get_choice})
                    if count == 20:
                        firebase_rdb.child('exam').child('user').child(get_token['user']).update({'permission': False})
                    elif count % 5 > 0:
                        unit = exam[count-1]['หน่วย']
                        #print(f"unit: {unit}")
                        examinations = firebase_rdb.child('exam').child('user').child(get_token['user']).child('examinations').child(unit-1).get().val()
                        #print(f"unit_exam: {examinations}")
                        get_exam = random.choice(examinations)
                        while get_exam is None:
                            get_exam = random.choice(examinations)
                        #print(f"exam: {get_exam}")
                        #print(f"from is :  { get_exam['หน่วย']} > {get_exam['ข้อ']}")
                        firebase_rdb.child('exam').child('user').child(get_token['user']).child('exam').child(count).set(get_exam)
                        firebase_rdb.child('exam').child('user').child(get_token['user']).child('examinations').child(get_exam['หน่วย']-1).child(get_exam['ข้อ']-1).remove()
                    else:
                        unit = exam[count-1]['หน่วย']
                        firebase_rdb.child('exam').child('user').child(get_token['user']).child('examinations').child(unit-1).remove()
                        examinations = firebase_rdb.child('exam').child('user').child(get_token['user']).child('examinations').get().val() 
                        examinations = json.loads(json.dumps(examinations))
                        if len(examinations)>1:    
                            get_unit = random.choice(examinations)
                            get_exam = random.choice(get_unit)
                        else:
                            exam_keys = list(examinations)
                            print(exam_keys)
                            get_unit = examinations[exam_keys[0]]
                            get_exam = random.choice(get_unit)
                        firebase_rdb.child('exam').child('user').child(get_token['user']).child('exam').child(count).set(get_exam)
                        firebase_rdb.child('exam').child('user').child(get_token['user']).child('examinations').child(get_exam['หน่วย']-1).child(get_exam['ข้อ']-1).remove()

                    return redirect(f"/exam?token={token}")
                except jwt.ExpiredSignature:
                    return redirect(f"/exam/login")
            except Exception as e:
                print(f"Error : {e}")
                PrintException()
                return redirect(f"/exam?token={token}")

        else:
            token = request.args.get("token")
            try:
                get_token = jwt.decode(token, "pp-exam")
                user = (
                    firebase_rdb.child("exam")
                    .child("user")
                    .child(get_token["user"])
                    .get()
                    .val()
                )
                #print(user)
                if user['permission'] is False:
                    return render_template("exam.html", user=user, permission=user['permission'], score=user['score'], token=get_token)
                elif 'exam' not in user.keys():
                    return redirect(f"/exam/profile?token={token}")
                else:
                    exam = user['exam']
                    count = len(exam)
                    header = exam[len(exam)-1]['คำถาม']
                    choice = exam[len(exam)-1]['ตัวเลือก']
                    #print(choice)
                    random.shuffle(choice)
                    #print(choice)
                    return render_template("exam.html", user=user, header=header, choice=choice, permission=user['permission'], score=user['score'], number=count, token=get_token)
            except jwt.ExpiredSignature:
                return redirect(f"/exam/login")
 

@exam_page.route("/exam/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print("Post...")
        if None not in (request.form["username"], request.form["password"]):
            print("geting...")
            user = request.form["username"]
            password = request.form["password"]
            if firebase_rdb.child('exam').child('user').child(user).get().val() is not None:
                data = firebase_rdb.child('exam').child('user').child(user).get().val() 
                playload = {"user": user, 'exp': datetime.utcnow() + timedelta(hours=1)}
                token = jwt.encode(playload, "pp-exam", algorithm="HS256").decode("utf-8")
                extra_args = {"token": token}
                return redirect(f"/exam?token={token}")
                # return render_template('exam.html', user=user, **extra_args)
            else:
                return render_template("login.html")
        else:
            print("error")
            return render_template("login.html")
    else:
        print("error")
        return render_template("login.html")


@exam_page.route("/exam/profile", methods=["GET", "POST"])
def profile():
    if request.args.get("token") is not None:
        if request.method == "POST":
            token = request.args.get("token")
            return redirect(f"/exam/intro?token={token}")
        else:
            get_token = request.args.get("token")
            try:
                get_token = jwt.decode(get_token, "pp-exam")
                user = (
                firebase_rdb.child("exam")
                .child("user")
                .child(get_token["user"])
                .get()
                .val()
                )
                return render_template("profile.html", key=get_token["user"], user=user)
            except jwt.ExpiredSignature:
                return redirect(f"/exam/login")
    else:
        #print("no data")
        return redirect(f"/exam/login")


@exam_page.route('/exam/intro', methods=['GET', 'POST'])
def intro():
    random.seed(datetime.now())
    """
    if 'next' in request.form:
        print('next')
    elif 'back' in request.form:
        print('back')
        pass 
    elif 'submit' in request.form:
        print('submit')
        pass
    """
    if request.args.get("token") is not None:
        if request.method == "POST":
            token = request.args.get("token")
            try:
                get_token = jwt.decode(token, "pp-exam")
                examinations = firebase_rdb.child('exam').child('examinations').get().val()
                user = firebase_rdb.child('exam').child('user').child(get_token['user']).get().val()
                firebase_rdb.child('exam').child('user').child(get_token['user']).child('examinations').set(examinations)
                if 'exam' not in user.keys():
                    unit = random.choice(examinations)
                    #print(f"from: {unit}")
                    exam = random.choice(unit)
                    #print(f"random is :{exam}")
                    firebase_rdb.child('exam').child('user').child(get_token['user']).child('exam').child('0').set(exam)
                    firebase_rdb.child('exam').child('user').child(get_token['user']).child('examinations').child(exam['หน่วย']-1).child(exam['ข้อ']-1).remove()
                    return redirect(f"/exam?token={token}")
            except jwt.ExpiredSignature:
                return redirect(f"/exam/login")  
        else:
            token = request.args.get("token")
            try:
                get_token = jwt.decode(token, "pp-exam")
                user = (
                firebase_rdb.child("exam")
                .child("user")
                .child(get_token["user"])
                .get()
                .val()
                )
                if 'exam' not in user.keys():
                    get_exam = (
                    firebase_rdb.child("exam").child("user").child(get_token["user"]).get().val())
                    get_exam.get('exam')
                else:
                    return redirect(f"/exam?token={token}")
            except jwt.ExpiredSignature:
                return redirect(f"/exam/login")
            
            return render_template("intro.html", user=user, token=token)

    else:
        #print("no data")
        return redirect(f"/exam/login")   






@exam_page.route('/exam/score/<room>')
def scoreexam(room):
    users = firebase_rdb.child('exam').child('user').get().val()
    show = []
    for i in users:
        user = users[i]
        if user['ห้อง'] == f"ม.4/{room}":
            show.append(users[i])
        #print(f'USER: {show}')
    return render_template("score.html", score=show)


@exam_page.route("/homework/login", methods=["GET", "POST"])
def homework_login():
    if request.method == "POST":
        print("Post...")
        if None not in (request.form["username"], request.form["password"]):
            print("geting...")
            user = request.form["username"]
            password = request.form["password"]
            if firebase_rdb.child('exam').child('user').child(user).get().val() is not None:
                data = firebase_rdb.child('exam').child('user').child(user).get().val() 
                playload = {"user": user, 'exp': datetime.utcnow() + timedelta(hours=1)}
                token = jwt.encode(playload, "pp-exam", algorithm="HS256").decode("utf-8")
                extra_args = {"token": token}
                return redirect(f"/homework?token={token}")
                # return render_template('exam.html', user=user, **extra_args)
            else:
                return render_template("login.html")
        else:
            print("error")
            return render_template("login.html")
    else:
        print("error")
        return render_template("login.html")


@exam_page.route('/homework', methods=["GET", "POST"])
def homework():
    if request.args.get("token") is not None:
        token = request.args.get("token")
        try:
            get_token = jwt.decode(token, 'pp-exam')
            user = (
                firebase_rdb.child("exam")
                        .child("user")
                        .child(get_token["user"])
                        .get()
                        .val()
                    )
            room = user['ห้อง']
            number = user['password']
            stduent = clientgs(f'คะแนนนักเรียน {room}', client)
            print(f"Exam: {stduent}")
            return render_template("homework.html", user=user, token=token)
        except jwt.ExpiredSignature:
            return redirect(f"/homework/login")
        
    else:
        #print("no data")
        return redirect(f"/homework/login")

@exam_page.route("/homework/profile", methods=["GET", "POST"])
def homework_profile():
    if request.args.get("token") is not None:
        if request.method == "POST":
            token = request.args.get("token")
            return redirect(f"/homework?token={token}")
        else:
            get_token = request.args.get("token")
            try:
                get_token = jwt.decode(get_token, "pp-exam")
                user = (
                firebase_rdb.child("exam")
                .child("user")
                .child(get_token["user"])
                .get()
                .val()
                )
                return render_template("profile.html", key=get_token["user"], user=user)
            except jwt.ExpiredSignature:
                return redirect(f"/exam/login")
    else:
        #print("no data")
        return redirect(f"/exam/login")