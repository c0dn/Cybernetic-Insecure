from flask import Flask, render_template
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_rest_paginate import Pagination

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
app.config["MAIL_SERVER"] = "smtp.mailgun.org"
app.config["MAIL_USERNAME"] = "postmaster@mail.idiotservice.net"
app.config["MAIL_PASSWORD"] = "75068b2f5a040da8e9d6a097f8432721-1b6eb03d-6cd1fdd3"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)


@app.route('/')
def cybernetic():
    return render_template('cybernetic.html')


app.config['PAGINATE_PAGE_SIZE'] = 20
app.config['PAGINATE_PAGE_PARAM'] = "page"
app.config['PAGINATE_SIZE_PARAM'] = "size"
app.config['PAGINATE_RESOURCE_LINKS_ENABLED'] = True
pagination = Pagination(app, db)

api = Api(app, version="1.0", title="Cybernetic", doc="", add_specs=False)


from cybernetic.User_api import api as users_api
from cybernetic.Auth_api import api as auth_api
from cybernetic.Card_api import api as cards_api
from cybernetic.Address_api import api as address_api
from cybernetic.Product_api import api as product_api
from cybernetic.Cart_api import api as cart_api
from cybernetic.Order_api import api as order_api
from cybernetic.Review_api import api as review_api
from cybernetic.Search_api import api as search_api

api.add_namespace(users_api)
api.add_namespace(auth_api)
api.add_namespace(cards_api)
api.add_namespace(address_api)
api.add_namespace(product_api)
api.add_namespace(cart_api)
api.add_namespace(order_api)
api.add_namespace(review_api)
api.add_namespace(search_api)
