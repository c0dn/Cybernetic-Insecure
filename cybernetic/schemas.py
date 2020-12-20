from cybernetic import ma
from cybernetic.Models import Order, OrderedProduct, UserCart, CartItem, Product, Card, User, Address, \
  ResetPasswordToken, ProductRating


class UserSchema(ma.SQLAlchemyAutoSchema):
  addresses = ma.List(ma.Nested("AddressSchema", exclude=("user",)))
  cards = ma.List(ma.Nested("CardSchema", exclude=("user",)))
  forget_tokens = ma.List(ma.Nested("ResetPasswordTokenSchema", exclude=("user",)))
  cart = ma.Nested("UserCartSchema", exclude=("user",))
  product_rating = ma.List(ma.Nested("ProductRatingSchema", exclude=("user", "product")))

  class Meta:
    model = User


class CardSchema(ma.SQLAlchemyAutoSchema):
  user = ma.Nested("UserSchema", exclude=("addresses", "cards", "cart", "product_rating"))

  class Meta:
    model = Card


class AddressSchema(ma.SQLAlchemyAutoSchema):
  user = ma.Nested("UserSchema", exclude=("addresses", "cards", "password", "cart", "product_rating"))

  class Meta:
    model = Address


class ResetPasswordTokenSchema(ma.SQLAlchemyAutoSchema):

  user = ma.Nested("UserSchema", exclude=("addresses", "cards", "password", "cart", "product_rating"))


  class Meta:
    model = ResetPasswordToken


class ProfileSchema(ma.SQLAlchemyAutoSchema):


  class Meta:
    model = User


class UserCartSchema(ma.SQLAlchemyAutoSchema):
  user = ma.Nested("UserSchema", exclude=("addresses", "cards", "cart", "product_rating"))
  items = ma.List(ma.Nested("CartItemSchema"))

  class Meta:
    model = UserCart


class ProductSchema(ma.SQLAlchemyAutoSchema):
  retail_price = ma.Float()

  class Meta:
    model = Product


class ProductRatingSchema(ma.SQLAlchemyAutoSchema):

  user = ma.Nested("UserSchema", exclude=("addresses", "cards", "password", "cart", "product_rating", "forget_tokens"))

  class Meta:
    model = ProductRating
    exclude = ("product",)


class CartItemSchema(ma.SQLAlchemyAutoSchema):
  product = ma.Nested("ProductSchema", exclude=("description", "pic_filename"))

  class Meta:
    model = CartItem


class OrderSchema(ma.SQLAlchemyAutoSchema):
  user = ma.Nested("UserSchema", exclude=("addresses", "cards", "cart", "product_rating"))
  items = ma.List(ma.Nested("OrderedProductSchema"))
  total_price = ma.Float()

  class Meta:
    model = Order


class OrderedProductSchema(ma.SQLAlchemyAutoSchema):
  product = ma.Nested("ProductSchema", exclude=("description", "pic_filename"))

  class Meta:
    model = OrderedProduct
