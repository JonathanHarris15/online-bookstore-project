from flask import request
from flask_restful import Resource
from app.models import User
from app import db
from flask_jwt_extended import create_access_token

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return {'message': 'Username, email, and password are required.'}, 400
        
        if User.query.filter_by (username=username).first():
            return {'message': 'Username already exists.'}, 400
        
        new_user = User(username=username, email=email)
        
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        return {'message': 'User registered successfully.'}, 201
    
class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            access_token = create_access_token(identity=str(user.id))
            return {'access_token': access_token}, 200
        
        return {'message': 'Invalid credentials.'}, 401