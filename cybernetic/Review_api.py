from flask_restx import Namespace, Resource
from flask import request, make_response, jsonify
from cybernetic import db
from cybernetic.Models import ProductRating, Product
from flask_jwt_extended import jwt_required
from cybernetic.schemas import ProductRatingSchema

api = Namespace("reviews", description="Reviews related")

@api.route("/<int:id>/")
@api.param("id", "Review identifier")
class Reviews(Resource):

  @jwt_required
  def put(self, id):
    review = ProductRating.query.filter_by(id=id).first()
    if review is not None:
      post_data = request.get_json(force=True)
      for key in post_data:
        setattr(review, key.lower(), post_data.get(key.lower()))
      db.session.commit()
      product_reviews_schema = ProductRatingSchema()
      response_obj = {
        "success": True,
        "data": product_reviews_schema.dump(review)
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "No such Review"
      }
      return make_response(jsonify(response_obj), 404)

  @jwt_required
  def delete(self, id):
    review = ProductRating.query.filter_by(id=id).first()
    if review is not None:
      db.session.delete(review)
      db.session.commit()
      response_obj = {
        "success": True,
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "No such Review"
      }
      return make_response(jsonify(response_obj), 404)

@api.route("/product/<int:id>/")
@api.param("id", "Product identifier")
class ProductReviews(Resource):

  @jwt_required
  def get(self, id):
    product = Product.query.filter_by(id=id).first()
    if product is not None:
      reviews = ProductRating.query.filter_by(product_id=id).all()
      product_reviews_schema = ProductRatingSchema(many=True)
      response_obj = {
        "success": True,
        "data":{
          "reviews": product_reviews_schema.dump(reviews)
        }
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "No such Product"
      }
      return make_response(jsonify(response_obj), 404)

  @jwt_required
  def post(self, id):
    product = Product.query.filter_by(id=id).first()
    if product is not None:
      post_data = request.get_json(force=True)
      review = ProductRating(
        rating= post_data.get("rating"),
        comments= post_data.get("comments"),
        product_id= id,
        user_id=post_data.get("user_id"),
      )
      db.session.add(review)
      db.session.commit()
      product_reviews_schema = ProductRatingSchema()
      response_obj = {
        "success": True,
        "data": product_reviews_schema.dump(review)
      }
      return response_obj
    else:
      response_obj = {
        "success": False,
        "message": "No such Product"
      }
      return make_response(jsonify(response_obj), 404)