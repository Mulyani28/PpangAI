import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def train_prediction_model(daily_emissions_df):
    """
    Train a machine learning model to predict future emissions based on historical data.
    
    Args:
        daily_emissions_df (DataFrame): Daily emissions data with date and emission_kg columns
                                      and features like day_of_week, month, day
    
    Returns:
        model: Trained prediction model
    """
    if len(daily_emissions_df) < 5:
        # Not enough data for meaningful training
        # Return a simple model that predicts based on day of week
        model = LinearRegression()
        X = np.array(daily_emissions_df['day_of_week']).reshape(-1, 1)
        y = daily_emissions_df['emission_kg']
        model.fit(X, y)
        return model
    
    # Features for training
    X = daily_emissions_df[['day_of_week', 'month', 'day']]
    y = daily_emissions_df['emission_kg']
    
    # If we have enough data, split into train/test
    if len(daily_emissions_df) >= 10:
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train a Random Forest model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate the model
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # If the model performs poorly, fall back to a simpler model
            if r2 < 0.1:  # Very poor fit
                model = LinearRegression()
                model.fit(X_train, y_train)
        except Exception as e:
            # If there's any error in model training, fall back to simple model
            print(f"Error in training complex model: {e}. Using simple model instead.")
            model = LinearRegression()
            model.fit(X[['day_of_week']], y)  # Use only day_of_week for simple model
    else:
        # Not enough data for split, use all data with a simpler model
        try:
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X, y)
        except Exception as e:
            # If there's any error, use an even simpler linear model
            print(f"Error in training model: {e}. Using linear model instead.")
            model = LinearRegression()
            model.fit(X[['day_of_week']], y)  # Use only day_of_week for simple model
    
    return model

def predict_future_emissions(model, future_dates):
    """
    Predict future emissions based on trained model and future dates.
    
    Args:
        model: Trained prediction model
        future_dates: DatetimeIndex of future dates to predict
    
    Returns:
        list: Predicted emissions for each date
    """
    # Create features for prediction
    future_features = pd.DataFrame({
        'date': future_dates,
        'day_of_week': future_dates.dayofweek,
        'month': future_dates.month,
        'day': future_dates.day
    })
    
    # Make predictions
    # Check model type to handle both simple and complex models
    if isinstance(model, LinearRegression) and model.coef_.shape[0] == 1:
        # Simple model expects only day_of_week
        X_future = future_features[['day_of_week']]
    else:
        # Complex model expects all features
        X_future = future_features[['day_of_week', 'month', 'day']]
    
    predictions = model.predict(X_future)
    
    # Ensure no negative predictions
    predictions = np.maximum(predictions, 0)
    
    return predictions

def train_waste_prediction_model(waste_data):
    """
    Train a machine learning model to predict waste generation.
    
    Args:
        waste_data (DataFrame): Historical waste data
        
    Returns:
        model: Trained prediction model
    """
    if len(waste_data) < 5:
        # Not enough data, create a simple model that returns average
        model = LinearRegression()
        # Create dummy data with single feature for minimal model
        X = np.array([0, 1, 2, 3, 4]).reshape(-1, 1)
        avg_weight = waste_data['weight_kg'].mean() if not waste_data.empty else 0
        y = np.ones(5) * avg_weight
        model.fit(X, y)
        return model
    
    # Convert date to datetime
    waste_data = waste_data.copy()
    waste_data['date'] = pd.to_datetime(waste_data['date'])
    
    # Group by date and calculate total waste
    daily_waste = waste_data.groupby('date')['weight_kg'].sum().reset_index()
    
    # Add time-based features
    daily_waste['day_of_week'] = daily_waste['date'].dt.dayofweek
    daily_waste['month'] = daily_waste['date'].dt.month
    daily_waste['day'] = daily_waste['date'].dt.day
    
    # Features and target
    X = daily_waste[['day_of_week', 'month', 'day']]
    y = daily_waste['weight_kg']
    
    try:
        # Train model (using RandomForest for robustness with small datasets)
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X, y)
    except Exception as e:
        # If there's any error, fall back to a simple linear model
        print(f"Error training waste prediction model: {e}. Using simple model.")
        model = LinearRegression()
        X_simple = daily_waste[['day_of_week']]
        model.fit(X_simple, y)
    
    return model

