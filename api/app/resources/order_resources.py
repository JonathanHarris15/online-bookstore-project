from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Order, OrderItem, Book, User
from app import db
from datetime import datetime
import os
import requests
import json
import threading
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# Server-side SendGrid configuration (read from server environment)
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL')


def _send_email_sendgrid_server(to_email, subject, html_content, plain_text=None, from_email=None):
    if not SENDGRID_API_KEY:
        raise RuntimeError("SENDGRID_API_KEY not configured on server")

    # Determine the from address: prefer explicit arg, then env var, else raise to avoid using unverified default
    sender = from_email or SENDGRID_FROM_EMAIL
    if not sender:
        raise RuntimeError("No sender email configured. Set SENDGRID_FROM_EMAIL in the environment to a verified sender.")

    payload = {
        "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
        "from": {"email": sender},
        "content": []
    }
    if plain_text:
        payload["content"].append({"type": "text/plain", "value": plain_text})
    payload["content"].append({"type": "text/html", "value": html_content})

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    # Perform the request and capture any error details for easier debugging (SendGrid returns JSON error reasons)
    try:
        resp = requests.post(SENDGRID_URL, headers=headers, data=json.dumps(payload), timeout=10)
        if resp.status_code >= 400:
            # Log response body for debugging before raising
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            print(f"SendGrid API error: status={resp.status_code}, body={body}")
            resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        # If the response object exists on the exception, try to log it
        print(f"SendGrid request failed: {e}")
        raise


def send_order_email_background(to_email, order_summary_html, order_summary_text):
    try:
        _send_email_sendgrid_server(to_email, "Your Order Confirmation", order_summary_html, plain_text=order_summary_text)
        print(f"Order confirmation sent to {to_email}")
    except Exception as e:
        print(f"Failed to send order confirmation to {to_email}: {e}")

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

        # After committing the order, send a confirmation email server-side (non-blocking)
        try:
            user = User.query.get(current_user_id)
            if user and user.email and SENDGRID_API_KEY:
                # Build plain text and HTML summary from the persisted order items
                plain = "Order Confirmation\n\n"
                html = "<h2>Order Confirmation</h2><ul>"
                for oi in new_order.order_items:
                    title = oi.book.title if oi.book else f"Book {oi.book_id}"
                    plain += f"{title} ({oi.type}): ${float(oi.item_price):.2f}\n"
                    html += f"<li>{title} ({oi.type}) — ${float(oi.item_price):.2f}</li>"
                plain += f"\nTotal: ${float(total_amount):.2f}"
                html += f"</ul><p><strong>Total: ${float(total_amount):.2f}</strong></p>"

                # Send in background thread so the API call returns quickly
                threading.Thread(target=send_order_email_background, args=(user.email, html, plain), daemon=True).start()
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error preparing/sending order email: {e}")

        return {
            "message": "Order placed successfully",
            "order_id": new_order.id,
            "total_amount": float(total_amount),
            "status": "Pending"
        }, 201
