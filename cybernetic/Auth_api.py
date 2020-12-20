import datetime
import hashlib
import random
from flask import request, make_response, jsonify
from flask_jwt_extended import create_access_token
from flask_mail import Message
from flask_restx import Namespace, Resource
from cybernetic import db, mail
from cybernetic.Models import User, UserCart, ResetPasswordToken

api = Namespace("auth", description="Auth related")


@api.route("/login/")
class Login(Resource):

  def post(self):
    post_data = request.get_json(force=True)
    password = post_data.get("password")
    sha_1 = hashlib.sha1()
    email = post_data.get("email")
    sha_1.update(password.encode())
    user = db.session.execute(
      f"SELECT * FROM user WHERE email = '{email}' AND password = '{sha_1.hexdigest()}'").first()
    if user:
      auth_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(days=1000, seconds=0))
      if auth_token:
        response_obj = {
          "success": True,
          "message": "Successfully logged in.",
          "auth_token": auth_token
        }
        return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "Incorrect username or password",
      }
      return make_response(jsonify(response_obj), 401)


@api.route("/register/")
class Register(Resource):

  def post(self):
    post_data = request.get_json(force=True)
    email_exist = User.query.filter_by(email=post_data.get("email")).first()
    user_exist = User.query.filter_by(email=post_data.get("username")).first()
    if not user_exist and not email_exist:
      user = User(
        email=post_data.get("email"),
        password=post_data.get("password"),
        username=post_data.get("username")
      )
      db.session.add(user)
      db.session.commit()
      cart = UserCart(user_id=user.id)
      db.session.add(cart)
      db.session.commit()
      auth_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(days=1000, seconds=0))
      response_obj = {
        "success": True,
        "message": "Successfully registered.",
        "auth_token": auth_token
      }
      return make_response(jsonify(response_obj), 201)
    else:
      response_obj = {
        "success": False,
        "message": "User already exists. Please Log in.",
      }
      return make_response(jsonify(response_obj), 202)


@api.route("/forget-password/")
class ForgetPasswordRequest(Resource):

  def post(self):
    post_data = request.get_json(force=True)
    email = post_data.get("email")
    user = User.query.filter_by(email=email).first()
    if user:
      while True:
        code = random.randint(100000, 999999)
        exist = ResetPasswordToken.query.filter_by(token=code).first()
        if exist is None:
          break
      token = ResetPasswordToken(token=code, user_id=user.id)
      db.session.add(token)
      db.session.commit()
      msg = Message(f"The code for resting your password is {code}",
                    sender="admin@idiotservice.net",
                    recipients=[email])
      mail.send(msg)
      response_obj = {
        "success": True,
        "message": "The email containing the 6 digit code for resetting your password has been sent to your email address.",
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "No user found with the email address provided",
      }
      return make_response(jsonify(response_obj), 404)


@api.route("/forget-password/new-password/")
class ForgetPasswordRequestNew(Resource):

  def post(self):
    post_data = request.get_json(force=True)
    user_id = post_data.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    if user:
      token = ResetPasswordToken.query.filter_by(token=post_data.get("code")).first()
      if token is not None:
        password = post_data.get("password")
        sha_1 = hashlib.sha1()
        sha_1.update(password.encode())
        user.password = sha_1.hexdigest()
        db.session.commit()
        response_obj = {
          "success": True,
          "message": f"{user.username} ({user.email}) password has been reset. New password is {post_data.get('password')}",
        }
        return response_obj
      else:
        response_obj = {
          "success": False,
          "message": "Invalid password reset code",
        }
        return make_response(jsonify(response_obj), 401)
    else:
      response_obj = {
        "success": False,
        "message": "No such user",
      }
      return make_response(jsonify(response_obj), 404)
