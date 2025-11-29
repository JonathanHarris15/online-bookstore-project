from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Order, OrderItem, Book
from app import db
from datetime import datetime

class OrderCreation(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()

        data = request.get_json()
        items_data = data.get('items')#this is a list [{"book_id": 1, ...}]

        if not items_data:
            return {'message': 'No items provided.'}, 400
        
        total_amount = 0
        new_order_items = []
        for item in items_data:
            book_id = item.get('book_id')
            action_type = item.get('type')

            book = Book.query.get(book_id)
            if not book:
                return {'message': f'Book with ID {book_id} not found.'}, 404
            
            if action_type == 'buy':
                price = book.buy_price
            elif action_type == 'rent':
                if not book.is_available:
                    return {'message': f'Book with ID {book_id} is not available for rent.'}, 400
                price = book.rent_price
                book.is_available = False
            else:
                return {'message': f"Invalid type {action_type} for Book ID {book_id}"}, 400
            
            total_amount += price

            order_item = OrderItem(
                book_id=book_id,
                type=action_type,
                item_price=price
            )
            new_order_items.append(order_item)
        
        new_order = Order(
            user_id=current_user_id,
            order_date=datetime.utcnow(),
            total_amount=total_amount,
            payment_status="Pending"
        )

        db.session.add(new_order)
        db.session.flush()#get the order ID but dont commit it to the database yet

        for item in new_order_items:
            item.order_id = new_order.id
            db.session.add(item)

        db.session.commit()

        return {
            "message": "Order placed successfully",
            "order_id": new_order.id,
            "total_amount": float(total_amount),
            "status": "Pending"
        }, 201
