from flask import request
from flask_restful import Resource
from app.models import User
from app import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

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
    
class UserResource(Resource):
    @jwt_required()
    def get(self, username):
        user = User.query.filter_by(username=username).first_or_404()
        orders_out = []
        for order in getattr(user, 'orders', []):
            items = []
            for item in getattr(order, 'order_items', []):
                book = getattr(item, 'book', None)
                items.append({
                    'book_id': item.book_id,
                    'title': book.title if book else None,
                    'author': book.author if book else None,
                    'type': item.type,
                    'item_price': float(item.item_price)
                })

            orders_out.append({
                'id': order.id,
                'order_date': order.order_date.isoformat(),
                'total_amount': float(order.total_amount),
                'payment_status': order.payment_status,
                'items': items
            })

        return {
            "username": user.username,
            "email": user.email,
            "orders": orders_out
        }, 200

    @jwt_required()
    def patch(self, username):
        # only allow the owner (or a manager if you add that logic) to update
        user = User.query.filter_by(username=username).first_or_404()
        current_user_id = get_jwt_identity()
        # get_jwt_identity() is stored as string in your login; cast for comparison
        if str(user.id) != str(current_user_id):
            return {"message": "Permission denied"}, 403

        data = request.get_json() or {}
        current_password = data.get('current_password')
        if not current_password or not user.check_password(current_password):
            return {"message": "Current password is required and must be valid."}, 401

        new_email = data.get('email')
        new_password = data.get('new_password')

        if new_email:
            user.email = new_email
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        return {"message": "User updated successfully"}, 200