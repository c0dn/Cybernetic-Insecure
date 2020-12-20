from datetime import datetime
from flask_restx import Namespace, Resource
from flask import request, make_response, jsonify
from cybernetic import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from cybernetic.Models import CartItem, UserCart, Order, OrderedProduct
from cybernetic.schemas import UserCartSchema, CartItemSchema, OrderSchema

api = Namespace("cart", description="Cart related")


@api.route("/<int:id>/")
@api.param("id", "Cart identifier")
class Cart(Resource):

    @jwt_required
    def get(self, id):
        cart = UserCart.query.filter_by(id=id).first()
        if cart is not None:
            cart_schema = UserCartSchema()
            response_obj = {
                "success": True,
                "data": cart_schema.dump(cart)
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such user cart"
            }
            return make_response(jsonify(response_obj), 404)

    @jwt_required
    def post(self, id):
        cart = UserCart.query.filter_by(id=id).first()
        if cart is not None:
            post_data = request.get_json(force=True)
            cart_item = CartItem.query.filter_by(product_id=post_data.get("product_id"), cart_id=id).first()
            if cart_item is None:
                cart_item = CartItem(
                    cart_id=id,
                    product_id=post_data.get("product_id"),
                    quantity=post_data.get("quantity")
                )
                db.session.add(cart_item)
            else:
                cart_item.quantity += int(post_data.get("quantity"))
            db.session.commit()
            cart_item_schema = CartItemSchema()
            response_obj = {
                "success": True,
                "data": cart_item_schema.dump(cart_item)
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such user cart"
            }
            return make_response(jsonify(response_obj), 404)


@api.route("/<int:id>/checkout/")
@api.param("id", "Cart identifier")
class CartCheckout(Resource):

    @jwt_required
    def post(self, id):
        cart = UserCart.query.filter_by(id=id).first()
        if cart is not None:
            user_id = get_jwt_identity()
            items = cart.items
            total = 0
            for item in items:
                total += item.quantity * item.product.retail_price
            order = Order(
                order_date=int(datetime.now().timestamp() * 1000),
                total_price=total,
                user_id=user_id
            )
            db.session.add(order)
            db.session.commit()
            for item in items:
                ordered = OrderedProduct(
                    order_id=order.id,
                    product_id=item.product.id,
                    quantity=item.quantity
                )
                db.session.delete(item)
                db.session.add(ordered)
            db.session.commit()
            order_schema = OrderSchema()
            response_obj = {
                "success": True,
                "data": order_schema.dump(order)
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such user cart"
            }
            return make_response(jsonify(response_obj), 404)


@api.route("/items/<int:id>")
@api.param("id", "Cart Item identifier")
class CartItems(Resource):

    @jwt_required
    def put(self, id):
        post_data = request.get_json(force=True)
        cart_item = CartItem.query.filter_by(id=id).first()
        if cart_item is not None:
            for key in post_data:
                setattr(cart_item, key.lower(), post_data.get(key.lower()))
            db.session.commit()
            cart_item_schema = CartItemSchema()
            response_obj = {
                "success": True,
                "data": cart_item_schema.dump(cart_item)
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
        cart_item = CartItem.query.filter_by(id=id).first()
        if cart_item is not None:
            db.session.delete(cart_item)
            db.session.commit()
            response_obj = {
                "success": True
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "Cart Item not found"
            }
            return make_response(jsonify(response_obj), 404)
