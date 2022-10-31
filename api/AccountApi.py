from flask_restful import Resource, request
import sys
sys.path.append('..')
import json
from collection.User import User
from flask_bcrypt import Bcrypt
import os
import jwt
import datetime
bcrypt = Bcrypt()

class AccountApi(Resource):
  # logout
  def get(self):
    authorization = request.headers.get('Authorization')
    try:
      jwt.decode(authorization, os.getenv('JWT_KEY'), algorithms=['HS256'])
    except jwt.exceptions.DecodeError as e:
      return { 'message': str(e) }, 400
    return { 'message': 'success' }
  # login
  def post(self):
    body = request.get_json()
    email = body.get('email')
    password = body.get('password')
    if not email: return { 'message': 'email required.' }, 400
    if not password: return { 'message': 'password required.' }, 400
    if len(password) < 6: return { 'message': 'password must be at least 6 characters.' }, 400

    user = json.loads(User.objects(email=email).only('password', 'uid').first().to_json())
    if not user: return { 'message': 'user not found.' }, 404
    hash_password = user.get('password')
    is_password_valid = bcrypt.check_password_hash(hash_password, password)
    if not is_password_valid: return { 'message': 'password is wrong.'}, 400
    uid = user.get('uid')
    jwt_exp = datetime.datetime.now()+ datetime.timedelta(days=7)
    jwt_token = jwt.encode({'uid': uid, 'exp': jwt_exp}, os.getenv('JWT_KEY'), algorithm="HS256")
    return { 'message': 'success', 'token': jwt_token}

class CheckLoginApi(Resource):
  def get(self):
    authorization = request.headers.get('Authorization')
    try:
      uid = jwt.decode(authorization, os.getenv('JWT_KEY'), algorithms=['HS256']).get('uid')
    except jwt.exceptions.DecodeError as e:
      return { 'message': str(e) }, 400
    return { 'message': 'success', 'uid': uid }