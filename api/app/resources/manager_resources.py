from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Order, Managers
from app import db

class ManagerOrderList(Resource):
    @jwt_required()
    def get(self):
        # Auth Check
        current_user_id = get_jwt_identity()
        manager_entry = Managers.query.filter_by(user_id=current_user_id).first()
        
        if not manager_entry:
            return {"message": "Authorization failed: Manager privileges required"}, 403
        
        orders = Order.query.all()

        output = []
        for order in orders:
            output.append({
                "id": order.id,
                "user_id": order.user_id,
                "total_amount": float(order.total_amount),
                "payment_status": order.payment_status,
                "order_date": order.order_date.isoformat()
            })

        return output, 200
    
class ManagerOrderUpdate(Resource):
    @jwt_required()
    def patch(self, order_id):
        # Auth Check
        current_user_id = get_jwt_identity()
        manager_entry = Managers.query.filter_by(user_id=current_user_id).first()
        
        if not manager_entry:
            return {"message": "Authorization failed: Manager privileges required"}, 403

        # Get Data
        data = request.get_json()
        new_status = data.get('payment_status')

        if not new_status:
            return {"message": "Missing 'payment_status' field"}, 400

        # Update
        order = Order.query.get(order_id)
        if not order:
            return {"message": "Order not found"}, 404

        order.payment_status = new_status
        db.session.commit()

        return {"message": f"Order {order_id} status updated to '{new_status}'"}, 200