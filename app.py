from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import pandas as pd
import numpy as np
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, DateField, TextAreaField, PasswordField, IntegerField, EmailField
from wtforms.validators import DataRequired, NumberRange, Email, Length, EqualTo, ValidationError
from datetime import datetime, timedelta
import os
import uuid
from functools import wraps
from io import StringIO
from flask_migrate import Migrate
from dotenv import load_dotenv



# Load environment variables
load_dotenv()

# Import database models
from models import db, Emission, Waste, User

# Import our custom modules
from ml_models import train_prediction_model, predict_future_emissions
from carbon_calculator import (
    calculate_transport_emissions, calculate_energy_emissions,
    calculate_food_emissions, calculate_waste_emissions,
    calculate_total_carbon_footprint, compare_to_average_footprint
)
from ai_insights import (
    analyze_emission_patterns, generate_personalized_recommendations,
    analyze_sustainability_score
)
from visualization import (
    plot_emissions_over_time, plot_emissions_by_category,
    plot_waste_composition, create_footprint_comparison,
    plot_emissions_breakdown, plot_emission_trends
)
from recommendations import (
    generate_transport_recommendations, generate_energy_recommendations,
    generate_waste_recommendations, generate_overall_recommendations
)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_' + str(uuid.uuid4()))
app.config['APP_NAME'] = 'Ppang - Carbon Footprint Tracker'

# Set database URI for SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ppang.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
migrate = Migrate(app, db)

# Initialize data storage for legacy support
if not os.path.exists('data'):
    os.makedirs('data')

# Database helper functions
def get_emission_data():
    """Get emission data from database"""
    try:
        print("Querying emissions from database...")
        emissions = Emission.query.all()
        print(f"Found {len(emissions)} emission records")
        
        if emissions:
            # Convert to DataFrame for compatibility with existing code
            data = [e.to_dict() for e in emissions]
            df = pd.DataFrame(data)
            # Convert date strings to datetime objects
            df['date'] = pd.to_datetime(df['date'])
            print(f"Converted to DataFrame with {len(df)} rows")
            print(f"DataFrame columns: {df.columns.tolist()}")
            print(f"First few records: {df.head(2).to_dict('records')}")
            return df
        else:
            print("No emission records found, returning empty DataFrame")
            return pd.DataFrame({
                'date': [], 'category': [], 'subcategory': [],
                'amount': [], 'unit': [], 'emission_kg': []
            })
    except Exception as e:
        print(f"Error getting emission data: {e}")
        import traceback
        print(traceback.format_exc())
        return pd.DataFrame({
            'date': [], 'category': [], 'subcategory': [],
            'amount': [], 'unit': [], 'emission_kg': []
        })

def get_waste_data():
    """Get waste data from database"""
    try:
        wastes = Waste.query.all()
        if wastes:
            # Convert to DataFrame for compatibility with existing code
            data = [w.to_dict() for w in wastes]
            df = pd.DataFrame(data)
            # Convert date strings to datetime objects
            df['date'] = pd.to_datetime(df['date'])
            return df
        else:
            return pd.DataFrame({
                'date': [], 'waste_type': [], 'weight_kg': [],
                'disposal_method': [], 'emission_kg': []
            })
    except Exception as e:
        print(f"Error getting waste data: {e}")
        return pd.DataFrame({
            'date': [], 'waste_type': [], 'weight_kg': [],
            'disposal_method': [], 'emission_kg': []
        })

def add_emission_entry(df, date, category, subcategory, amount, unit, emission_kg):
    """Add a new emission entry to the database"""
    try:
        print(f"Adding emission: {date}, {category}, {subcategory}, {amount} {unit}, {emission_kg} kg CO2e")
        
        # Convert date if needed
        if isinstance(date, str):
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date_obj = date
            
        print(f"Converted date: {date_obj}")
        
        # Create new emission record
        new_emission = Emission(
            date=date_obj,
            category=category,
            subcategory=subcategory,
            amount=amount,
            unit=unit,
            emission_kg=emission_kg
        )
        
        # Add to database
        db.session.add(new_emission)
        print("Added to session, committing...")
        db.session.commit()
        print("Commit successful!")
        
        # Double-check if the entry was added
        emission_count = Emission.query.count()
        print(f"Total emissions in database: {emission_count}")
        
        # Update DataFrame for compatibility with existing code
        return get_emission_data()
    except Exception as e:
        db.session.rollback()
        print(f"ERROR adding emission entry: {e}")
        import traceback
        print(traceback.format_exc())
        
        # Add to DataFrame for compatibility if database fails
        new_row = pd.DataFrame({
            'date': [date],
            'category': [category],
            'subcategory': [subcategory],
            'amount': [amount],
            'unit': [unit],
            'emission_kg': [emission_kg]
        })
        return pd.concat([df, new_row], ignore_index=True)
    
def add_waste_entry(df, date, waste_type, weight_kg, disposal_method, emission_kg):
    """Add a new waste entry to the database"""
    try:
        print(f"Adding waste: {date}, {waste_type}, {weight_kg} kg, {disposal_method}, {emission_kg} kg CO2e")
        
        # Convert date if needed
        if isinstance(date, str):
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date_obj = date
            
        print(f"Converted date: {date_obj}")
        
        # Create new waste record
        new_waste = Waste(
            date=date_obj,
            waste_type=waste_type,
            weight_kg=weight_kg,
            disposal_method=disposal_method,
            emission_kg=emission_kg
        )
        
        # Add to database
        db.session.add(new_waste)
        print("Added to session, committing...")
        db.session.commit()
        print("Commit successful!")
        
        # Double-check if the entry was added
        waste_count = Waste.query.count()
        print(f"Total waste entries in database: {waste_count}")
        
        # Update DataFrame for compatibility with existing code
        return get_waste_data()
    except Exception as e:
        db.session.rollback()
        print(f"ERROR adding waste entry: {e}")
        import traceback
        print(traceback.format_exc())
        
        # Add to DataFrame for compatibility if database fails
        new_row = pd.DataFrame({
            'date': [date],
            'waste_type': [waste_type],
            'weight_kg': [weight_kg],
            'disposal_method': [disposal_method],
            'emission_kg': [emission_kg]
        })
        return pd.concat([df, new_row], ignore_index=True)

# Form classes for data entry
class TransportForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now)
    transport_type = SelectField('Transport Type', 
                               choices=[('Car', 'Car'), ('Bus', 'Bus'), ('Train', 'Train'), 
                                        ('Plane', 'Plane'), ('Bike', 'Bike'), ('Walking', 'Walking'), 
                                        ('Other', 'Other')],
                               validators=[DataRequired()])
    distance = FloatField('Distance (km)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Calculate Emissions')

class EnergyForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now)
    energy_type = SelectField('Energy Type', 
                            choices=[('Electricity', 'Electricity'), ('Natural Gas', 'Natural Gas'), 
                                    ('Heating Oil', 'Heating Oil'), ('Renewable', 'Renewable'), 
                                    ('Other', 'Other')],
                            validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Calculate Emissions')

class FoodForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now)
    food_type = SelectField('Food Type', 
                          choices=[('Beef', 'Beef'), ('Pork', 'Pork'), ('Chicken', 'Chicken'), 
                                  ('Fish', 'Fish'), ('Dairy', 'Dairy'), ('Vegetables', 'Vegetables'), 
                                  ('Fruits', 'Fruits'), ('Processed Foods', 'Processed Foods')],
                          validators=[DataRequired()])
    weight = FloatField('Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Calculate Emissions')

class WasteForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now)
    waste_type = SelectField('Waste Type', 
                           choices=[('Plastic', 'Plastic'), ('Paper', 'Paper'), ('Glass', 'Glass'), 
                                   ('Metal', 'Metal'), ('Organic', 'Organic'), ('Electronic', 'Electronic'), 
                                   ('Other', 'Other')],
                           validators=[DataRequired()])
    weight = FloatField('Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])
    disposal_method = SelectField('Disposal Method', 
                                choices=[('Landfill', 'Landfill'), ('Recycled', 'Recycled'), 
                                        ('Composted', 'Composted'), ('Reused', 'Reused'), 
                                        ('Incinerated', 'Incinerated')],
                                validators=[DataRequired()])
    submit = SubmitField('Calculate Emissions')

class CustomEmissionForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now)
    category = StringField('Category', validators=[DataRequired()])
    subcategory = StringField('Subcategory', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField('Unit', validators=[DataRequired()])
    emission_kg = FloatField('Emission (kg CO2e)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Custom Emission')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    location = StringField('Location', validators=[Length(max=128)])
    household_size = IntegerField('Household Size', validators=[NumberRange(min=1, max=20)], default=1)
    sustainability_goal = TextAreaField('Sustainability Goal', validators=[Length(max=500)])
    submit = SubmitField('Update Profile')

# Define routes
@app.route('/')
def index():
    """Home page - Dashboard"""
    emission_data = get_emission_data()
    waste_data = get_waste_data()
    
    # Prepare metrics
    total_emissions = round(emission_data['emission_kg'].sum() if not emission_data.empty else 0, 2)
    
    # Calculate time periods for emissions analysis
    current_date = datetime.now()
    last_month = current_date - timedelta(days=30)
    previous_month = current_date - timedelta(days=60)
    
    # Calculate current month emissions
    if not emission_data.empty:
        emission_data['date'] = pd.to_datetime(emission_data['date'])
        last_month_df = emission_data[emission_data['date'] > last_month]
        month_emissions = round(last_month_df['emission_kg'].sum(), 2)
        
        # Calculate previous month emissions for trend
        prev_month_df = emission_data[(emission_data['date'] > previous_month) & (emission_data['date'] <= last_month)]
        prev_month_emissions = round(prev_month_df['emission_kg'].sum(), 2) if not prev_month_df.empty else 0
        
        # Calculate trend percentage
        if prev_month_emissions > 0:
            trend_emissions = round(((month_emissions - prev_month_emissions) / prev_month_emissions) * 100)
        else:
            trend_emissions = 0  # Default when no previous data exists
    else:
        month_emissions = 0
        trend_emissions = 0
    
    # Calculate waste metrics
    total_waste = round(waste_data['weight_kg'].sum() if not waste_data.empty else 0, 2)
    
    # Calculate recycling rate
    recycling_rate = 0
    if not waste_data.empty and total_waste > 0:
        recycled = waste_data[waste_data['disposal_method'].isin(['Recycled', 'Composted', 'Reused'])]
        recycling_rate = round((recycled['weight_kg'].sum() / total_waste) * 100, 1)
    
    # Generate charts (create placeholder charts if no data)
    charts = {}
    
    # Emissions over time chart
    emissions_chart = plot_emissions_over_time(emission_data)
    charts['emissions_time'] = json.dumps(emissions_chart, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Emissions by category chart
    categories = []
    if not emission_data.empty and len(emission_data) > 0:
        # Get emissions categories and their percentages for chat functionality
        category_totals = emission_data.groupby('category')['emission_kg'].sum().reset_index()
        total = category_totals['emission_kg'].sum()
        
        for _, row in category_totals.iterrows():
            percentage = round((row['emission_kg'] / total) * 100, 1)
            categories.append({
                'name': row['category'], 
                'percentage': percentage,
                'value': row['emission_kg']
            })
        
        # Sort categories by percentage (highest first)
        categories = sorted(categories, key=lambda x: x['percentage'], reverse=True)
            
        # Create the category chart using our visualization function
        category_chart = plot_emissions_by_category(emission_data)
    else:
        # Create empty chart with informative message
        fig = go.Figure()
        fig.update_layout(
            title="No emission data available yet",
            annotations=[
                dict(
                    text="Add emission data through the Data Entry page to see your carbon footprint breakdown.",
                    showarrow=False,
                    x=0.5,
                    y=0.5,
                    font=dict(size=14)
                )
            ]
        )
        category_chart = fig
    
    charts['emissions_category'] = json.dumps(category_chart, cls=plotly.utils.PlotlyJSONEncoder)
    
    
    
    # Waste composition chart
    if not waste_data.empty and len(waste_data) > 0:
        waste_chart = plot_waste_composition(waste_data)
    else:
        # Create empty chart with informative message
        fig = go.Figure()
        fig.update_layout(
            title="No waste data available yet",
            annotations=[
                dict(
                    text="Add waste data through the Data Entry page to see your waste composition.",
                    showarrow=False,
                    x=0.5,
                    y=0.5,
                    font=dict(size=14)
                )
            ]
        )
        waste_chart = fig
    
    charts['waste_composition'] = json.dumps(waste_chart, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('dashboard.html', 
                          total_emissions=total_emissions,
                          month_emissions=month_emissions,
                          total_waste=total_waste,
                          recycling_rate=recycling_rate,
                          trend_emissions=trend_emissions,
                          categories=categories,
                          charts=charts)

@app.route('/data_entry')
def data_entry():
    """Data entry page"""
    transport_form = TransportForm()
    energy_form = EnergyForm()
    food_form = FoodForm()
    custom_form = CustomEmissionForm()
    waste_form = WasteForm()
    
    # Get current data
    emission_data = get_emission_data()
    waste_data = get_waste_data()
    
    return render_template('data_entry.html',
                          transport_form=transport_form,
                          energy_form=energy_form,
                          food_form=food_form,
                          custom_form=custom_form,
                          waste_form=waste_form,
                          emission_data=emission_data.to_dict('records') if not emission_data.empty else [],
                          waste_data=waste_data.to_dict('records') if not waste_data.empty else [])

@app.route('/add_transport', methods=['POST'])
def add_transport():
    """Add transport emission"""
    form = TransportForm()
    if form.validate_on_submit():
        emission_data = get_emission_data()
        
        date = form.date.data.strftime('%Y-%m-%d')
        transport_type = form.transport_type.data
        distance = form.distance.data
        unit = "km"
        
        # Calculate emissions
        emission_kg = calculate_transport_emissions(transport_type, distance)
        
        # Add entry
        new_entry = add_emission_entry(
            emission_data,
            date,
            "Transport",
            transport_type,
            distance,
            unit,
            emission_kg
        )
        
        # Show success message
        flash(f"Added {emission_kg:.2f} kg CO2e from {transport_type}", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", "error")
    
    return redirect(url_for('data_entry'))

@app.route('/add_energy', methods=['POST'])
def add_energy():
    """Add energy emission"""
    form = EnergyForm()
    if form.validate_on_submit():
        emission_data = get_emission_data()
        
        date = form.date.data.strftime('%Y-%m-%d')
        energy_type = form.energy_type.data
        amount = form.amount.data
        unit = "kWh" if energy_type == "Electricity" or energy_type == "Renewable" else "m³"
        
        # Calculate emissions
        emission_kg = calculate_energy_emissions(energy_type, amount)
        
        # Add entry
        new_entry = add_emission_entry(
            emission_data,
            date,
            "Energy",
            energy_type,
            amount,
            unit,
            emission_kg
        )
        
        # Show success message
        flash(f"Added {emission_kg:.2f} kg CO2e from {energy_type}", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", "error")
    
    return redirect(url_for('data_entry'))

@app.route('/add_food', methods=['POST'])
def add_food():
    """Add food emission"""
    form = FoodForm()
    if form.validate_on_submit():
        emission_data = get_emission_data()
        
        date = form.date.data.strftime('%Y-%m-%d')
        food_type = form.food_type.data
        weight = form.weight.data
        unit = "kg"
        
        # Calculate emissions
        emission_kg = calculate_food_emissions(food_type, weight)
        
        # Add entry
        new_entry = add_emission_entry(
            emission_data,
            date,
            "Food",
            food_type,
            weight,
            unit,
            emission_kg
        )
        
        # Show success message
        flash(f"Added {emission_kg:.2f} kg CO2e from {food_type}", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", "error")
    
    return redirect(url_for('data_entry'))

@app.route('/add_custom', methods=['POST'])
def add_custom():
    """Add custom emission"""
    form = CustomEmissionForm()
    if form.validate_on_submit():
        emission_data = get_emission_data()
        
        date = form.date.data.strftime('%Y-%m-%d')
        category = form.category.data
        subcategory = form.subcategory.data
        amount = form.amount.data
        unit = form.unit.data
        emission_kg = form.emission_kg.data
        
        # Add entry
        new_entry = add_emission_entry(
            emission_data,
            date,
            category,
            subcategory,
            amount,
            unit,
            emission_kg
        )
        
        # Show success message
        flash(f"Added {emission_kg:.2f} kg CO2e from {subcategory}", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", "error")
    
    return redirect(url_for('data_entry'))

@app.route('/add_waste', methods=['POST'])
def add_waste():
    """Add waste data"""
    form = WasteForm()
    if form.validate_on_submit():
        waste_data = get_waste_data()
        
        date = form.date.data.strftime('%Y-%m-%d')
        waste_type = form.waste_type.data
        weight = form.weight.data
        disposal_method = form.disposal_method.data
        
        # Calculate emissions
        emission_kg = calculate_waste_emissions(waste_type, weight, disposal_method)
        
        # Add entry
        new_entry = add_waste_entry(
            waste_data,
            date,
            waste_type,
            weight,
            disposal_method,
            emission_kg
        )
        
        # Show success message
        flash(f"Added {weight} kg of {waste_type} waste with {emission_kg:.2f} kg CO2e", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", "error")
    
    return redirect(url_for('data_entry'))

@app.route('/predictions', methods=['GET', 'POST'])
def predictions():
    """Predictions and forecasting page"""
    emission_data = get_emission_data()
    
    # Check if we have enough data
    if emission_data.empty or len(emission_data) < 5:
        return render_template('predictions.html', 
                              error="Not enough data for predictions. Please add at least 5 emission entries.")
    
    # Default prediction days
    prediction_days = 30
    selected_scenario = "25% Reduction"
    
    # Handle form submission
    if request.method == 'POST':
        prediction_days = int(request.form.get('prediction_days', 30))
        selected_scenario = request.form.get('reduction_scenario', "25% Reduction")
    
    # Prepare data
    df = emission_data.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Group by date and sum emissions
    daily_emissions = df.groupby('date')['emission_kg'].sum().reset_index()
    
    # Make sure we have sequential dates by reindexing
    min_date = daily_emissions['date'].min()
    max_date = daily_emissions['date'].max()
    date_range = pd.date_range(start=min_date, end=max_date)
    daily_emissions = daily_emissions.set_index('date').reindex(date_range).fillna(0).reset_index()
    daily_emissions = daily_emissions.rename(columns={'index': 'date'})
    
    # Create features
    daily_emissions['day_of_week'] = daily_emissions['date'].dt.dayofweek
    daily_emissions['month'] = daily_emissions['date'].dt.month
    daily_emissions['day'] = daily_emissions['date'].dt.day
    
    # Train model
    model = train_prediction_model(daily_emissions)
    
    # Generate predictions
    last_date = daily_emissions['date'].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=prediction_days)
    future_emissions = predict_future_emissions(model, future_dates)
    
    # Create forecast chart
    forecast_fig = go.Figure()
    
    # Actual emissions
    forecast_fig.add_trace(go.Scatter(
        x=daily_emissions['date'],
        y=daily_emissions['emission_kg'],
        mode='lines+markers',
        name='Actual Emissions',
        line=dict(color='#1f77b4')
    ))
    
    # Predicted emissions
    forecast_fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_emissions,
        mode='lines',
        name='Predicted Emissions',
        line=dict(color='#ff7f0e', dash='dash')
    ))
    
    forecast_fig.update_layout(
        title='Carbon Emissions Forecast',
        xaxis_title='Date',
        yaxis_title='Emissions (kg CO2e)',
        hovermode='x unified'
    )
    
    # Calculate prediction summary
    total_predicted = sum(future_emissions)
    avg_predicted = np.mean(future_emissions)
    
    # Reduction scenarios
    reduction_options = {
        "10% Reduction": 0.9,
        "25% Reduction": 0.75,
        "50% Reduction": 0.5
    }
    
    reduction_factor = reduction_options.get(selected_scenario, 0.75)
    reduced_emissions = [e * reduction_factor for e in future_emissions]
    reduction_amount = sum(future_emissions) - sum(reduced_emissions)
    
    # Create reduction scenario chart
    scenario_fig = go.Figure()
    
    # Baseline prediction
    scenario_fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_emissions,
        mode='lines',
        name='Baseline Prediction',
        line=dict(color='#ff7f0e')
    ))
    
    # Reduced emissions
    scenario_fig.add_trace(go.Scatter(
        x=future_dates,
        y=reduced_emissions,
        mode='lines',
        name=f'{selected_scenario} Scenario',
        line=dict(color='#2ca02c')
    ))
    
    scenario_fig.update_layout(
        title=f'Emissions with {selected_scenario}',
        xaxis_title='Date',
        yaxis_title='Emissions (kg CO2e)',
        hovermode='x unified'
    )
    
    # Convert charts to JSON for template
    charts = {
        'forecast': json.dumps(forecast_fig, cls=plotly.utils.PlotlyJSONEncoder),
        'scenario': json.dumps(scenario_fig, cls=plotly.utils.PlotlyJSONEncoder)
    }
    
    return render_template('predictions.html',
                          prediction_days=prediction_days,
                          selected_scenario=selected_scenario,
                          total_predicted=total_predicted,
                          avg_predicted=avg_predicted,
                          reduction_amount=reduction_amount,
                          future_days=prediction_days,
                          charts=charts,
                          reduction_options=list(reduction_options.keys()))

@app.route('/recommendations')
def recommendations():
    """Recommendations page"""
    emission_data = get_emission_data()
    waste_data = get_waste_data()
    
    # Check if we have emission data
    if emission_data.empty:
        return render_template('recommendations.html', 
                              error="Add emission data to receive personalized recommendations.")
    
    # Analyze emissions data
    df = emission_data.copy()
    
    # Get emissions by category
    category_emissions = df.groupby('category')['emission_kg'].sum().reset_index()
    
    # Identify highest emission categories
    sorted_categories = category_emissions.sort_values('emission_kg', ascending=False)
    if not sorted_categories.empty:
        highest_category = sorted_categories.iloc[0]['category']
    else:
        highest_category = "Unknown"
    
    # Create emission breakdown chart using the same approach as in the dashboard
    # Sort by emission value (highest first) to make the chart consistent
    category_emissions = category_emissions.sort_values('emission_kg', ascending=False)
    
    # Custom colors for better visibility
    custom_colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#E91E63', '#F44336']
    
    # Create cleaner pie chart with simple design
    breakdown_fig = go.Figure(data=[go.Pie(
        labels=[row['category'] for _, row in category_emissions.iterrows()],
        values=category_emissions['emission_kg'].tolist(),
        hole=0.4,
        textinfo='label+percent',
        marker=dict(colors=custom_colors[:len(category_emissions)]),
        pull=[0.05 if i == 0 else 0 for i in range(len(category_emissions))],
        textposition='inside',
        textfont=dict(size=14, color='white'),
        insidetextorientation='horizontal'
    )])
    
    # Calculate total
    total_emissions = category_emissions['emission_kg'].sum()
    
    # Add a cleaner title and layout
    breakdown_fig.update_layout(
        title={
            'text': 'Your Carbon Footprint by Category',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=18)
        },
        margin=dict(t=80, b=80, l=20, r=20),
        annotations=[dict(
            text=f"Total: {total_emissions:.1f} kg CO₂e",
            x=0.5, y=0.5,
            font=dict(size=14),
            showarrow=False
        )]
    )
    
    # Generate recommendations
    all_recommendations = {}
    
    # Transport recommendations
    if 'Transport' in df['category'].values:
        transport_emissions = df[df['category'] == 'Transport'].copy()
        transport_total = transport_emissions['emission_kg'].sum()
        transport_recs = generate_transport_recommendations(transport_emissions)
        all_recommendations['transport'] = transport_recs
    
    # Energy recommendations
    if 'Energy' in df['category'].values:
        energy_emissions = df[df['category'] == 'Energy'].copy()
        energy_total = energy_emissions['emission_kg'].sum()
        energy_recs = generate_energy_recommendations(energy_emissions)
        all_recommendations['energy'] = energy_recs
    
    # Waste recommendations
    if not waste_data.empty:
        waste_recs = generate_waste_recommendations(waste_data)
        all_recommendations['waste'] = waste_recs
    
    # Overall recommendations
    overall_recs = generate_overall_recommendations(emission_data, waste_data)
    all_recommendations['overall'] = overall_recs
    
    # Create action plan
    action_items = []
    
    # Add top recommendations for each category to action plan
    if 'transport' in all_recommendations and all_recommendations['transport']:
        action_items.append(all_recommendations['transport'][0])
    
    if 'energy' in all_recommendations and all_recommendations['energy']:
        action_items.append(all_recommendations['energy'][0])
    
    if 'waste' in all_recommendations and all_recommendations['waste']:
        action_items.append(all_recommendations['waste'][0])
    
    # Add 1-2 overall recommendations
    if 'overall' in all_recommendations:
        action_items.extend(all_recommendations['overall'][:2])
    
    # Create timeline for action plan
    timeline = ["This week", "Next week", "Within a month", "Within three months"]
    action_plan = []
    
    for i, (time, action) in enumerate(zip(timeline[:len(action_items)], action_items)):
        action_plan.append({"time": time, "action": action})
    
    return render_template('recommendations.html',
                           highest_category=highest_category,
                           breakdown_chart=json.dumps(breakdown_fig, cls=plotly.utils.PlotlyJSONEncoder),
                           recommendations=all_recommendations,
                           action_plan=action_plan)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


# User authentication and profile routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    # Redirect if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('profile'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('register.html', form=form)
        
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        # Add to database
        db.session.add(user)
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        
        flash('Your account has been created! Welcome to Ppang.', 'success')
        return redirect(url_for('profile'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    # Redirect if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):
            # Set session
            session['user_id'] = user.id
            session['username'] = user.username
            
            flash('You have been logged in successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'error')
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """User logout"""
    # Clear session
    session.pop('user_id', None)
    session.pop('username', None)
    
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile page"""
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('login'))
    
    # Get user
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('logout'))
    
    form = ProfileForm()
    
    # Pre-fill form with existing data if it's a GET request
    if request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.bio.data = user.bio
        form.location.data = user.location
        form.household_size.data = user.household_size
        form.sustainability_goal.data = user.sustainability_goal
    
    # Process form submission
    if form.validate_on_submit():
        # Update user data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.bio = form.bio.data
        user.location = form.location.data
        user.household_size = form.household_size.data
        user.sustainability_goal = form.sustainability_goal.data
        
        # Save to database
        db.session.commit()
        
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Get user's emission data
    emission_data = get_emission_data()
    total_emissions = round(emission_data['emission_kg'].sum() if not emission_data.empty else 0, 2)
    
    # Calculate per capita emissions (household size adjusted)
    per_capita_emissions = round(total_emissions / user.household_size, 2) if user.household_size > 0 else total_emissions
    
    # Emission breakdown by category
    category_chart = plot_emissions_by_category(emission_data)
    category_chart_json = json.dumps(category_chart, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Footprint comparison
    footprint_comp = create_footprint_comparison(total_emissions)
    footprint_comp_json = json.dumps(footprint_comp, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('profile.html', 
                         user=user, 
                         form=form, 
                         total_emissions=total_emissions,
                         per_capita_emissions=per_capita_emissions,
                         category_chart=category_chart_json,
                         footprint_chart=footprint_comp_json)


# Chat API endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for Chat with Ppang feature"""
    try:
        # Get user message from request
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': 'No message provided'
            }), 400
        
        # Get user's emission data for context
        emission_data = get_emission_data()
        total_emissions = round(emission_data['emission_kg'].sum() if not emission_data.empty else 0, 2)
        
        # Get category breakdown
        category_breakdown = {}
        if not emission_data.empty:
            category_emissions = emission_data.groupby('category')['emission_kg'].sum()
            for category, value in category_emissions.items():
                category_breakdown[category] = round(value, 2)
        
        # Generate response based on user message and data context
        response = generate_chat_response(user_message, total_emissions, category_breakdown)
        
        return jsonify({
            'status': 'success',
            'response': response
        })
    
    except Exception as e:
        app.logger.error(f"Chat API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred processing your request'
        }), 500


@app.route('/ai-insights')
def ai_insights_page():
    """AI-powered insights and analysis page"""
    # Authentication check
    if 'user_id' not in session:
        flash('Please log in to access AI insights', 'warning')
        return redirect(url_for('login'))
    
    # Get data
    emission_data = get_emission_data()
    waste_data = get_waste_data()
    
    # If no data, show a message
    if emission_data.empty:
        flash('Add some emission data to get AI-powered insights', 'info')
        return redirect(url_for('data_entry'))
    
    # Get user profile if available
    user_profile = None
    if session.get('user_id'):
        user = User.query.get(session['user_id'])
        if user:
            user_profile = user.to_dict()
    
    # Get AI insights
    try:
        insights = analyze_emission_patterns(emission_data)
        recommendations = generate_personalized_recommendations(emission_data, user_profile)
        sustainability_score = analyze_sustainability_score(emission_data, waste_data)
        
        # Convert insights to plotly charts
        time_chart = plot_emissions_over_time(emission_data, title="Your Emission Trends")
        category_chart = plot_emissions_by_category(emission_data, title="Emissions by Category")
        
        # Create a sustainability score gauge chart
        score = sustainability_score.get('score', 50)
        score_chart = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "Sustainability Score"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if score > 75 else "orange" if score > 50 else "red"},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "green"}
                ]
            }
        ))
        
        # Generate trend chart
        trend_chart = plot_emission_trends(emission_data)
        
        # Convert the plotly figures to JSON for rendering
        time_chart_json = json.dumps(time_chart, cls=plotly.utils.PlotlyJSONEncoder)
        category_chart_json = json.dumps(category_chart, cls=plotly.utils.PlotlyJSONEncoder)
        score_chart_json = json.dumps(score_chart, cls=plotly.utils.PlotlyJSONEncoder)
        trend_chart_json = json.dumps(trend_chart, cls=plotly.utils.PlotlyJSONEncoder)
        
        return render_template(
            'ai_insights.html',
            title='AI Insights',
            insights=insights,
            recommendations=recommendations,
            sustainability_score=sustainability_score,
            time_chart=time_chart_json,
            category_chart=category_chart_json,
            score_chart=score_chart_json,
            trend_chart=trend_chart_json
        )
    except Exception as e:
        flash(f'Error generating AI insights: {e}', 'danger')
        print(f"Error in AI insights: {e}")
        import traceback
        print(traceback.format_exc())
        return redirect(url_for('index'))


