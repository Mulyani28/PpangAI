from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Emission(db.Model):
    __tablename__ = 'emissions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    emission_kg = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Emission(id={self.id}, date={self.date}, category={self.category}, emission_kg={self.emission_kg})>"
        
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'category': self.category,
            'subcategory': self.subcategory,
            'amount': self.amount,
            'unit': self.unit,
            'emission_kg': self.emission_kg,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Waste(db.Model):
    __tablename__ = 'waste'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    waste_type = db.Column(db.String(50), nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    disposal_method = db.Column(db.String(50), nullable=False)
    emission_kg = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Waste(id={self.id}, date={self.date}, waste_type={self.waste_type}, weight_kg={self.weight_kg})>"
        
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'waste_type': self.waste_type,
            'weight_kg': self.weight_kg,
            'disposal_method': self.disposal_method,
            'emission_kg': self.emission_kg,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    bio = db.Column(db.Text)
    location = db.Column(db.String(128))
    household_size = db.Column(db.Integer, default=1)
    sustainability_goal = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'location': self.location,
            'household_size': self.household_size,
            'sustainability_goal': self.sustainability_goal,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }