from flask import Flask, request, abort, render_template, url_for, Blueprint
from flask_httpauth import HTTPBasicAuth
from ..firebase.config_firebase import firebase_db, firebase_rdb
import json


exam_page = Blueprint('exam_page', __name__)
auth_exam = HTTPBasicAuth()

@auth_exam.verify_password
def verify_password(username, password):
    print("checking....")
    if username is None or password is None:
        return abort(403)
    if firebase_rdb.child('exam').child('user').child(username).get().val() is not None:
        print(username)
        return username
    else:
        print('False')
        return abort(403)

@exam_page.route('/exam')
@auth_exam.login_required
def exam():
    return render_template('exam.html')