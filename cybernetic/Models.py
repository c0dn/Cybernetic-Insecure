import hashlib
from cybernetic import db


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(30), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(255), nullable=False)
  admin = db.Column(db.Boolean, nullable=False, default=False)
  addresses = db.relationship("Address", backref="user", lazy=True)
  forget_tokens = db.relationship("ResetPasswordToken", backref="user", lazy=True)
  cards = db.relationship("Card", backref="user", lazy=True)
  product_rating = db.relationship("ProductRating", backref="user", lazy=True)
  active = db.Column(db.Boolean, nullable=False, default=True)
  cart = db.relationship("UserCart", uselist=False, back_populates="user")

  def __init__(self, username, email, password, admin=False):
    self.username = username
    self.email = email
    sha_1 = hashlib.sha1()
    sha_1.update(password.encode())
    self.password = sha_1.hexdigest()
    self.admin = admin

  def __repr__(self):
    return f"User('{self.username}', '{self.email}')"


class Address(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), unique=False, nullable=False)
  contact = db.Column(db.String(30), unique=False, nullable=False)
  description = db.Column(db.String(20), unique=False, nullable=False)
  address_1 = db.Column(db.String(100), nullable=False)
  address_2 = db.Column(db.String(100), nullable=True)
  postal_code = db.Column(db.String(10), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  default = db.Column(db.Boolean, nullable=False, default=False)

  def __repr__(self):
    return f"Address('{self.description}', '{self.address_1} {self.address_2} {self.postal_code}')"


class Card(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  type = db.Column(db.String(20), nullable=False)
  name = db.Column(db.String(30), nullable=False)
  number = db.Column(db.String(20), nullable=False)
  cvc = db.Column(db.String(4), nullable=False)
  expiry = db.Column(db.String(100), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

  def __repr__(self):
    return f"Card('{self.name}', '{self.number}', '{self.cvc}', '{self.expiry}')"


class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  retail_price = db.Column(db.Integer, nullable=False)
  description = db.Column(db.Text(500), nullable=False)
  stock = db.Column(db.Integer, nullable=False)
  pic_filename = db.Column(db.String(255), nullable=False)
  cart_item = db.relationship("CartItem", backref="product", lazy=True)
  product_rating = db.relationship("ProductRating", backref="product", lazy=True)
  ordered_product = db.relationship("OrderedProduct", backref="product", lazy=True)

  def __repr__(self):
    return f"Product('{self.name}', '{self.retail_price}', '{self.stock}')"


class UserCart(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  user = db.relationship("User", back_populates="cart")
  items = db.relationship("CartItem", backref="cart", lazy=True)

  def __repr__(self):
    return f"UserCart('{self.id}','{self.total_price}','{self.user_id}'')"


class CartItem(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  cart_id = db.Column(db.Integer, db.ForeignKey("user_cart.id"), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
  quantity = db.Column(db.Integer, nullable=False)

  def __repr__(self):
    return f"CartItem('{self.id}', '{self.cart_id}','{self.product_id}','{self.quantity}')"


class Order(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  order_date = db.Column(db.String(100), nullable=False)
  total_price = db.Column(db.DECIMAL, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  items = db.relationship("OrderedProduct", backref="order", lazy=True)
  tracking_no = db.Column(db.String(30), nullable=True, default=None)

  def __repr__(self):
    return f"Order('{self.id}', '{self.order_date}','{self.total_price}','{self.user_id}'')"


class OrderedProduct(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
  quantity = db.Column(db.Integer, nullable=False)

  def __repr__(self):
    return f"Ordered('{self.id}', '{self.order_id}','{self.product_id}','{self.quantity}')"


class ResetPasswordToken(db.Model):
  token = db.Column(db.String(300), primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

  def __repr__(self):
    return f"ResetPasswordLInk('{self.token}','{self.user_id}')"


class ProductRating(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  rating = db.Column(db.Integer, nullable=False)
  deleted = db.Column(db.Boolean, nullable=False, default=False)
  comments = db.Column(db.Text(500), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

  def __repr__(self):
    return f"ProductRating('{self.id}','{self.rating}, {self.product_id}')"
