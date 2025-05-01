import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_emissions_over_time(emission_data, title="Carbon Emissions Over Time"):
    """
    Create a line chart of emissions over time.
    
    Args:
        emission_data (DataFrame): Emissions data with date and emission_kg columns
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    if emission_data.empty:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No emission data available",
            xaxis_title="Date",
            yaxis_title="Emissions (kg CO2e)"
        )
        return fig
    
    # Prepare data
    df = emission_data.copy()
    
    # Convert date to datetime if not already
    if not pd.api.types.is_datetime64_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # Group by date and sum emissions
    daily_emissions = df.groupby('date')['emission_kg'].sum().reset_index()
    
    # Sort by date
    daily_emissions = daily_emissions.sort_values('date')
    
    # Calculate cumulative emissions
    daily_emissions['cumulative_emissions'] = daily_emissions['emission_kg'].cumsum()
    
    # Create subplots: daily emissions only (removing cumulative for clarity)
    fig = go.Figure()
    
    # Add daily emissions bar chart with improved styling
    fig.add_trace(
        go.Bar(
            x=daily_emissions['date'],
            y=daily_emissions['emission_kg'],
            name="Daily Emissions",
            marker_color='#2E86C1',
            hovertemplate="Date: %{x}<br>Emissions: %{y:.1f} kg CO2e<extra></extra>"
        )
    )
    
    # Calculate moving average for trend line
    window = min(7, len(daily_emissions))
    daily_emissions['moving_avg'] = daily_emissions['emission_kg'].rolling(window=window).mean()
    
    # Add trend line
    fig.add_trace(
        go.Scatter(
            x=daily_emissions['date'],
            y=daily_emissions['moving_avg'],
            name=f"{window}-Day Average",
            line=dict(color='#E74C3C', width=2),
            hovertemplate="Date: %{x}<br>Average: %{y:.1f} kg CO2e<extra></extra>"
        )
    )
    
    # Set titles and layout
    fig.update_layout(
        title={
            'text': title,
            'font': dict(size=20)
        },
        xaxis_title="Date",
        yaxis_title="Daily Emissions (kg CO2e)",
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=50, l=50, r=50, b=50)
    )
    
    # Improve axis formatting
    fig.update_xaxes(
        tickformat="%Y-%m-%d",
        tickangle=45,
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(211,211,211,0.3)'
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(211,211,211,0.3)',
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor='rgba(211,211,211,0.5)'
    )
    
    return fig

def plot_emissions_by_category(emission_data, title="Emissions by Category"):
    """
    Create a pie chart of emissions by category.
    
    Args:
        emission_data (DataFrame): Emissions data with category and emission_kg columns
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    if emission_data.empty:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(title="No emission data available")
        return fig
    
    # Group by category and sum emissions
    category_emissions = emission_data.groupby('category')['emission_kg'].sum().reset_index()
    
    # Calculate percentage for each category
    total_emissions = category_emissions['emission_kg'].sum()
    category_emissions['percentage'] = (category_emissions['emission_kg'] / total_emissions * 100).round(1)
    
    # For debugging - print the actual values
    print("Emission by Category Data:")
    for _, row in category_emissions.iterrows():
        print(f"{row['category']}: {row['emission_kg']} kg CO2e ({row['percentage']}%)")
    
    # Sort by emission value (highest first) to make the chart consistent
    category_emissions = category_emissions.sort_values('emission_kg', ascending=False)
    
    # Custom colors for better visibility
    custom_colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#E91E63', '#F44336']
    
    # Create pie chart with simple labels and clean look
    fig = go.Figure(data=[go.Pie(
        labels=[row['category'] for _, row in category_emissions.iterrows()],
        values=category_emissions['emission_kg'].tolist(),
        hole=0.4,
        textinfo='label+percent',
        marker=dict(colors=custom_colors[:len(category_emissions)]),
        pull=[0.05 if i == 0 else 0 for i in range(len(category_emissions))],  # Pull out the largest segment
        textposition='inside',
        textfont=dict(size=14, color='white'),
        insidetextorientation='horizontal'
    )])
    
    # Add a cleaner title and remove unnecessary elements
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=18)
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=80, b=80, l=20, r=20),
        annotations=[dict(
            text=f"Total: {total_emissions:.1f} kg CO₂e",
            x=0.5, y=0.5,
            font=dict(size=14),
            showarrow=False
        )]
    )
    
    return fig

