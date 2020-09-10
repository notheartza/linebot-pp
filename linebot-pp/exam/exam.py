from flask import Flask,request,abort,render_template,url_for,make_response,redirect,Blueprint,session,flash 
from ..firebase.config_firebase import firebase_db, firebase_rdb
from functools import wraps
import jwt
import json
import datetime
import time
import random


exam_page = Blueprint("exam_page", __name__)


@exam_page.route("/exam", methods=["GET", "POST"])
def exam():
    if request.args.get("token") is None:
        print("no data")
        return redirect(f"/exam/login")
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
            get_users = json.dumps(user)
            get_users = json.loads(get_users)
            print(get_users)
            if get_users["exam"] is "":
                return redirect(f"/exam/profile?token={get_token}")
            else:
                return render_template("exam.html", user=user, token=get_token)
        except:
            return redirect(f"/exam/login")
 

@exam_page.route("/exam/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print("Post...")
        if None not in (request.form["username"], request.form["password"]):
            print("geting...")
            user = request.form["username"]
            password = request.form["password"]
            playload = {"user": user, "password": password}
            token = jwt.encode(playload, "pp-exam", algorithm="HS256").decode("utf-8")
            extra_args = {"token": token}
            # getuser = firebase_rdb.child('exam').child('user').child(user).get().val()
            return redirect(f"/exam?token={token}")
            # return render_template('exam.html', user=user, **extra_args)
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
            return render_template("profile.html")
    else:
        print("no data")
        return redirect(f"/exam/login")


@exam_page.route('/exam/intro', methods=['GET', 'POST'])
def intro():
    if request.args.get("token") is not None:
        if request.method == "POST":
            token = request.args.get("token")
            return redirect(f"/exam?token={token}")
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
                get_users = json.dumps(user)
                get_users = json.loads(get_users)
                print(get_users)
                if get_users["exam"] is "":
                    get_exam = (
                    firebase_rdb.child("exam").child("user").child(get_token["user"]).get().val())
                    get_exam.get('exam')
                else:
                    return render_template("exam.html", user=user, token=get_token)
            except:
                return redirect(f"/exam/login")
            
            return render_template("intro.html", intro="")

    else:
        print("no data")
        return redirect(f"/exam/login")   

