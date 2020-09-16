from flask import Flask,request,abort,render_template,url_for,make_response,redirect,Blueprint,session,flash 
from ..firebase.config_firebase import firebase_db, firebase_rdb
from functools import wraps
import jwt
import json
from datetime import datetime, date, time, timedelta
import time
import random


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
                        print(f"unit_exam: {examinations}")
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
                        if len(examinations)>1:    
                            get_unit = random.choice(examinations)
                            get_exam = random.choice(get_unit)
                        else:
                            examinations = json.loads(json.dumps(examinations))
                            exam_keys = list(examinations.keys())
                            get_unit = examinations[exam_keys[0]]
                            get_exam = random.choice(get_unit)
                        firebase_rdb.child('exam').child('user').child(get_token['user']).child('exam').child(count).set(get_exam)
                        firebase_rdb.child('exam').child('user').child(get_token['user']).child('examinations').child(get_exam['หน่วย']-1).child(get_exam['ข้อ']-1).remove()

                    return redirect(f"/exam?token={token}")
                except jwt.ExpiredSignature:
                    return redirect(f"/exam/login")
            except Exception as e:
                print(f"Error : {e}")
                print(f"Error with : {get_exam}")
                print(f"Exam from error : {examinations}")
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
                print(user)
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
                    return render_template("exam.html", user=user, header=header, choice=choice, permission=user['permission'], score=user['score'], token=get_token)
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
        print("no data")
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
                    print(f"from: {unit}")
                    exam = random.choice(unit)
                    print(f"random is :{exam}")
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
        print("no data")
        return redirect(f"/exam/login")   