def plot_waste_composition(waste_data):
    """
    Create a pie chart of waste by type.
    
    Args:
        waste_data (DataFrame): Waste data with waste_type and weight_kg columns
        
    Returns:
        Figure: Plotly figure object
    """
    if waste_data.empty:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(title="No waste data available")
        return fig
    
    # Group by waste type and sum weights
    waste_composition = waste_data.groupby('waste_type')['weight_kg'].sum().reset_index()
    
    # Calculate percentage for each waste type
    total_waste = waste_composition['weight_kg'].sum()
    waste_composition['percentage'] = (waste_composition['weight_kg'] / total_waste * 100).round(1)
    
    # For debugging - print the actual values
    print("Waste Composition Data:")
    for _, row in waste_composition.iterrows():
        print(f"{row['waste_type']}: {row['weight_kg']} kg ({row['percentage']}%)")
    
    # Sort by weight (highest first) to make the chart consistent
    waste_composition = waste_composition.sort_values('weight_kg', ascending=False)
    
    # Custom colors for better visibility
    custom_colors = ['#795548', '#FFC107', '#607D8B', '#8BC34A', '#03A9F4', '#673AB7']
    
    # Create pie chart with simple labels and clean look
    fig = go.Figure(data=[go.Pie(
        labels=[row['waste_type'] for _, row in waste_composition.iterrows()],
        values=waste_composition['weight_kg'].tolist(),
        hole=0.4,
        textinfo='label+percent',
        marker=dict(colors=custom_colors[:len(waste_composition)]),
        pull=[0.05 if i == 0 else 0 for i in range(len(waste_composition))],
        textposition='inside',
        textfont=dict(size=14, color='white'),
        insidetextorientation='horizontal'
    )])
    
    # Add a cleaner title and layout
    fig.update_layout(
        title={
            'text': 'Waste Composition',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=18)
        },
        margin=dict(t=80, b=80, l=20, r=20),
        annotations=[dict(
            text=f"Total: {total_waste:.1f} kg",
            x=0.5, y=0.5,
            font=dict(size=14),
            showarrow=False
        )]
    )
    
    return fig

def create_footprint_comparison(total_emissions):
    """
    Create a bar chart comparing user's footprint to average.
    
    Args:
        total_emissions (float): User's total emissions in kg CO2e
        
    Returns:
        Figure: Plotly figure object
    """
    # Average annual per capita emissions in kg CO2e
    # Source: World Bank data (approximate)
    averages = {
        'World': 4800,
        'USA': 16500,
        'EU': 8600,
        'China': 7500,
        'India': 1900,
        'You': total_emissions
    }
    
    # Create comparison data
    comparison_df = pd.DataFrame({
        'Entity': list(averages.keys()),
        'Annual Emissions (kg CO2e)': list(averages.values())
    })
    
    # Create bar chart
    fig = px.bar(
        comparison_df,
        x='Entity',
        y='Annual Emissions (kg CO2e)',
        title='Your Annual Carbon Footprint Compared to Global Averages',
        color='Entity',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Highlight user's bar
    fig.update_traces(
        marker_color=['#1f77b4', '#1f77b4', '#1f77b4', '#1f77b4', '#1f77b4', '#ff7f0e'],
        marker_line_color=['#1f77b4', '#1f77b4', '#1f77b4', '#1f77b4', '#1f77b4', 'red'],
        marker_line_width=[1, 1, 1, 1, 1, 3]
    )
    
    # Improve layout
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Annual Emissions (kg CO2e)",
        showlegend=False
    )
    
    return fig

def plot_emissions_breakdown(emission_data, category=None):
    """
    Create a treemap of emissions breakdown by category and subcategory.
    
    Args:
        emission_data (DataFrame): Emissions data
        category (str, optional): Filter by specific category
        
    Returns:
        Figure: Plotly figure object
    """
    if emission_data.empty:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(title="No emission data available")
        return fig
    
    # Filter by category if specified
    df = emission_data.copy()
    if category:
        df = df[df['category'] == category]
    
    # Create treemap
    fig = px.treemap(
        df,
        path=['category', 'subcategory'],
        values='emission_kg',
        title=f'Emissions Breakdown{"" if not category else f" for {category}"}',
        color='emission_kg',
        color_continuous_scale='Viridis'
    )
    
    # Improve layout
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    
    return fig

