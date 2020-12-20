from flask_restx import Namespace, Resource
from flask import make_response, jsonify, request
from cybernetic.Models import User
from cybernetic import db, app
from flask_jwt_extended import get_jwt_identity, jwt_required
import hashlib
from cybernetic.schemas import UserSchema

api = Namespace("users", description="Orders related")


@api.route("/")
class Users(Resource):

  @jwt_required
  def get(self):
    users = User.query.filter_by(admin=False).all()
    users_schema = UserSchema(many=True)
    response_obj = {
      "success": True,
      "data": {
        "users": users_schema.dump(users)
      }
    }
    return response_obj


@api.route("/<int:id>/")
@api.param("id", "User identifier")
class UserDetails(Resource):

  def delete(self, id):
    user = User.query.filter_by(id=id, active=True).first()
    if user is not None:
      user.active = False
      db.session.commit()
      response_obj = {
        "success": True,
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "No such User/User already deactivated."
      }
      return make_response(jsonify(response_obj), 404)


@api.route("/me/")
class Me(Resource):

  @jwt_required
  def get(self):
    user_identifier = get_jwt_identity()
    user = User.query.filter_by(id=user_identifier).first()
    user_schema = UserSchema()
    response_obj = {
      "success": True,
      "data": user_schema.dump(user)
    }
    return response_obj

  @jwt_required
  def put(self):
    post_data = request.get_json(force=True)
    user_identifier = get_jwt_identity()
    user = User.query.filter_by(id=user_identifier).first()
    for key in post_data:
      if key.lower() != "password":
        setattr(user, key.lower(), post_data.get(key.lower()))
      else:
        password = post_data.get("password")
        sha_1 = hashlib.sha1()
        email = post_data.get("email")
        sha_1.update(password.encode())
        user.password = sha_1.hexdigest()
    db.session.commit()
    user_schema = UserSchema()
    response_obj = {
      "success": True,
      "data": user_schema.dump(user)
    }
    return response_obj
