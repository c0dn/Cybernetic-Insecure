import random
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource
from flask import request, make_response, jsonify
from cybernetic import db
from cybernetic.Models import Card
from datetime import datetime

from cybernetic.schemas import CardSchema

api = Namespace("cards", description="Cards related")


@api.route("/")
class Cards(Resource):

    @jwt_required
    def get(self):
        user_identifier = get_jwt_identity()
        cards = Card.query.filter_by(user_id=user_identifier).all()
        cards_schema = CardSchema(many=True)
        response_obj = {
            "success": True,
            "data": {
                "cards": cards_schema.dump(cards)
            }
        }
        return response_obj

    @jwt_required
    def post(self):
        user_identifier = get_jwt_identity()
        post_data = request.get_json(force=True)
        card = Card.query.filter_by(number=post_data.get("number")).first()
        if card is None:
            c_type = ""
            c_d = ["Credit", "Debit"]
            c_number = post_data.get("number")
            if c_number[0] == "4":
                c_type += "Visa "
            elif c_number[0] == "3":
                c_type += "AMEX "
            elif c_number[0] == "6":
                c_type += "Discover "
            else:
                c_type += "Mastercard "
            c_type += random.choice(c_d)
            c = Card(name=post_data.get("name"), type=c_type, cvc=post_data.get("cvc"),
                     expiry=datetime(int(post_data.get("expiry_year")), int(post_data.get("expiry_month")),
                                     1).timestamp(),
                     number=c_number, user_id=user_identifier)
            db.session.add(c)
            db.session.commit()
            card_schema = CardSchema()
            response_obj = {
                "success": True,
                "data": card_schema.dump(c)
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "Card already exist"
            }
            return make_response(jsonify(response_obj), 400)


@api.route("/<int:id>/")
@api.param("id", "Card identifier")
class CardDetails(Resource):

    @jwt_required
    def get(self, id):
        card = Card.query.filter_by(id=id).first()
        if card is not None:
            card_schema = CardSchema()
            response_obj = {
                "success": True,
                "data": card_schema.dump(card)
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such card"
            }
            return make_response(jsonify(response_obj), 404)

    @jwt_required
    def delete(self, id):
        card = Card.query.filter_by(id=id).first()
        if card is not None:
            db.session.delete(card)
            db.session.commit()
            response_obj = {
                "success": True,
            }
            return make_response(jsonify(response_obj), 200)
        else:
            response_obj = {
                "success": False,
                "message": "No such card"
            }
            return make_response(jsonify(response_obj), 404)
