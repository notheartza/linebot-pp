from flask import Flask, request, abort, render_template, url_for, make_response, redirect, Blueprint, session, flash
from ..firebase.config_firebase import firebase_db, firebase_rdb
from functools import wraps
import jwt
import json
import datetime
import time


exam_page = Blueprint('exam_page', __name__)


@exam_page.route('/exam', methods=['GET', 'POST'], strict_slashes=False)
@exam_page.route('/exam/<string:route>', methods=['GET', 'POST'], strict_slashes=False)
def exam(route=None):
    if request.args.get('token') is None:
        print('no data')
        if request.method == "POST":
            print('Post...')
            if None not in (request.form['username'], request.form['password']):
                print('geting...')
                user = request.form['username'] 
                password = request.form['password']
                playload = {'user': user, 'password': password}
                token =jwt.encode(playload, 'secret', algorithm='HS256').decode('utf-8')
                extra_args = {'token': token}
                #getuser = firebase_rdb.child('exam').child('user').child(user).get().val()
                return redirect(f"/exam?token={token}")
                #return render_template('exam.html', user=user, **extra_args)
            else:
                print('error')
                return render_template('login.html')
        else:
            print('error')
            return render_template('login.html')
    else:  
        print(route)
        if route is None:
            token = request.args.get('token')
            get_token = jwt.decode(token, 'secret')
            user = firebase_rdb.child('exam').child('user').child(get_token['user']).get().val()
            get_users = json.dumps(user)
            get_users = json.loads(get_users)
            print(get_users)

            if get_users['exam'] is "":
                return redirect(f"/exam/profile?token={token}")
            else:
                return render_template('exam.html', user=user, token=get_token)
        elif route is "profile":
            return render_template('profile.html')
        """
        try:
            get_token = jwt.decode(token, 'secret', algorithms='HS256')
            user = firebase_rdb.child('exam').child('user').child(get_token['user']).get().val()
            if get_users['exam'] is "":
                return redirect(f"/exam/profile?token={token}")
            else:
                return render_template('exam.html', user=user, token=get_token)
        except Exception as e:
            print(f"error: {e}")
            return render_template('login.html')
            """