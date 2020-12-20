from flask_restx import Namespace, Resource
from cybernetic import db
from flask import request, abort
from flask_jwt_extended import jwt_optional, get_jwt_identity
from cybernetic.schemas import ProductSchema, UserSchema

api = Namespace("search", description="Search")


@api.route("/<model>/")
class Search(Resource):

  @jwt_optional
  def get(self, model: str):
    user = get_jwt_identity()
    schema = None
    if model.lower() == "product":
      schema = ProductSchema(many=True)
    elif model.lower() == "user":
      if user is None:
        return abort(401)
      schema = UserSchema(many=True)
    query = f"SELECT * FROM {model} WHERE "
    args_query = request.args
    if len(args_query) == 0:
      return abort(400)
    else:
      for key in args_query:
          query += f"{key} LIKE '%{args_query[key]}%' "
      results = db.session.execute(query).fetchall()
      response_obj = {
        "success": True,
        "data": {
          "results": schema.dump(results)
        }
      }
      return response_obj


