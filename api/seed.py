from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from app import create_app, db
# ADD Order and OrderItem to imports
from app.models import Book, User, Managers, Order, OrderItem

def seed():
    app = create_app()
    with app.app_context():
        print("🌱 Starting database seed...")

        # --- 1. SEED BOOKS ---
        print("📚 Seeding Books...")
        books_data = [
            {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "buy_price": 10.99, "rent_price": 2.50},
            {"title": "1984", "author": "George Orwell", "buy_price": 8.99, "rent_price": 1.99},
            {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "buy_price": 15.00, "rent_price": 4.50},
            {"title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "buy_price": 95.00, "rent_price": 35.00},
            {"title": "Clean Code", "author": "Robert C. Martin", "buy_price": 40.00, "rent_price": 12.00}
        ]

        for data in books_data:
            existing_book = Book.query.filter_by(title=data["title"]).first()
            if not existing_book:
                new_book = Book(
                    title=data['title'],
                    author=data['author'],
                    buy_price=data['buy_price'],
                    rent_price=data['rent_price'],
                    is_available=True
                )
                db.session.add(new_book)
                print(f"   -> Added: {data['title']}")
            else:
                print(f"   -> Skipped: {data['title']}")

        # --- 2. SEED USERS ---
        print("\n👤 Seeding Users...")
        users_data = [
            {"username": "test_customer", "email": "customer@test.com", "password": "CustomerPass1!", "is_manager": False},
            {"username": "test_admin", "email": "admin@test.com", "password": "AdminPass1!", "is_manager": True}
        ]

        for u_data in users_data:
            existing_user = User.query.filter_by(username=u_data['username']).first()
            if not existing_user:
                new_user = User(username=u_data['username'], email=u_data['email'])
                new_user.set_password(u_data['password'])
                db.session.add(new_user)
                db.session.flush() # Get ID
                
                print(f"   -> Added User: {u_data['username']}")

                if u_data['is_manager']:
                    new_manager = Managers(user_id=new_user.id, user_name=new_user.username)
                    db.session.add(new_manager)
                    print(f"      -> Promoted {u_data['username']} to Manager")
            else:
                print(f"   -> Skipped User: {u_data['username']}")

        # --- 3. SEED ORDERS (NEW SECTION) ---
        print("\n📦 Seeding Dummy Order...")
        
        # We need the customer to attach the order to
        customer = User.query.filter_by(username="test_customer").first()
        
        # Only create if the customer exists and doesn't have an order yet (to prevent duplicates)
        if customer:
            existing_order = Order.query.filter_by(user_id=customer.id).first()
            
            if not existing_order:
                # Find two books to put in the order
                book1 = Book.query.filter_by(title="The Great Gatsby").first()
                book2 = Book.query.filter_by(title="1984").first()

                if book1 and book2:
                    # Calculate total (Buying Gatsby + Renting 1984)
                    total = float(book1.buy_price) + float(book2.rent_price)

                    # Create the Receipt
                    new_order = Order(
                        user_id=customer.id,
                        order_date=datetime.utcnow(),
                        total_amount=total,
                        payment_status="Pending"
                    )
                    db.session.add(new_order)
                    db.session.flush() # Get Order ID

                    # Create the Line Items
                    item1 = OrderItem(order_id=new_order.id, book_id=book1.id, type="buy", item_price=book1.buy_price)
                    item2 = OrderItem(order_id=new_order.id, book_id=book2.id, type="rent", item_price=book2.rent_price)
                    
                    db.session.add(item1)
                    db.session.add(item2)
                    
                    print(f"   -> Added Order #{new_order.id} for {customer.username} ($ {total})")
            else:
                print(f"   -> Skipped Order: {customer.username} already has one.")

        # --- 4. COMMIT ALL ---
        db.session.commit()
        print("\n✅ Database seeded successfully!")

if __name__ == '__main__':
    seed()