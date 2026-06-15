import sys
from app.database import Base, engine
from app.models.user_model import User
from app.models.otp_model import OTPVerification
from app.models.merchant_model import Merchant
from app.models.expense_model import Expense

print("--------------------------------------------------")
print("WARNING: This will drop ALL tables in the database!")
print("Database URL in use:", engine.url)
print("--------------------------------------------------")

confirm = input("Are you sure you want to drop and recreate the schema? (y/n): ")
if confirm.lower() != 'y':
    print("Operation aborted.")
    sys.exit(0)

try:
    print("Dropping all existing database tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped successfully.")
    
    print("Re-creating all tables with updated schema structures...")
    Base.metadata.create_all(bind=engine)
    print("Schema rebuilt successfully! Your database tables are synchronized.")
    
except Exception as e:
    print("An error occurred during schema reconstruction:", e)
