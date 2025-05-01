
from app import app, db
from models import Emission, Waste
from datetime import datetime, timedelta
import random

def create_sample_data():
    with app.app_context():
        # Clear existing data
        Emission.query.delete()
        Waste.query.delete()
        db.session.commit()
        
        # Generate data for last 30 days
        categories = {
            'Transport': ['Car', 'Bus', 'Train', 'Bike'],
            'Energy': ['Electricity', 'Natural Gas'],
            'Food': ['Beef', 'Chicken', 'Vegetables', 'Dairy'],
            'Waste': ['Plastic', 'Paper', 'Glass', 'Organic']
        }
        
        base_date = datetime.now() - timedelta(days=30)
        
        # Generate emissions data
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            
            # Add 2-3 emissions per day
            for _ in range(random.randint(2, 3)):
                category = random.choice(list(categories.keys()))
                subcategory = random.choice(categories[category])
                amount = round(random.uniform(1, 20), 2)
                
                emission = Emission(
                    date=current_date,
                    category=category,
                    subcategory=subcategory,
                    amount=amount,
                    unit='km' if category == 'Transport' else 'kg' if category == 'Food' else 'kWh',
                    emission_kg=round(amount * random.uniform(0.1, 2.0), 2)
                )
                db.session.add(emission)
            
            # Add 1-2 waste entries per day
            for _ in range(random.randint(1, 2)):
                waste_type = random.choice(categories['Waste'])
                weight = round(random.uniform(0.5, 5.0), 2)
                
                waste = Waste(
                    date=current_date,
                    waste_type=waste_type,
                    weight_kg=weight,
                    disposal_method=random.choice(['Recycled', 'Landfill', 'Composted']),
                    emission_kg=round(weight * random.uniform(0.1, 0.5), 2)
                )
                db.session.add(waste)
        
        db.session.commit()
        print("Sample data generated successfully!")

if __name__ == "__main__":
    create_sample_data()
