from flask import Flask, request, abort, render_template, url_for, make_response, redirect, Blueprint
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from ..firebase.config_firebase import firebase_db, firebase_rdb
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as JWS
import json


exam_page = Blueprint('exam_page', __name__)
exam_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Exam')
multi_auth = MultiAuth(exam_auth, token_auth)
jws = JWS('exam_pp', expires_in=3600)


@exam_auth.verify_password
def verify_password(username, password):
    print("checking....")
    if firebase_rdb.child('exam').child('user').child(username).get().val() is not None:
        #res = make_response(redirect('/exam'))
        #res.set_cookie('username', value='Test', max_age=3600)
        return username


@token_auth.verify_token
def verify_token(token):
    try:
        data = jws.loads(token)
    except:  # noqa: E722
        return False
    if 'username' in data:
        return data['username']


@exam_page.route('/exam')
@multi_auth.login_required
def exam():
    id = multi_auth.current_user()
    user = firebase_rdb.child('exam').child('user').child(id).get().val()
    return render_template('exam.html', user=user)