import os
from app import app, db
from models import Emission, Waste, User
from datetime import datetime, timedelta

# Make sure the directory for SQLite file exists
db_path = os.path.dirname(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ppang.db'))
os.makedirs(db_path, exist_ok=True)

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully in SQLite!")
    
    # Check if the database is empty and add some sample data
    print("Checking if sample data already exists...")
    emission_count = Emission.query.count()
    waste_count = Waste.query.count()
    
    if emission_count == 0:
        print("No emissions found, adding sample data...")
        
        # Add a sample transport emission
        sample_transport = Emission(
            date=datetime.now().date(),
            category="Transport",
            subcategory="Car",
            amount=50.0,
            unit="km",
            emission_kg=10.5
        )
        
        # Add a sample energy emission
        sample_energy = Emission(
            date=(datetime.now() - timedelta(days=2)).date(),
            category="Energy",
            subcategory="Electricity",
            amount=100.0,
            unit="kWh",
            emission_kg=25.0
        )
        
        # Add a sample food emission
        sample_food = Emission(
            date=(datetime.now() - timedelta(days=5)).date(),
            category="Food",
            subcategory="Beef",
            amount=0.5,
            unit="kg",
            emission_kg=15.5
        )
        
        db.session.add(sample_transport)
        db.session.add(sample_energy)
        db.session.add(sample_food)
        db.session.commit()
        print("Added 3 sample emission records")
    else:
        print(f"Found {emission_count} existing emission records, skipping sample data")
    
    if waste_count == 0:
        print("No waste records found, adding sample data...")
        
        # Add a sample waste entry
        sample_waste = Waste(
            date=datetime.now().date(),
            waste_type="Plastic",
            weight_kg=2.0,
            disposal_method="Recycled",
            emission_kg=0.8
        )
        
        db.session.add(sample_waste)
        db.session.commit()
        print("Added 1 sample waste record")
    else:
        print(f"Found {waste_count} existing waste records, skipping sample data")
        
    # Check if users exist and add a sample user if not
    user_count = User.query.count()
    if user_count == 0:
        print("No users found, adding a sample user...")
        sample_user = User(
            username="demo",
            email="demo@example.com",
            first_name="Demo",
            last_name="User",
            bio="This is a demo user account for testing the application.",
            location="Global",
            household_size=2,
            sustainability_goal="Reduce my carbon footprint by 30% this year."
        )
        sample_user.set_password("password123")
        
        db.session.add(sample_user)
        db.session.commit()
        print("Added a sample user account (username: demo, password: password123)")
    else:
        print(f"Found {user_count} existing user accounts, skipping sample user creation")
        
    # Verify if data was added correctly
    new_emission_count = Emission.query.count()
    new_waste_count = Waste.query.count()
    new_user_count = User.query.count()
    print(f"Final counts: {new_emission_count} emissions, {new_waste_count} waste records, {new_user_count} users")