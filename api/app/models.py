from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)

    buy_price = db.Column(db.Numeric(10,2), nullable=False)
    rent_price = db.Column(db.Numeric(10,2), nullable=False)

    is_available = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
    
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Numeric(10,2), nullable=False)
    payment_status = db.Column(db.String(50), nullable=False)

    #create a relationship to User
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f'<Order {self.id} by User {self.user_id}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'buy' or 'rent'
    item_price = db.Column(db.Numeric(10,2), nullable=False)
    rent_due_date = db.Column(db.DateTime, nullable=True)  # Only needed for rentals

    #create relationships
    order = db.relationship('Order', backref=db.backref('order_items', lazy=True))
    book = db.relationship('Book', backref=db.backref('order_items', lazy=True))

    def __repr__(self):
        return f'<OrderItem {self.id} for Order {self.order_id}>'

class Managers(db.Model):
    __tablename__ = 'managers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user_name = db.Column(db.String(80), nullable=False)

    #create a relationship to User
    user = db.relationship('User', backref=db.backref('manager', uselist=False))

    def __repr__(self):
        return f'<Manager {self.user_name} (User ID: {self.user_id})>'