import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

load_dotenv()

# --- Get credentials from environment variables ---
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

print(f"---- TESTING WITH MYSQL-CONNECTOR ----")
print(f"User: {db_user}")
print(f"Host: {db_host}")

try:
    # URI uses 'mysql+mysqlconnector' instead of 'pymysql'
    uri = f"mysql+mysqlconnector://{db_user}:{quote_plus(db_pass)}@{db_host}/{db_name}"
    
    engine = create_engine(uri)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("\n✅ SUCCESS! The official Oracle driver worked.")
except Exception as e:
    print(f"\n❌ FAILED: {e}")