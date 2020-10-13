# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import requests
import hashlib

app = Flask(__name__)
@app.route('/')
def hello_flask():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    elif request.method == 'POST':
        userid = request.form.get('userid')
        username = request.form.get('username')
        password = request.form.get('password')
        re_password = request.form.get('re_password')

        if not (userid and username and password and re_password):
            return "모두 입력해주세요"
        elif password != re_password:
            return "비밀번호를 확인해주세요"
        else:
            #** USER API PATH **#
            url = 'http://0.0.0.0:5000/user/users'
            datas = {'userid':userid,'password':password,'username':username}
            res = requests.post(url, data=datas)
            return res.text

        return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='4999', debug=True)