def detect_emission_anomalies(emission_data, window_size=7):
    """
    Detect anomalies in emission data using a rolling window approach.
    
    Args:
        emission_data (DataFrame): Emission data with date and emission_kg columns
        window_size (int): Size of the rolling window for anomaly detection
        
    Returns:
        DataFrame: Data with anomaly flags
    """
    if len(emission_data) < window_size * 2:
        # Not enough data for meaningful anomaly detection
        return pd.DataFrame()
    
    # Prepare data
    df = emission_data.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Group by date
    daily_emissions = df.groupby('date')['emission_kg'].sum().reset_index()
    daily_emissions = daily_emissions.sort_values('date')
    
    # Calculate rolling statistics
    daily_emissions['rolling_mean'] = daily_emissions['emission_kg'].rolling(window=window_size, min_periods=2).mean()
    daily_emissions['rolling_std'] = daily_emissions['emission_kg'].rolling(window=window_size, min_periods=2).std()
    
    # Calculate z-scores
    daily_emissions['z_score'] = np.nan
    mask = daily_emissions['rolling_std'] > 0  # Avoid division by zero
    daily_emissions.loc[mask, 'z_score'] = (
        (daily_emissions.loc[mask, 'emission_kg'] - daily_emissions.loc[mask, 'rolling_mean']) /
        daily_emissions.loc[mask, 'rolling_std']
    )
    
    # Flag anomalies (z-score > 2)
    daily_emissions['is_anomaly'] = abs(daily_emissions['z_score']) > 2
    
    return daily_emissions[['date', 'emission_kg', 'z_score', 'is_anomaly']]

def analyze_emission_patterns(emission_data):
    """
    Analyze patterns in emission data to find insights.
    
    Args:
        emission_data (DataFrame): Emission data
        
    Returns:
        dict: Dictionary containing insights
    """
    if emission_data.empty:
        return {}
    
    insights = {}
    
    # Convert date to datetime
    df = emission_data.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Add day of week
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_name'] = df['date'].dt.day_name()
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.month_name()
    
    # Analyze by day of week
    day_emissions = df.groupby('day_name')['emission_kg'].agg(['sum', 'mean']).reset_index()
    if not day_emissions.empty:
        highest_day = day_emissions.sort_values('sum', ascending=False).iloc[0]
        insights['highest_emission_day'] = highest_day['day_name']
        insights['highest_day_avg'] = highest_day['mean']
    
    # Analyze by month
    month_emissions = df.groupby('month_name')['emission_kg'].agg(['sum', 'mean']).reset_index()
    if not month_emissions.empty:
        highest_month = month_emissions.sort_values('sum', ascending=False).iloc[0]
        insights['highest_emission_month'] = highest_month['month_name']
        insights['highest_month_avg'] = highest_month['mean']
    
    # Analyze by category
    category_emissions = df.groupby('category')['emission_kg'].agg(['sum', 'mean']).reset_index()
    if not category_emissions.empty:
        highest_category = category_emissions.sort_values('sum', ascending=False).iloc[0]
        insights['highest_emission_category'] = highest_category['category']
        insights['highest_category_total'] = highest_category['sum']
    
    # Time trend analysis - is it getting better or worse?
    if len(df) >= 5:
        df = df.sort_values('date')
        df['cumulative_avg'] = df['emission_kg'].expanding().mean()
        first_half = df.iloc[:len(df)//2]['emission_kg'].mean()
        second_half = df.iloc[len(df)//2:]['emission_kg'].mean()
        
        insights['trend'] = 'improving' if second_half < first_half else 'worsening'
        insights['trend_change_percent'] = abs((second_half - first_half) / first_half * 100)
    
    return insights
