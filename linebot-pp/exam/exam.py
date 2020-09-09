from flask import (
    Flask,
    request,
    abort,
    render_template,
    url_for,
    make_response,
    redirect,
    Blueprint,
    session,
    flash,
)
from ..firebase.config_firebase import firebase_db, firebase_rdb
from functools import wraps
import jwt
import json
import datetime
import time
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    jwt_refresh_token_required,
    create_refresh_token,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)


exam_page = Blueprint("exam_page", __name__)

'''
def verify_token(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        data = request.get_json()
        if data is not None:
            token = data["token"]
            # token = request.args.get('token') ///on get
            if not token:
                return render_template("login.html")
            try:
                data = jwt.decode(token, "pp-exam")
            except:
                return render_template("login.html")
            return f(*args, **kwargs)
        else:
            return render_template("login.html")

    return wrapped
'''

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


def exam():
    if request.args.get("token") is None:
        print("no data")
        return redirect(f"/exam/login")
    else:
        token = request.args.get("token")
        get_token = jwt.decode(token, "pp-exam")
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
            return redirect(f"/exam/profile?token={token}")
        else:
            return render_template("exam.html", user=user, token=get_token)



@exam_page.route("/exam", methods=["GET", "POST"])
@exam_page.route("/exam/<string:route>")
def exam_page(route=None):
    if route is "profile":
        return render_template("profile.html")
    elif route is "login":
        login()
    else:
        exam()

'''
@exam_page.route("/test")
@verify_token
def test_jwt():
    return render_template("profile.html")
'''