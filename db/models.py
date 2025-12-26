from flask_login import UserMixin

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    email = Column(String(120), unique=True)
    phone = Column(String(30), nullable=False, unique=True)
    password_hash = Column(String(256))
    cart_items = relationship('CartItem', backref='owner')
    orders = relationship('Order', backref='owner')
    reviews = relationship('Review', backref='author')

    def __str__(self):
        return f'{self.name}'

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    author = Column(String(120))
    cover = Column(String(500))
    year = Column(Integer)
    price = Column(Float(2))
    genre = Column(String(50))
    rating = Column(Float(1), default=False)
    description = Column(Text)
    in_carts = relationship('CartItem', backref='added_book')
    in_orders = relationship('OrderItem', backref='added_book')
    in_orders_tmp = relationship('OrderItemTmp', backref='added_book')
    reviews = relationship('Review', backref='book')

    def __str__(self):
        return f'Книга "{self.title.capitalize()}"'

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    amount = Column(Integer, nullable=False, default=1)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)#в пути, доставлено, готовится, заказ отменен
    address = Column(String(500), nullable=False)
    price = Column(Float(2), nullable=False)
    items_list = relationship('OrderItem', backref='order')

class OrderItemTmp(Base):
    __tablename__ = "order_items_tmp"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    book_dict = Column(PickleType, nullable=False)

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    amount = Column(Integer, nullable=False)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Integer)