def generate_chat_response(message, total_emissions, category_breakdown):
    """
    Generate a contextual response to the user's chat message
    based on their emissions data and the query content.
    
    Args:
        message (str): User's message
        total_emissions (float): Total user emissions in kg CO2e
        category_breakdown (dict): Emissions by category
        
    Returns:
        str: AI response message
    """
    message = message.lower()
    
    # Greeting patterns
    if any(greeting in message for greeting in ['hello', 'hi', 'hey', 'greetings']):
        return f"Hello! I'm Ppang, your sustainability assistant. How can I help you understand your carbon footprint today?"
    
    # Questions about total emissions
    if any(term in message for term in ['total emissions', 'carbon footprint', 'my footprint', 'my emissions']):
        if total_emissions > 0:
            if total_emissions > 100:
                return f"Your total carbon footprint is {total_emissions} kg CO2e. This is above average. The main contributor is {max(category_breakdown, key=category_breakdown.get)} at {category_breakdown[max(category_breakdown, key=category_breakdown.get)]} kg."
            else:
                return f"Your total carbon footprint is {total_emissions} kg CO2e. This is relatively low compared to average. Great job! The main contributor is still {max(category_breakdown, key=category_breakdown.get)} at {category_breakdown[max(category_breakdown, key=category_breakdown.get)]} kg."
        else:
            return "You haven't recorded any emissions data yet. Start by tracking your transport, energy, food, or waste activities to see your carbon footprint."
    
    # Questions about specific categories
    for category in ['transport', 'energy', 'food', 'waste']:
        if category in message:
            category_title = category.title()
            if category_title in category_breakdown and category_breakdown[category_title] > 0:
                percentage = round((category_breakdown[category_title] / total_emissions * 100), 1)
                
                # Category-specific advice
                if category == 'transport':
                    return f"Your {category} emissions are {category_breakdown[category_title]} kg CO2e ({percentage}% of your total). Consider carpooling, using public transport, or walking/cycling for short trips to reduce this."
                elif category == 'energy':
                    return f"Your {category} emissions are {category_breakdown[category_title]} kg CO2e ({percentage}% of your total). You can reduce this by using energy-efficient appliances, turning off lights when not in use, and switching to renewable energy sources."
                elif category == 'food':
                    return f"Your {category} emissions are {category_breakdown[category_title]} kg CO2e ({percentage}% of your total). Reducing meat consumption, especially beef, and buying local, seasonal produce can help lower this significantly."
                elif category == 'waste':
                    return f"Your {category} emissions are {category_breakdown[category_title]} kg CO2e ({percentage}% of your total). Focus on reducing, reusing and recycling. Composting food waste also helps reduce methane emissions from landfills."
            else:
                return f"You haven't recorded any {category} emissions yet. Would you like to know how to track them?"
    
    # Questions about how to reduce footprint
    if any(term in message for term in ['reduce', 'lower', 'decrease', 'cut', 'minimize']):
        if 'footprint' in message or 'emissions' in message or 'carbon' in message:
            if total_emissions > 0:
                highest_category = max(category_breakdown, key=category_breakdown.get)
                return f"To reduce your carbon footprint, focus first on your highest emission category: {highest_category} ({category_breakdown[highest_category]} kg). Some effective ways to reduce this include: " + get_category_tips(highest_category)
            else:
                return "To reduce your carbon footprint, start by tracking your emissions across transport, energy, food, and waste. Once you have data, I can provide personalized recommendations."
    
    # Questions about the app or how to use it
    if any(term in message for term in ['how to use', 'how do i', 'how does this work', 'help me', 'instructions']):
        return "To use Ppang, start by tracking your daily activities in the 'Track Emissions' section. Add your transport, energy use, food consumption, and waste data. The dashboard will show your carbon footprint breakdown, and you'll get personalized recommendations to reduce your impact."
    
    # General sustainability questions
    if any(term in message for term in ['sustainable', 'eco-friendly', 'green', 'environmental']):
        return "Living sustainably means making choices that reduce your environmental impact. This includes reducing energy use, choosing low-carbon transportation, eating a plant-rich diet, minimizing waste, and supporting environmentally responsible companies. Small daily changes can add up to a significant positive impact."
    
    # Fallback response
    return "I'm here to help you understand and reduce your carbon footprint. You can ask me about your emissions, specific categories like transport or food, or how to live more sustainably. What would you like to know more about?"


def get_category_tips(category):
    """Get specific tips for reducing emissions in a category"""
    tips = {
        'Transport': "use public transportation, carpool, bike or walk for short trips, combine errands to reduce trips, and consider an electric vehicle for your next car purchase.",
        'Energy': "switch to LED bulbs, unplug devices when not in use, use a programmable thermostat, wash clothes in cold water, and consider switching to renewable energy providers.",
        'Food': "reduce beef consumption, eat more plant-based meals, buy local and seasonal produce, reduce food waste by planning meals, and compost food scraps.",
        'Waste': "practice the 4 Rs: refuse, reduce, reuse, recycle. Compost organic waste, avoid single-use plastics, and repair items instead of replacing them when possible."
    }
    return tips.get(category, "make small, consistent changes in your daily habits and be mindful of your consumption patterns.")


# Error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Error handler for 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
    app.run(host="0.0.0.0", port=5001, debug=True)