def plot_emission_trends(emission_data):
    """
    Create a line chart with trend line of emissions over time.
    
    Args:
        emission_data (DataFrame): Emissions data with date and emission_kg columns
        
    Returns:
        Figure: Plotly figure object
    """
    import plotly.graph_objects as go
    import numpy as np
    
    if emission_data.empty or len(emission_data) < 3:
        # Return empty figure if not enough data
        fig = go.Figure()
        fig.update_layout(
            title="Not enough data for trend analysis",
            xaxis_title="Date",
            yaxis_title="Emissions (kg CO2e)"
        )
        return fig
        
    # Prepare data
    df = emission_data.copy()
    df['date'] = pd.to_datetime(df['date'])
    daily_emissions = df.groupby('date')['emission_kg'].sum().reset_index()
    daily_emissions = daily_emissions.sort_values('date')
    
    # Create figure
    fig = go.Figure()
    
    # Add daily emissions
    fig.add_trace(go.Scatter(
        x=daily_emissions['date'],
        y=daily_emissions['emission_kg'],
        mode='lines+markers',
        name='Daily Emissions',
        line=dict(color='#2E86C1', width=2)
    ))
    
    # Add trend line
    x_numeric = np.arange(len(daily_emissions))
    z = np.polyfit(x_numeric, daily_emissions['emission_kg'], 1)
    p = np.poly1d(z)
    
    fig.add_trace(go.Scatter(
        x=daily_emissions['date'],
        y=p(x_numeric),
        mode='lines',
        name='Trend',
        line=dict(color='#E74C3C', dash='dash')
    ))
    
    # Update layout
    fig.update_layout(
        title='Emission Trends Over Time',
        xaxis_title='Date',
        yaxis_title='Emissions (kg CO2e)',
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig
    
    # Prepare data
    df = emission_data.copy()
    
    # Convert date to datetime if not already
    if not pd.api.types.is_datetime64_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # Group by date and sum emissions
    daily_emissions = df.groupby('date')['emission_kg'].sum().reset_index()
    
    # Sort by date
    daily_emissions = daily_emissions.sort_values('date')
    
    # Simple moving average
    window_size = min(7, len(daily_emissions))
    daily_emissions['moving_avg'] = daily_emissions['emission_kg'].rolling(window=window_size, min_periods=1).mean()
    
    # Create figure
    fig = go.Figure()
    
    # Add daily emissions scatter plot
    fig.add_trace(
        go.Scatter(
            x=daily_emissions['date'],
            y=daily_emissions['emission_kg'],
            mode='markers',
            name="Daily Emissions",
            marker=dict(
                size=8,
                color='rgb(55, 83, 109)',
                opacity=0.7
            )
        )
    )
    
    # Add moving average line
    fig.add_trace(
        go.Scatter(
            x=daily_emissions['date'],
            y=daily_emissions['moving_avg'],
            mode='lines',
            name=f"{window_size}-Day Moving Average",
            line=dict(
                color='red',
                width=2
            )
        )
    )
    
    # Set titles and layout
    fig.update_layout(
        title="Carbon Emission Trends",
        xaxis_title="Date",
        yaxis_title="Emissions (kg CO2e)",
        hovermode="x unified"
    )
    
    return fig

def plot_monthly_comparison(emission_data):
    """
    Create a bar chart comparing emissions by month.
    
    Args:
        emission_data (DataFrame): Emissions data with date and emission_kg columns
        
    Returns:
        Figure: Plotly figure object
    """
    if emission_data.empty:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No emission data available",
            xaxis_title="Month",
            yaxis_title="Emissions (kg CO2e)"
        )
        return fig
    
    # Prepare data
    df = emission_data.copy()
    
    # Convert date to datetime if not already
    if not pd.api.types.is_datetime64_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # Extract month and year
    df['month_year'] = df['date'].dt.strftime('%Y-%m')
    df['month'] = df['date'].dt.strftime('%b')
    df['year'] = df['date'].dt.year
    
    # Group by month-year and sum emissions
    monthly_emissions = df.groupby(['month_year', 'month', 'year'])['emission_kg'].sum().reset_index()
    
    # Sort by date
    monthly_emissions = monthly_emissions.sort_values(['year', 'month_year'])
    
    # Create bar chart
    fig = px.bar(
        monthly_emissions,
        x='month',
        y='emission_kg',
        color='year',
        title='Monthly Emissions Comparison',
        labels={'emission_kg': 'Emissions (kg CO2e)', 'month': 'Month'},
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    
    # Improve layout
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Emissions (kg CO2e)",
        hovermode="x unified",
        xaxis={'categoryorder':'array', 'categoryarray':['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']}
    )
    
    return fig
