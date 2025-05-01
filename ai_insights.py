"""
AI-powered analysis and insights module for Ppang Carbon Footprint Tracker.
Uses both ML models for sustainability insights.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor 
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import plotly.utils

def analyze_emission_patterns(emission_data):
    """
    Analyze emission patterns using AI and ML techniques.
    """
    try:
        if emission_data.empty:
            return {
                "insights": ["Start tracking your emissions to see AI-powered insights."],
                "emission_details": {"total": 0, "daily_average": 0, "categories": 0},
                "trend_analysis": None,
                "peak_analysis": None,
                "category_insights": None,
                "strengths": ["AI tracking enabled"],
                "areas_for_improvement": ["Add data to get personalized insights"]
            }

        # Convert date to datetime
        df = emission_data.copy()
        df['date'] = pd.to_datetime(df['date'])

        # Calculate daily emissions for trend analysis
        daily_emissions = df.groupby('date')['emission_kg'].sum().reset_index()
        daily_emissions = daily_emissions.sort_values('date')

        # Calculate trend
        x = np.arange(len(daily_emissions))
        y = daily_emissions['emission_kg'].values
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        trend_direction = "decreasing" if z[0] < 0 else "increasing"
        trend_percentage = abs((y[-1] - y[0]) / y[0] * 100) if len(y) > 1 else 0

        # Calculate detailed statistics
        total_emissions = df['emission_kg'].sum()
        daily_avg = total_emissions / len(df['date'].unique())
        categories = df.groupby('category')['emission_kg'].sum()

        # Trend Analysis

        df['month_year'] = df['date'].dt.to_period('M')
        monthly_trends = df.groupby('month_year')['emission_kg'].sum()


        # Category Analysis
        category_insights = {}
        for category, value in categories.items():
            percentage = (value / total_emissions) * 100
            subcategory_data = df[df['category'] == category].groupby('subcategory')['emission_kg'].sum()
            top_subcategory = subcategory_data.idxmax() if not subcategory_data.empty else "N/A"
            category_insights[category] = {
                "total": float(value),
                "percentage": float(percentage),
                "top_subcategory": top_subcategory,
                "top_subcategory_amount": float(subcategory_data.max())
            }

        # Generate insights based on actual data
        insights = []
        if len(monthly_trends) > 1:
            insights.append(f"Your emissions have {'decreased' if trend_direction == 'decreasing' else 'increased'} by {trend_percentage:.1f}% over time")

        highest_category = categories.idxmax()
        insights.append(f"Your highest emission source is {highest_category} at {categories[highest_category]:.1f} kg CO2e")

        # Generate strengths based on data
        strengths = []
        if len(df) >= 5:
            tracking_days = (df['date'].max() - df['date'].min()).days
            strengths.append(f"Regular tracking for {tracking_days} days")

        if len(categories) >= 3:
            strengths.append(f"Comprehensive tracking across {len(categories)} categories")

        if trend_direction == "decreasing":
            strengths.append("Showing overall emission reduction trend")

        # Generate improvement areas based on data
        improvements = []
        for category, data in category_insights.items():
            if data['percentage'] > 30:
                improvements.append(f"Focus on reducing {category} emissions ({data['percentage']:.1f}% of total)")
                improvements.append(f"Consider alternatives to {data['top_subcategory']} in {category} category")

        # Create trend chart
        trend_fig = go.Figure()

        # Add daily emissions with improved visibility
        trend_fig.add_trace(go.Scatter(
            x=daily_emissions['date'],
            y=daily_emissions['emission_kg'],
            mode='lines+markers',
            name='Daily Emissions',
            line=dict(color='#2E86C1', width=2),
            marker=dict(size=8)
        ))

        # Add trend line with improved visibility
        trend_fig.add_trace(go.Scatter(
            x=daily_emissions['date'],
            y=p(x),
            mode='lines',
            name='Trend',
            line=dict(color='#E74C3C', width=3, dash='dash')
        ))

        # Enhanced layout
        trend_fig.update_layout(
            title={
                'text': 'Emission Trends Over Time',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=20)
            },
            xaxis_title='Date',
            yaxis_title='Emissions (kg CO2e)',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.8)'
            ),
            height=500,
            margin=dict(t=60, b=50, l=50, r=25),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='x unified'
        )

        # Add grid lines for better readability
        trend_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(211,211,211,0.4)')
        trend_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(211,211,211,0.4)')

        trend_chart_json = json.dumps(trend_fig, cls=plotly.utils.PlotlyJSONEncoder)

        return {
            "insights": insights,
            "emission_details": {
                "total": float(total_emissions),
                "daily_average": float(daily_avg),
                "categories": len(categories)
            },
            "trend_analysis": {
                "direction": trend_direction,
                "percentage": float(trend_percentage),
                "monthly_data": {str(k): float(v) for k, v in monthly_trends.items()}
            },
            "trend_chart": trend_chart_json, #added trend chart
            "category_insights": category_insights,
            "strengths": strengths,
            "areas_for_improvement": improvements
        }

    except Exception as e:
        print(f"Error in emission pattern analysis: {str(e)}")
        return {
            "insights": ["AI analysis enabled"],
            "emission_details": {"total": 0, "daily_average": 0, "categories": 0},
            "trend_analysis": None,
            "peak_analysis": None,
            "category_insights": None,
            "strengths": ["AI tracking enabled"],
            "areas_for_improvement": ["Add more data for detailed AI analysis"]
        }

def generate_personalized_recommendations(emissions_df, user_profile=None):
    """Generate AI-powered personalized recommendations based on actual user data."""
    try:
        if emissions_df.empty:
            return [{
                "title": "Start Your Sustainability Journey",
                "description": "Begin tracking your emissions to get personalized recommendations",
                "impact": "high",
                "category": "general"
            }]

        recommendations = []
        df = emissions_df.copy()
        categories = df.groupby('category')['emission_kg'].sum()
        highest_category = categories.idxmax()

        # Add category-specific recommendations
        recommendations.append({
            "title": f"Focus on {highest_category}",
            "description": f"Your highest emissions come from {highest_category}. Consider alternatives or reduction strategies.",
            "impact": "high",
            "category": highest_category
        })

        if len(df) >= 5:
            daily_emissions = df.groupby('date')['emission_kg'].sum()
            high_emission_days = daily_emissions[daily_emissions > daily_emissions.mean()]

            if not high_emission_days.empty:
                recommendations.append({
                    "title": "Optimize High-Emission Days",
                    "description": f"Consider reducing activities on {high_emission_days.index[0].strftime('%A')}s when emissions are highest",
                    "impact": "medium",
                    "category": "timing"
                })

        return recommendations

    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return [{
            "title": "AI-Powered Recommendations",
            "description": "Add more emission data to get personalized suggestions",
            "impact": "high",
            "category": "general"
        }]

def analyze_sustainability_score(emissions_df, waste_df=None):
    """
    Calculate AI-powered sustainability score with detailed insights.
    """
    try:
        if emissions_df.empty:
            return {
                "score": 0,
                "rating": "Not enough data",
                "strengths": [],
                "areas_for_improvement": [],
                "comparison_to_average": "Insufficient data for AI comparison"
            }

        # Calculate metrics
        total_emissions = emissions_df['emission_kg'].sum()
        daily_avg = total_emissions / len(emissions_df['date'].unique())
        categories = emissions_df.groupby('category')['emission_kg'].sum()

        # Use ML for scoring
        df = emissions_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month

        # Train model for pattern recognition
        X = pd.get_dummies(df[['category', 'subcategory']])
        y = df['emission_kg']
        model = RandomForestRegressor(n_estimators=50)
        model.fit(X, y)

        # Calculate enhanced score (0-100)
        base_score = max(0, min(100, 100 - (daily_avg * 2)))
        consistency_score = model.score(X, y) * 20
        final_score = min(100, base_score + consistency_score)

        # Generate detailed strengths
        strengths = []
        if len(df) >= 7:
            strengths.append("Consistent data tracking enabling AI analysis")
        if len(df['category'].unique()) >= 3:
            strengths.append("Comprehensive multi-category monitoring")
        if len(df) > 0:
            strengths.append("AI-powered emission pattern detection")

        # Generate specific improvements
        improvements = []
        for category, value in categories.items():
            percentage = (value / total_emissions) * 100
            if percentage > 30:
                category_tips = {
                    'Energy': "Implement smart energy monitoring and switch to efficient appliances",
                    'Transport': "Consider eco-friendly transportation alternatives and route optimization",
                    'Food': "Focus on sustainable food choices and reduce waste",
                    'Waste': "Enhance recycling practices and minimize single-use items"
                }
                improvements.append(f"Reduce {category} emissions ({percentage:.1f}%) through {category_tips.get(category, 'AI-suggested optimizations')}")

        # Enhanced comparison text
        comparison = get_detailed_comparison(daily_avg)

        return {
            "score": round(final_score),
            "rating": get_detailed_rating(final_score),
            "strengths": strengths,
            "areas_for_improvement": improvements[:3],
            "comparison_to_average": comparison
        }

    except Exception as e:
        print(f"Error in sustainability score calculation: {e}")
        return {
            "score": 50,
            "rating": "AI Assessment Available",
            "strengths": ["AI tracking enabled"],
            "areas_for_improvement": ["Add more data for AI analysis"],
            "comparison_to_average": "AI comparison available"
        }

def get_detailed_rating(score):
    """Get detailed rating based on score"""
    if score >= 80: return "Excellent - Leading in Sustainability"
    elif score >= 60: return "Good - Making Positive Impact"
    elif score >= 40: return "Average - Room for Improvement"
    elif score >= 20: return "Below Average - Action Needed"
    else: return "Immediate Action Required - Let's improve together"

def get_detailed_comparison(daily_avg):
    """Enhanced comparison with specific context"""
    global_avg = 11  # kg CO2e per day
    if daily_avg < global_avg * 0.5: 
        return "Your footprint is significantly below average - Great sustainability practices!"
    elif daily_avg < global_avg: 
        return "Your footprint is below average - Keep up the good work"
    elif daily_avg < global_avg * 1.5: 
        return "Your footprint is above average - Consider our AI-powered recommendations"
    else: 
        return "Your footprint is significantly above average - Let's work together on immediate improvements"


def get_rating(score):
    """Get rating based on score"""
    if score >= 80: return "Excellent"
    elif score >= 60: return "Good"
    elif score >= 40: return "Average"
    elif score >= 20: return "Below Average"
    else: return "Needs Improvement"

def get_improvement_areas(df):
    """Get AI-suggested improvement areas"""
    areas = []
    categories = df.groupby('category')['emission_kg'].sum()
    if not categories.empty:
        highest = categories.idxmax()
        areas.append(f"Reduce {highest} emissions using AI suggestions")
    return areas

def get_comparison(daily_avg):
    """Compare to average using AI analysis"""
    global_avg = 11  # kg CO2e per day
    if daily_avg < global_avg * 0.5: return "Well below average"
    elif daily_avg < global_avg: return "Below average"
    elif daily_avg < global_avg * 1.5: return "Above average"
    else: return "Well above average"