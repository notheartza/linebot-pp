from flask import Flask, request, abort, render_template, url_for, make_response, redirect, Blueprint, session, flash
from ..firebase.config_firebase import firebase_db, firebase_rdb
from functools import wraps
import jwt
import json


exam_page = Blueprint('exam_page', __name__)


@exam_page.route('/exam', methods=['GET', 'POST'])
def exam():
    if request.form.get('token') is None:
        if None not in (request.form['username'], request.form['password']):
            user = request.form['username'] 
            password = request.form['password']
            token =jwt.encode({'user': user, 'password': password}, 'secret', algorithm='HS256')
            redirect(url_for(f'/exam?token={token}'))
        else:
            return render_template('login.html')
    else:  
        #user = firebase_rdb.child('exam').child('user').child(id).get().val()
        return render_template('exam.html', user=user)