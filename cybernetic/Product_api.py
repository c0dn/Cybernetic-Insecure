import os
import uuid
from flask_restx import Namespace, Resource
from werkzeug.utils import secure_filename
from cybernetic.Models import Product
from cybernetic import db, pagination
from flask import request, make_response, jsonify, send_from_directory
from flask_jwt_extended import jwt_required
from cybernetic.schemas import ProductSchema

api = Namespace("products", description="Product related")
UPLOAD_FOLDER = "./cybernetic/uploads/"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def gen_unique_filename(filename):
    unique = str(uuid.uuid4())
    name = filename.split(".")[0]
    name += unique
    return f"{name}.{filename.split('.')[1]}"


@api.route("/uploads/")
class ImageUpload(Resource):

    @jwt_required
    def post(self):
        if "file" not in request.files:
            response_obj = {
                "success": False,
                "message": "no file part"
            }
            return make_response(jsonify(response_obj), 400)
        file = request.files["file"]
        if file.filename == "":
            response_obj = {
                "success": False,
                "message": "no file part"
            }
            return make_response(jsonify(response_obj), 400)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = gen_unique_filename(filename)
            file.save(os.path.abspath(UPLOAD_FOLDER + filename))
            response_obj = {
                "success": True,
                "data": {
                    "filename": filename
                }
            }
            return response_obj


@api.route("/uploads/<filename>")
class GetImage(Resource):

    def get(self, filename):
        return send_from_directory(os.path.abspath(UPLOAD_FOLDER), filename)


@api.route("/")
class Products(Resource):

    def get(self):
        product_schema = ProductSchema(many=True)
        products = pagination.paginate(Product, product_schema, True)
        response_obj = {
            "success": True,
            "data": {
                "products": products
            }
        }
        return response_obj

    @jwt_required
    def post(self):
        post_data = request.get_json(force=True)
        product = Product.query.filter_by(name=post_data.get("name")).first()
        if not product:
            product = Product(
                name=post_data.get("name"),
                retail_price=post_data.get("retail_price"),
                description=post_data.get("description"),
                stock=post_data.get("stock"),
                pic_filename=post_data.get("pic_filename")
            )
            db.session.add(product)
            db.session.commit()
            product_schema = ProductSchema()
            response_obj = {
                "success": True,
                "data": product_schema.dump(product)
            }
            return make_response(jsonify(response_obj), 201)
        else:
            response_obj = {
                "success": False,
                'message': "Product already exists.",
            }
            return make_response(jsonify(response_obj), 202)


@api.route("/<id>/")
@api.param("id", "Product identifier")
class ProductDetails(Resource):

    def get(self, id):
        product = Product.query.filter_by(id=id).first()
        if product is not None:
            product_schema = ProductSchema()
            response_obj = {
                "success": True,
                "data": product_schema.dump(product)
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such Product"
            }
            return make_response(jsonify(response_obj), 404)

    @jwt_required
    def put(self, id):
        product = Product.query.filter_by(id=id).first()
        if product is not None:
            post_data = request.get_json(force=True)
            for key in post_data:
                setattr(product, key.lower(), post_data.get(key.lower()))
            db.session.commit()
            product_schema = ProductSchema()
            response_obj = {
                "success": True,
                "data": product_schema.dump(product)
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such Product"
            }
            return make_response(jsonify(response_obj), 404)

    @jwt_required
    def delete(self, id):
        query = f"SELECT * FROM product WHERE id = '{id}' "
        product = db.session.execute(query).first()
        if product is not None:
            query = f"DELETE FROM product WHERE id = '{id}' "
            db.session.execute(query)
            db.session.commit()
            response_obj = {
                "success": True,
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such Product"
            }
            return make_response(jsonify(response_obj), 404)
