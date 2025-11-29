from flask import request
from flask_restful import Resource
from app.models import Book, Managers
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

class BookList(Resource):
    def get(self):
        query = request.args.get('q')
        
        #if there is a query when they asked for a book, filter
        if query:
            books = Book.query.filter(
                (Book.title.ilike(f'%{query}%')) |
                (Book.author.ilike(f'%{query}%'))
            ).all()
        else:
            books = Book.query.all()
        
        #Format the output 
        output = []
        for book in books:
            output.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'buy_price': float(book.buy_price),
                'rent_price': float(book.rent_price),
                'is_available': book.is_available
            })
        
        return output, 200
    
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        #run the check to see if the user is a manager
        manager_entry = Managers.query.filter_by(user_id=current_user_id).first()
        if not manager_entry:
            return {"message": "Authorization failed: Manager privileges required"}, 403
        
        
        #get the data from the post
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        buy_price = data.get('buy_price')
        rent_price = data.get('rent_price')

        if not title or not buy_price:
            return {"message": "Missing required fields"}, 400

        new_book = Book(
            title=title,
            author=author,
            buy_price=buy_price,
            rent_price=rent_price,
            is_available=True
        )

        db.session.add(new_book)
        db.session.commit(
        )

        return {"message": f"Book '{title}' added successfully"}, 201

class BookResource(Resource):
    def get(self, book_id):
        book = Book.query.get_or_404(book_id)
        return {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'buy_price': float(book.buy_price),
            'rent_price': float(book.rent_price),
            'is_available': book.is_available
        }

    @jwt_required()
    def patch(self, book_id):
        manager_entry = Managers.query.filter_by(user_id=get_jwt_identity()).first()
        if not manager_entry:
            return {"message": "Manager access required"}, 403

        book = Book.query.get_or_404(book_id)
        data = request.get_json()

        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.buy_price = data.get('buy_price', book.buy_price)
        book.rent_price = data.get('rent_price', book.rent_price)
        book.is_available = data.get('is_available', book.is_available)
        
        db.session.commit()
        return {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'buy_price': float(book.buy_price),
            'rent_price': float(book.rent_price),
            'is_available': book.is_available
        }

    @jwt_required()
    def delete(self, book_id):
        manager_entry = Managers.query.filter_by(user_id=get_jwt_identity()).first()
        if not manager_entry:
            return {"message": "Manager access required"}, 403

        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return {"message": f"Book with ID {book_id} has been deleted."}



