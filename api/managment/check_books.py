from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import Book

app = create_app()

with app.app_context():
    # Fetch all users
    users = Book.query.all()
    print(f"---- BOOKS IN DATABASE ({len(users)}) ----")
    for u in users:
        print(f"ID: {u.id} | Title: {u.title} | Author: {u.author} | Price: {u.buy_price}/{u.rent_price}")