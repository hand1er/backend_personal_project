# -*- coding:utf-8 -*-

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import Flask, request
from flask_restplus import Resource, Api, reqparse, fields
from pymongo import MongoClient
import hashlib
from bson.json_util import dumps, loads

app = Flask(__name__)

#--------------------------------------------
# 사용자 관리를 위한 API 정의
#--------------------------------------------

api = Api(app, version='1.0', title='User API', description='사용자 관리 REST API 문서')
ns = api.namespace('user',description='사용자 API 목록')
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

model_users = api.model('users',{
    'user_id': fields.String(required=True, description='사용자 ID', help='사용자 ID는 필수'),
    'name' : fields.String(required=False, description='사용자 이름', help='사용자 이름은 필수'),
    'password' : fields.String(required=True, description='비밀번호', help='비밀번호는 필수'),
})

@ns.route('/')
class UserResource(Resource):

    def get(self, user_id=None):
        """
            Get a user resource or list users.
            GET/HEAD /user
            GET/HEAD /users/{user_id}
        """
        if user_id is not None:
            return self.get_user_mongo(user_id)
        return self.list_users_mongo()

    def get_user_mongo(self, user_id):
        """
            Get a user resource.
            GET/HEAD /v3/users/{user_id}
        """
        #** MONGO_DB_HOST **#
        client = MongoClient('mongodb://localhost:27017/')
        db = client.user
        collection = db.userlist
        users = collection.find({"user_id":user_id},{"_id":0,"user_id":1,"name":1})
        json_data=loads(dumps(users, ensure_ascii=False))
        client.close()
        return json_data

    def list_users_mongo(self):
        """
            List users.
            GET/HEAD /v3/users
        """
        #** MONGO_DB_PATH **#
        client = MongoClient('mongodb://localhost:27017/')
        db = client.user
        collection = db.userlist
        users = collection.find({},{"_id":0,"user_id":1,"name":1})
        json_data=loads(dumps(users, ensure_ascii=False))
        client.close()
        if json_data:
            return json_data
        else:
            return {'result': "등록된 사용자가 없습니다."}

    @ns.expect(model_users)
    def post(self):
        """
            Create a user.
            POST /users
        """
        try:
            body = request.get_json()
            user_id = body['user_id']
            password = body['password']
            name = body['name']
            message = self.create_user_mongo(user_id,name,password)
        except KeyError:
            return {'result': 'ERROR_PARAMETER'},400

        result = {'result': message, 'user_id':user_id, 'name':name}
        return result, 200

    def patch(self, user_id):
        """
            Update a user.
            PATCH /users/{user_id}
        """
        try:
            body = request.get_json()
            user_id = user_id
            password = body['password']
            name = body['name']
            message = self.edit_user_mongo(user_id,name,password)
        except KeyError:
            return {'result': 'ERROR_PARAMETER'},400

        if message:
            return {'result' : '정상적으로 변경되었습니다.', 'user_id':user_id, 'name':name},200
        else:
            return {'result' : 'ID나 비밀번호를 다시 확인해주세요.'},401

    def create_user_mongo(self, user_id, name, password):
        hasher = hashlib.sha512()
        hasher.update(password.encode('utf-8'))
        #** MONGO_DB_PATH **#
        client = MongoClient('mongodb://localhost:27017/')
        db = client.user
        collection = db.userlist

        if self.get_user_mongo(user_id):
            client.close()
            return "이미 가입된 ID입니다"

        collection.insert({'user_id':user_id,'password':hasher.hexdigest(),'name':name})
        client.close()
        return "회원가입 완료"

    def edit_user_mongo(self, user_id, name, password):
        hasher = hashlib.sha512()
        hasher.update(password.encode('utf-8'))
        #** MONGO_DB_PATH **#
        client = MongoClient('mongodb://localhost:27017/')
        db = client.user
        collection = db.userlist
        #users = collection.find({"user_id":user_id,"password":hasher.hexdigest()})
        users = collection.update({"user_id":user_id,"password":hasher.hexdigest()},{"$set":{"name":name}})
        json_data=loads(dumps(users, ensure_ascii=False))
        client.close()
    
        if json_data['nModified'] :
            return True
        else:
            return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)