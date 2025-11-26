from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Fetch all users
    users = User.query.all()
    print(f"---- USERS IN DATABASE ({len(users)}) ----")
    for u in users:
        print(f"ID: {u.id} | User: {u.username} | Email: {u.email} | Hash: {u.password_hash[:15]}...")