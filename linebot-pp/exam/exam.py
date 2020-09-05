from flask import Flask, request, abort, render_template, url_for, make_response, Blueprint
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
    if username == 'admin' and password == '1234':
        res = make_response()
        res.set_cookie('foo', 'bar', max_age=3600)
        resp.headers['location'] = url_for('exam_page.exam') 
        return username, res


@token_auth.verify_token
def verify_token(token):
    try:
        data = jws.loads(token)
    except:  # noqa: E722
        return False
    if 'username' in data:
        return data['username']


"""
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
"""
@exam_page.route('/exam')
@multi_auth.login_required
def exam():
    return render_template('exam.html')