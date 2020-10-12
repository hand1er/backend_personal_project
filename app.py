from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
import hashlib
app = Flask(__name__)
@app.route('/')
def hello_flask():
    return "Hello world!"

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        userid = request.form.get('userid')
        username = request.form.get('username')
        password = request.form.get('password')
        re_password = request.form.get('re_password')

        if not (userid and username and password and re_password):
            return "모두 입력해주세요"
        elif password != re_password:
            return "비밀번호를 확인해주세요"
        else:
            return register_mongo(userid,username,password)

        return redirect('/')


@app.route('/mongo',methods=['POST'])
def register_mongo(userid,username,password):
    hasher = hashlib.sha512()
    hasher.update(password.encode('utf-8'))

    client = MongoClient('mongodb://localhost:27017/')
    db = client.user
    collection = db.userlist
    collection.insert({"userid":userid,"password":hasher.hexdigest(),"username":username})
    client.close()
    return "회원가입 완료"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)
