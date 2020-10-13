# -*- coding:utf-8 -*-

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import Flask
from flask_restplus import Resource, Api, reqparse
from pymongo import MongoClient
import hashlib

app = Flask(__name__)
api = Api(app, version='1.0', title='User API', description='사용자 관리 REST API 문서')
ns = api.namespace('user',description='사용자 API 목록')
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

#--------------------------------------------
# 사용자 관리를 위한 API 정의
#--------------------------------------------
user_parser = ns.parser()
user_parser.add_argument('userid', required=True, help='사용자 ID')
user_parser.add_argument('password', required=True, help='패스워드')
user_parser.add_argument('username', required=True, help='사용자 이름')

@ns.route('/users')
@ns.expect(user_parser)
class User(Resource):
    def get(self):
        """
            List User
        """

    def post(self):
        """
            Create User
        """
        args = user_parser.parse_args()

        try:
            userid = args['userid']
            password = args['password']
            username = args['username']
            message = create_user_mongo(userid,username,password)
        except KeyError:
            return {'result': 'ERROR_PARAMETER'}, 500

        result = {'result': message, 'userid':userid, 'username':username}
        return result, 200
    
def create_user_mongo(userid,username,password):
    hasher = hashlib.sha512()
    hasher.update(password.encode('utf-8'))
    #** MONGO_DB_PATH **#
    client = MongoClient('mongodb://localhost:27017/')
    db = client.user
    collection = db.userlist

    if collection.find_one({"userid":userid}):
        client.close()
        return "이미 가입된 ID입니다"

    collection.insert({'userid':userid,'password':hasher.hexdigest(),'username':username})
    client.close()
    return "회원가입 완료"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)