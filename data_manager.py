import pandas as pd
import json
import os
import io
from datetime import datetime

# Define functions to save and load data
def save_data(df, data_type):
    """
    Save a DataFrame to a JSON format for persistence.
    
    Args:
        df (DataFrame): The data to save
        data_type (str): Type of data ('emissions' or 'waste')
    """
    # Convert to JSON and store in memory
    json_data = df.to_json(orient='records', date_format='iso')
    
    # Here we'd typically save to a file, but for this application we'll store in session state
    # The actual save operation would be:
    # with open(f"{data_type}_data.json", "w") as f:
    #     f.write(json_data)
    
    return True

def load_data(data_type):
    """
    Load data from JSON format.
    
    Args:
        data_type (str): Type of data ('emissions' or 'waste')
        
    Returns:
        DataFrame: The loaded data
    """
    # Here we'd typically load from a file, but for this application we'll check session state
    # The actual load operation would be:
    # try:
    #     with open(f"{data_type}_data.json", "r") as f:
    #         json_data = f.read()
    #     return pd.read_json(json_data, orient='records')
    # except (FileNotFoundError, ValueError):
    #     # Return empty DataFrame if file doesn't exist or is invalid
    #     if data_type == 'emissions':
    #         return pd.DataFrame({
    #             'date': [], 'category': [], 'subcategory': [], 
    #             'amount': [], 'unit': [], 'emission_kg': []
    #         })
    #     else:  # waste
    #         return pd.DataFrame({
    #             'date': [], 'waste_type': [], 'weight_kg': [], 
    #             'disposal_method': [], 'emission_kg': []
    #         })
    
    # For now, raise error to trigger initialization in app.py
    raise FileNotFoundError("No saved data found")

def get_emissions_data():
    """
    Get all emissions data.
    
    Returns:
        DataFrame: All emission records
    """
    try:
        return load_data('emissions')
    except:
        return pd.DataFrame({
            'date': [], 'category': [], 'subcategory': [], 
            'amount': [], 'unit': [], 'emission_kg': []
        })

def get_waste_data():
    """
    Get all waste data.
    
    Returns:
        DataFrame: All waste records
    """
    try:
        return load_data('waste')
    except:
        return pd.DataFrame({
            'date': [], 'waste_type': [], 'weight_kg': [], 
            'disposal_method': [], 'emission_kg': []
        })

def add_emission_entry(df, date, category, subcategory, amount, unit, emission_kg):
    """
    Add a new emission entry to the data.
    
    Args:
        df (DataFrame): Current emissions DataFrame
        date (str): Date of the emission
        category (str): Emission category
        subcategory (str): Emission subcategory
        amount (float): Amount of activity
        unit (str): Unit of measurement
        emission_kg (float): Calculated emissions in kg CO2e
        
    Returns:
        DataFrame: Updated emissions DataFrame
    """
    new_entry = pd.DataFrame({
        'date': [date],
        'category': [category],
        'subcategory': [subcategory],
        'amount': [amount],
        'unit': [unit],
        'emission_kg': [emission_kg]
    })
    
    # Append the new entry
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    
    return updated_df

def add_waste_entry(df, date, waste_type, weight_kg, disposal_method, emission_kg):
    """
    Add a new waste entry to the data.
    
    Args:
        df (DataFrame): Current waste DataFrame
        date (str): Date of the waste generation
        waste_type (str): Type of waste
        weight_kg (float): Weight in kg
        disposal_method (str): Method of disposal
        emission_kg (float): Calculated emissions in kg CO2e
        
    Returns:
        DataFrame: Updated waste DataFrame
    """
    new_entry = pd.DataFrame({
        'date': [date],
        'waste_type': [waste_type],
        'weight_kg': [weight_kg],
        'disposal_method': [disposal_method],
        'emission_kg': [emission_kg]
    })
    
    # Append the new entry
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    
    return updated_df

def get_filtered_data(df, start_date=None, end_date=None, category=None):
    """
    Filter data based on date range and/or category.
    
    Args:
        df (DataFrame): Data to filter
        start_date (str, optional): Start date for filtering
        end_date (str, optional): End date for filtering
        category (str, optional): Category to filter by
        
    Returns:
        DataFrame: Filtered data
    """
    filtered_df = df.copy()
    
    # Convert date column to datetime if it's not already
    if 'date' in filtered_df.columns and not pd.api.types.is_datetime64_dtype(filtered_df['date']):
        filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    
    # Apply date filters
    if start_date:
        start_date = pd.to_datetime(start_date)
        filtered_df = filtered_df[filtered_df['date'] >= start_date]
    
    if end_date:
        end_date = pd.to_datetime(end_date)
        filtered_df = filtered_df[filtered_df['date'] <= end_date]
    
    # Apply category filter
    if category and 'category' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['category'] == category]
    
    return filtered_df

def get_aggregated_data(df, group_by, agg_column, agg_func='sum'):
    """
    Aggregate data by a specific column.
    
    Args:
        df (DataFrame): Data to aggregate
        group_by (str): Column to group by
        agg_column (str): Column to aggregate
        agg_func (str): Aggregation function ('sum', 'mean', etc.)
        
    Returns:
        DataFrame: Aggregated data
    """
    if df.empty or group_by not in df.columns or agg_column not in df.columns:
        return pd.DataFrame()
    
    # Perform aggregation
    agg_df = df.groupby(group_by)[agg_column].agg(agg_func).reset_index()
    
    return agg_df

def export_data_csv(df):
    """
    Export data to CSV format.
    
    Args:
        df (DataFrame): Data to export
        
    Returns:
        str: CSV data as string
    """
    if df.empty:
        return ""
    
    # Use StringIO to capture CSV output
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    return csv_data

def import_data_csv(csv_data, data_type):
    """
    Import data from CSV format.
    
    Args:
        csv_data (str): CSV data to import
        data_type (str): Type of data ('emissions' or 'waste')
        
    Returns:
        DataFrame: Imported data
    """
    try:
        # Read CSV into DataFrame
        df = pd.read_csv(io.StringIO(csv_data))
        
        # Validate expected columns based on data type
        if data_type == 'emissions':
            required_cols = ['date', 'category', 'subcategory', 'amount', 'unit', 'emission_kg']
        else:  # waste
            required_cols = ['date', 'waste_type', 'weight_kg', 'disposal_method', 'emission_kg']
        
        # Check if all required columns are present
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return df
    except Exception as e:
        raise ValueError(f"Error importing data: {str(e)}")
