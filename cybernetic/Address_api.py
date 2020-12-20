from flask_restx import Namespace, Resource
from flask import request, make_response, jsonify
from cybernetic import db
from cybernetic.Models import Address
from flask_jwt_extended import get_jwt_identity, jwt_required
from cybernetic.schemas import AddressSchema
from marshmallow import ValidationError

api = Namespace("address", description="Addresses related")


@api.route("/")
class Addresses(Resource):

  @jwt_required
  def get(self):
    user_identifier = get_jwt_identity()
    addresses = Address.query.filter_by(user_id=user_identifier).all()
    addresses_schema = AddressSchema(many=True)
    response_obj = {
      "success": True,
      "data": {
        "addresses": addresses_schema.dump(addresses)
      }
    }
    return response_obj

  @jwt_required
  def post(self):
    user_identifier = get_jwt_identity()
    addresses_schema = AddressSchema()
    post_data = request.get_json(force=True)
    try:
      post_data = addresses_schema.load(post_data)
    except ValidationError as e:
      return {"success": False, "error": str(e)}
    address = Address.query.filter_by(description=post_data.get("description"), user_id=user_identifier).first()
    if address is None:
      try:
        address_2 = post_data.get("address_2")
      except KeyError:
        address_2 = None
      temp = Address.query.filter_by(user_id=user_identifier).all()
      if not temp:
        default = True
      else:
        default = False
      a = Address(description=post_data.get("description"),
                  contact=post_data.get("contact"),
                  name=post_data.get("name"),
                  address_1=post_data.get("address_1"),
                  address_2=address_2,
                  postal_code=post_data.get("postal_code"), user_id=user_identifier, default=default)
      db.session.add(a)
      db.session.commit()
      addresses_schema = AddressSchema()
      response_obj = {
        "success": True,
        "data": addresses_schema.dump(a)
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "Address already exist"
      }
      return make_response(jsonify(response_obj), 400)


@api.route("/<int:id>/")
@api.param("id", "Address identifier")
class AddressDetails(Resource):

  @jwt_required
  def get(self, id):
    address = Address.query.filter_by(id=id).first()
    if address is not None:
      addresses_schema = AddressSchema()
      response_obj = {
        "success": True,
        "data": addresses_schema.dump(address)
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "No such Address saved"
      }
      return make_response(jsonify(response_obj), 404)

  @jwt_required
  def put(self, id):
    address = Address.query.filter_by(id=id).first()
    if address is not None:
      post_data = request.get_json(force=True)
      for key in post_data:
        setattr(address, key.lower(), post_data.get(key.lower()))
      db.session.commit()
      addresses_schema = AddressSchema()
      response_obj = {
        "success": True,
        "data": addresses_schema.dump(address)
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "No such Address saved"
      }
      return make_response(jsonify(response_obj), 404)

  @jwt_required
  def delete(self, id):
    address = Address.query.filter_by(id=id).first()
    if address is not None:
      db.session.delete(address)
      db.session.commit()
      response_obj = {
        "success": True,
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "No such Address saved"
      }
      return make_response(jsonify(response_obj), 404)
