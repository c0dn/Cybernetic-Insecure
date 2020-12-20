from flask_restx import Namespace, Resource
from flask import make_response, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from cybernetic.Models import Order
from cybernetic.schemas import OrderSchema

api = Namespace("orders", description="Order related")


@api.route("/")
class Orders(Resource):

  @jwt_required
  def get(self):
    user_identifier = get_jwt_identity()
    orders = Order.query.filter_by(user_id=user_identifier).all()
    orders_schema = OrderSchema(many=True)
    response_obj = {
      "success": True,
      "data": {
        "orders": orders_schema.dump(orders)
      }
    }
    return response_obj


@api.route("/<int:id>/")
@api.param("id", "Order identifier")
class OrderDetail(Resource):

  @jwt_required
  def get(self, id):
    order = Order.query.filter_by(id=id).first()
    if order is not None:
      order_schema = OrderSchema()
      response_obj = {
        "success": True,
        "data": order_schema.dump(order)
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "No such Order"
      }
      return make_response(jsonify(response_obj), 404)
