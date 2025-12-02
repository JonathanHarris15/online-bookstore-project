from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import User, Book, Order, OrderItem, Managers
from api.managment.seed import seed

app = create_app()

@app.cli.command('create-tables')
def create_tables():
    """Populates the database initially"""
    with app.app_context():
        db.create_all()
        print("Database tables created.")

@app.cli.command("reset-db")
def reset_db():
    """Drops and Recreates all tables."""
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database reset complete!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)