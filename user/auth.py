# -*- coding:utf-8 -*-

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import Flask, request
from flask_restplus import Resource, Api, reqparse, fields
from pymongo import MongoClient
import hashlib
import jwt
from bson.json_util import dumps, loads
from datetime import datetime, timedelta

app = Flask(__name__)

#--------------------------------------------
# 인증 관리를 위한 API 정의
#--------------------------------------------

api = Api(app, version='1.0', title='Auth API', description='인증 관리 REST API 문서')
ns = api.namespace('auth',description='인증 API 목록')
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

model_users = api.model('users',{
    'user_id': fields.String(required=True, description='사용자 ID', help='사용자 ID는 필수'),
    'password' : fields.String(required=True, description='비밀번호', help='비밀번호는 필수'),
})

@ns.route('/')
class AuthResource(Resource):

    @ns.expect(model_users)
    def post(self):
        """
            Authenticate user.

            HEAD/POST /auth
        """
        try:
            body = request.get_json()
            user_id = body['user_id']
            password = body['password']
            auth_result = self.authenticate_mongo(user_id,password)
        except KeyError:
            return {'result': 'ERROR_PARAMETER'},400

        if auth_result:
            payload = {
                "user_id" : user_id,
                "exp" : datetime.utcnow() + timedelta(seconds = 60)
            }
            token = jwt.encode(payload, 'abc', algorithm="HS256")
            return {"access_token":token.decode('UTF-8')}, 200
        else:
            return {'result': 'Authentication Failed'},401

    def authenticate_mongo(self, user_id, password):
        hasher = hashlib.sha512()
        hasher.update(password.encode('utf-8'))
        #** MONGO_DB_HOST **#
        client = MongoClient('mongodb://localhost:27017/')
        db = client.user
        collection = db.userlist
        users = collection.find({"user_id":user_id,"password":hasher.hexdigest()},{"_id":0,"user_id":1,"name":1})
        json_data=loads(dumps(users, ensure_ascii=False))
        client.close()

        return json_data

@ns.route('/tokens')
class AuthResource(Resource):

    def get(self):
        """
            Validate a token.

            HEAD/GET /auth/tokens
        """
        try:
            token_id = request.headers.get('X-Subject-Token')
        except KeyError:
            return {'result': 'ERROR_PARAMETER'},400

        try:
            token = jwt.decode(token_id, 'abc', algorithm='HS256')

        except jwt.DecodeError:
            return {'result': 'Invalid'},401
        except jwt.ExpiredSignatureError:
            return {'result': 'Expired_token'},400        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)