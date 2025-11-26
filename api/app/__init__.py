from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager
from .config import DevelopmentConfig

db = SQLAlchemy() 
api = Api()
jwt = JWTManager()

def create_app(config_class=DevelopmentConfig):
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class) # Loads configuration from app/config.py

    #connect the database and encryption to the app
    db.init_app(app) # Links the SQLAlchemy object to the running app and its config
    jwt.init_app(app)
    

    #Resources
    from .resources.user_resources import UserRegister, UserLogin
    from .resources.book_resources import BookList
    from .resources.order_resources import OrderCreation
    from .resources.manager_resources import ManagerOrderList, ManagerOrderUpdate


    #User
    api.add_resource(UserRegister, '/auth/register')
    api.add_resource(UserLogin, '/auth/login')

    #Book
    api.add_resource(BookList, '/books')

    #Orders
    api.add_resource(OrderCreation, '/orders')

    #Manager
    api.add_resource(ManagerOrderList, '/manager/orders')
    api.add_resource(ManagerOrderUpdate, '/manager/orders/<int:order_id>')

    api.init_app(app)

    return app
