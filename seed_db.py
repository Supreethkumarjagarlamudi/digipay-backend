import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models.user_model import User
from app.models.merchant_model import Merchant
from app.models.expense_model import Expense

# Make sure tables are created
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    print("Clearing existing database records for a clean seed...")
    db.query(Expense).delete()
    db.query(Merchant).delete()
    db.query(User).delete()
    db.commit()
    
    print("Inserting user accounts...")
    
    # 1. Admin User
    admin = User(
        phone_number="9999999999",
        role="admin",
        full_name="Global Administrator",
        email="admin@digipay.com",
        profile_completed=True,
        is_verified=True
    )
    db.add(admin)
    
    # 2. Customer accounts
    customers = [
        User(phone_number="9876543210", role="customer", full_name="Aarav Sharma", email="aarav@gmail.com", profile_completed=True, is_verified=True, monthly_budget=20000.0, monthly_income=50000.0),
        User(phone_number="9123456789", role="customer", full_name="Diya Patel", email="diya@gmail.com", profile_completed=True, is_verified=True, monthly_budget=15000.0, monthly_income=45000.0),
        User(phone_number="9321654987", role="customer", full_name="Kabir Mehta", email="kabir@gmail.com", profile_completed=True, is_verified=True, monthly_budget=25000.0, monthly_income=60000.0),
        User(phone_number="9444455555", role="customer", full_name="Rohan Das", email="rohan@gmail.com", profile_completed=True, is_verified=True, monthly_budget=12000.0, monthly_income=35000.0),
    ]
    for c in customers:
        db.add(c)
        
    # 3. Merchant user accounts
    merchant_users = [
        User(phone_number="9888877777", role="merchant", full_name="Vikram Rao", email="mcd@mcdonalds-in.com", profile_completed=True, is_verified=True),
        User(phone_number="9777766666", role="merchant", full_name="Sanjay Gupta", email="starbucks@coffee.com", profile_completed=True, is_verified=True),
        User(phone_number="9666655555", role="merchant", full_name="Priya Nair", email="apollo@apollopharmacy.in", profile_completed=True, is_verified=True),
        User(phone_number="9555544444", role="merchant", full_name="Anil Kumar", email="zara@zarafashion.in", profile_completed=True, is_verified=True),
        User(phone_number="9444433333", role="merchant", full_name="Meera Sen", email="ikea@ikea-retail.co.in", profile_completed=True, is_verified=True),
    ]
    for mu in merchant_users:
        db.add(mu)
        
    db.commit()
    
    # Refresh references
    db.refresh(admin)
    for c in customers:
        db.refresh(c)
    for mu in merchant_users:
        db.refresh(mu)
        
    print("Inserting merchant business details...")
    
    # Create matching merchants mapping
    merchants = [
        Merchant(
            user_id=merchant_users[0].id,
            business_name="McDonald's Family Restaurant",
            owner_name="Vikram Rao",
            category="Food",
            gst_number="29AAAAA1111A1Z1",
            description="Quick service burgers, fries, and beverage items.",
            latitude=12.9716,
            longitude=77.5946,
            altitude=920.0,
            accuracy=5.0,
            heading=45.0,
            speed=0.0,
            upi_deep_link="upi://pay?pa=mcdonalds@ybl&pn=McDonalds&mc=5812&am=0.00&cu=INR",
            is_active=True
        ),
        Merchant(
            user_id=merchant_users[1].id,
            business_name="Starbucks Coffee Corner",
            owner_name="Sanjay Gupta",
            category="Food",
            gst_number="29BBBBB2222B2Z2",
            description="Premium espresso drinks, gourmet pastries, and teas.",
            latitude=12.9722,
            longitude=77.5950,
            altitude=919.5,
            accuracy=3.5,
            heading=90.0,
            speed=0.0,
            upi_deep_link="upi://pay?pa=starbucks@icici&pn=Starbucks&mc=5812&am=0.00&cu=INR",
            is_active=True
        ),
        Merchant(
            user_id=merchant_users[2].id,
            business_name="Apollo Pharmacy Store",
            owner_name="Priya Nair",
            category="Medical",
            gst_number="29CCCCC3333C3Z3",
            description="Medicines, healthcare supplements, and wellness utilities.",
            latitude=12.9750,
            longitude=77.5910,
            altitude=921.2,
            accuracy=4.2,
            heading=180.0,
            speed=0.0,
            upi_deep_link="upi://pay?pa=apollomedical@paytm&pn=ApolloPharmacy&mc=5912&am=0.00&cu=INR",
            is_active=True
        ),
        Merchant(
            user_id=merchant_users[3].id,
            business_name="Zara Apparel Outlet",
            owner_name="Anil Kumar",
            category="Shopping",
            gst_number="29DDDDD4444D4Z4",
            description="Latest modern clothing designs and accessory store.",
            latitude=12.9690,
            longitude=77.5990,
            altitude=918.0,
            accuracy=6.0,
            heading=270.0,
            speed=0.0,
            upi_deep_link="upi://pay?pa=zararetail@hdfc&pn=Zara&mc=5691&am=0.00&cu=INR",
            is_active=True
        ),
        Merchant(
            user_id=merchant_users[4].id,
            business_name="IKEA Home Furnishings",
            owner_name="Meera Sen",
            category="Retail",
            gst_number="29EEEEE5555E5Z5",
            description="Ready-to-assemble modern furniture, home appliances, and decor.",
            latitude=13.0300,
            longitude=77.5300,
            altitude=935.0,
            accuracy=10.0,
            heading=120.0,
            speed=0.0,
            upi_deep_link="upi://pay?pa=ikeahome@sbi&pn=Ikea&mc=5712&am=0.00&cu=INR",
            is_active=True
        ),
    ]
    for m in merchants:
        db.add(m)
    db.commit()
    
    print("Generating transaction records (expenses)...")
    
    categories = {
        "Food": ["McDonald's Family Restaurant", "Starbucks Coffee Corner"],
        "Medical": ["Apollo Pharmacy Store"],
        "Shopping": ["Zara Apparel Outlet"],
        "Retail": ["IKEA Home Furnishings"],
        "Bills": ["State Power Grid Corporation", "Global Tel Telecom"],
        "Entertainment": ["PVR Cinemas Complex"],
        "Other": ["Cabs Taxi Booking"]
    }
    
    now = datetime.utcnow()
    
    # Generate ~65 transactions over the last 30 days
    seeded_expenses = []
    
    # Ensure there are transactions for "today"
    today_start = datetime(now.year, now.month, now.day)
    
    # 1. Active transactions today for merchant revenue calculations
    for i in range(8):
        cust = random.choice(customers)
        cat = random.choice(list(categories.keys()))
        store = random.choice(categories[cat])
        amt = round(random.uniform(80.0, 1500.0), 2)
        
        # distribute hours to show peak hours (e.g. morning, afternoon, evening)
        hour = random.choice([8, 9, 13, 14, 18, 19, 20])
        minute = random.randint(0, 59)
        tx_time = today_start.replace(hour=hour, minute=minute)
        
        exp = Expense(
            user_id=cust.id,
            merchant_name=store,
            amount=amt,
            category=cat,
            timestamp=tx_time,
            latitude=12.97 + random.uniform(-0.02, 0.02),
            longitude=77.59 + random.uniform(-0.02, 0.02),
            heading=random.uniform(0.0, 360.0),
            speed=random.uniform(0.0, 10.0)
        )
        seeded_expenses.append(exp)
        
    # 2. Historical transactions
    for d in range(1, 30):
        # 1-3 transactions per day
        day_time = now - timedelta(days=d)
        for _ in range(random.randint(1, 3)):
            cust = random.choice(customers)
            cat = random.choice(list(categories.keys()))
            store = random.choice(categories[cat])
            amt = round(random.uniform(40.0, 2500.0), 2)
            
            # create hour curves
            hour = random.choice([8, 12, 13, 17, 18, 19, 20, 21])
            minute = random.randint(0, 59)
            tx_time = datetime(day_time.year, day_time.month, day_time.day, hour, minute)
            
            exp = Expense(
                user_id=cust.id,
                merchant_name=store,
                amount=amt,
                category=cat,
                timestamp=tx_time,
                latitude=12.97 + random.uniform(-0.02, 0.02),
                longitude=77.59 + random.uniform(-0.02, 0.02),
                heading=random.uniform(0.0, 360.0),
                speed=random.uniform(0.0, 10.0)
            )
            seeded_expenses.append(exp)

    # 3. Add admin specific transactions to demonstrate admin capabilities
    # Admin logs in as user_id of Admin
    for i in range(10):
        cat = random.choice(list(categories.keys()))
        store = random.choice(categories[cat])
        amt = round(random.uniform(100.0, 3000.0), 2)
        day_ago = now - timedelta(days=random.randint(1, 28))
        hour = random.choice([9, 13, 19])
        tx_time = datetime(day_ago.year, day_ago.month, day_ago.day, hour, random.randint(0, 59))
        
        exp = Expense(
            user_id=admin.id,
            merchant_name=store,
            amount=amt,
            category=cat,
            timestamp=tx_time,
            latitude=12.9716,
            longitude=77.5946,
            heading=180.0,
            speed=0.0
        )
        seeded_expenses.append(exp)

    for ex in seeded_expenses:
        db.add(ex)
        
    db.commit()
    print(f"Successfully seeded database with {len(seeded_expenses)} expense entries!")
    
except Exception as e:
    db.rollback()
    print("An error occurred during database seeding:", e)
finally:
    db.close()
