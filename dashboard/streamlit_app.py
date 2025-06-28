"""
Supply Chain Carbon Analytics - Streamlit Dashboard
A modern, interactive dashboard for carbon emissions analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta, date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db_session
from database.models import Shipment, CarbonEmission
from sqlalchemy import func, and_

# Page configuration
st.set_page_config(
    page_title="Carbon Analytics Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stAlert {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_filtered_data(start_date: str, end_date: str, transport_mode: str, package_type: str) -> pd.DataFrame:
    """Get filtered data from database with caching."""
    try:
        session = get_db_session()
        
        # Build query
        query = session.query(
            Shipment.shipment_id,
            Shipment.origin_lat,
            Shipment.origin_lng,
            Shipment.destination_lat,
            Shipment.destination_lng,
            Shipment.transport_mode,
            Shipment.weight_kg,
            Shipment.distance_km,
            Shipment.package_type,
            Shipment.departure_time,
            Shipment.arrival_time,
            CarbonEmission.co2_kg,
            CarbonEmission.co2_equivalent_kg,
            CarbonEmission.calculated_at
        ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id)
        
        # Apply date filter
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(
                and_(
                    Shipment.departure_time >= start_dt,
                    Shipment.departure_time <= end_dt
                )
            )
        
        # Apply transport mode filter
        if transport_mode != 'All Modes':
            query = query.filter(Shipment.transport_mode == transport_mode.lower())
        
        # Apply package type filter
        if package_type != 'All Types':
            query = query.filter(Shipment.package_type == package_type)
        
        # Execute query
        results = query.all()
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=[
            'shipment_id', 'origin_lat', 'origin_lng', 'destination_lat', 'destination_lng',
            'transport_mode', 'weight_kg', 'distance_km', 'package_type', 'departure_time',
            'arrival_time', 'co2_kg', 'co2_equivalent_kg', 'calculated_at'
        ])
        
        session.close()
        return df
        
    except Exception as e:
        st.error(f"Error getting data: {e}")
        return pd.DataFrame()

def calculate_metrics(df: pd.DataFrame) -> dict:
    """Calculate key metrics from data."""
    if df.empty:
        return {
            'total_emissions': 0,
            'total_shipments': 0,
            'avg_emissions': 0,
            'efficiency_score': 0,
            'total_distance': 0,
            'avg_distance': 0
        }
    
    total_emissions = df['co2_kg'].sum()
    total_shipments = len(df)
    avg_emissions = df['co2_kg'].mean()
    total_distance = df['distance_km'].sum()
    avg_distance = df['distance_km'].mean()
    
    # Calculate efficiency score (lower emissions per km = higher score)
    if total_distance > 0:
        efficiency = (1 / (total_emissions / total_distance)) * 1000
        efficiency_score = min(efficiency, 100)
    else:
        efficiency_score = 0
    
    return {
        'total_emissions': total_emissions,
        'total_shipments': total_shipments,
        'avg_emissions': avg_emissions,
        'efficiency_score': efficiency_score,
        'total_distance': total_distance,
        'avg_distance': avg_distance
    }

def main():
    # Header
    st.markdown('<h1 class="main-header">🌱 Supply Chain Carbon Analytics Platform</h1>', unsafe_allow_html=True)
    st.markdown("### Real-time carbon emissions tracking and supply chain optimization")
    
    # Sidebar filters
    st.sidebar.header("📊 Filters")
    
    # Date range
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(start_date, end_date),
        max_value=end_date
    )
    
    if len(date_range) == 2:
        start_date_str = date_range[0].isoformat()
        end_date_str = date_range[1].isoformat()
    else:
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
    
    # Transport mode filter
    transport_mode = st.sidebar.selectbox(
        "Transport Mode",
        ["All Modes", "Air", "Ground", "Sea"]
    )
    
    # Package type filter
    package_type = st.sidebar.selectbox(
        "Package Type",
        ["All Types", "Small Package", "Large Package", "Pallet"]
    )
    
    # Get data
    df = get_filtered_data(start_date_str, end_date_str, transport_mode, package_type)
    
    # Key metrics
    metrics = calculate_metrics(df)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total CO₂ Emissions",
            value=f"{metrics['total_emissions']:,.0f} kg",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Shipments",
            value=f"{metrics['total_shipments']:,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Avg Emissions/Shipment",
            value=f"{metrics['avg_emissions']:.1f} kg",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Efficiency Score",
            value=f"{metrics['efficiency_score']:.0f}/100",
            delta=None
        )
    
    # Charts
    if not df.empty:
        # Row 1: Timeline and Pie Chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Emissions Over Time")
            df['date'] = pd.to_datetime(df['departure_time']).dt.date
            daily_emissions = df.groupby('date')['co2_kg'].sum().reset_index()
            
            fig_timeline = px.line(
                daily_emissions,
                x='date',
                y='co2_kg',
                title="Daily Carbon Emissions",
                labels={'co2_kg': 'CO₂ Emissions (kg)', 'date': 'Date'}
            )
            fig_timeline.update_layout(height=400)
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        with col2:
            st.subheader("🥧 Emissions by Transport Mode")
            mode_emissions = df.groupby('transport_mode')['co2_kg'].sum().reset_index()
            
            fig_pie = px.pie(
                mode_emissions,
                values='co2_kg',
                names='transport_mode',
                title="Emissions Distribution",
                color_discrete_map={
                    'air': '#FF6B6B',
                    'ground': '#4ECDC4',
                    'sea': '#45B7D1'
                }
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Row 2: Scatter and Bar Chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distance vs Emissions")
            
            # Clean the data for the scatter plot
            df_clean = df.copy()
            df_clean['weight_kg'] = pd.to_numeric(df_clean['weight_kg'], errors='coerce')
            df_clean = df_clean.dropna(subset=['weight_kg', 'distance_km', 'co2_kg'])
            
            # Convert to float to ensure numeric type
            df_clean['weight_kg'] = df_clean['weight_kg'].astype(float)
            
            if not df_clean.empty:
                fig_scatter = px.scatter(
                    df_clean,
                    x='distance_km',
                    y='co2_kg',
                    color='transport_mode',
                    size='weight_kg',
                    hover_data=['package_type', 'weight_kg'],
                    title="Distance vs Emissions Relationship",
                    labels={
                        'distance_km': 'Distance (km)',
                        'co2_kg': 'CO₂ Emissions (kg)',
                        'transport_mode': 'Transport Mode',
                        'weight_kg': 'Weight (kg)'
                    }
                )
                fig_scatter.update_layout(height=400)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning("No valid data available for scatter plot after cleaning.")
        
        with col2:
            st.subheader("📦 Emissions by Package Type")
            package_emissions = df.groupby('package_type')['co2_kg'].sum().reset_index()
            
            fig_bar = px.bar(
                package_emissions,
                x='package_type',
                y='co2_kg',
                title="Emissions by Package Type",
                labels={'co2_kg': 'CO₂ Emissions (kg)', 'package_type': 'Package Type'},
                color='co2_kg',
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Row 3: Map and Statistics
        st.subheader("🗺️ Carbon Intensity Map")
        
        # Calculate carbon intensity and clean data for map
        df_map = df.copy()
        
        # Ensure numeric conversion for calculations
        df_map['co2_kg'] = pd.to_numeric(df_map['co2_kg'], errors='coerce')
        df_map['distance_km'] = pd.to_numeric(df_map['distance_km'], errors='coerce')
        
        # Calculate carbon intensity only for valid numeric data
        df_map = df_map.dropna(subset=['co2_kg', 'distance_km'])
        df_map['carbon_intensity'] = df_map['co2_kg'] / df_map['distance_km']
        
        # Ensure coordinates are numeric
        df_map['origin_lat'] = pd.to_numeric(df_map['origin_lat'], errors='coerce')
        df_map['origin_lng'] = pd.to_numeric(df_map['origin_lng'], errors='coerce')
        df_map = df_map.dropna(subset=['origin_lat', 'origin_lng', 'carbon_intensity'])
        
        # Convert carbon_intensity to float to ensure it's numeric
        df_map['carbon_intensity'] = df_map['carbon_intensity'].astype(float)
        
        if not df_map.empty:
            # Create map
            fig_map = px.scatter_mapbox(
                df_map,
                lat='origin_lat',
                lon='origin_lng',
                size='carbon_intensity',
                color='transport_mode',
                hover_data=['distance_km', 'co2_kg', 'package_type'],
                title="Carbon Intensity by Origin Location",
                mapbox_style="carto-positron",
                zoom=3
            )
            
            fig_map.update_layout(
                mapbox=dict(
                    center=dict(lat=39.8283, lon=-98.5795)  # Center of US
                ),
                height=500
            )
            
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No valid coordinate data available for map visualization.")
        
        # Statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Summary Statistics")
            
            # Clean data for statistics
            df_stats = df.copy()
            df_stats['co2_kg'] = pd.to_numeric(df_stats['co2_kg'], errors='coerce')
            df_stats['distance_km'] = pd.to_numeric(df_stats['distance_km'], errors='coerce')
            df_stats['weight_kg'] = pd.to_numeric(df_stats['weight_kg'], errors='coerce')
            df_stats = df_stats.dropna(subset=['co2_kg', 'distance_km', 'weight_kg'])
            
            if not df_stats.empty:
                stats_df = df_stats[['co2_kg', 'distance_km', 'weight_kg']].describe()
                st.dataframe(stats_df, use_container_width=True)
            else:
                st.warning("No valid data available for statistics.")
        
        with col2:
            st.subheader("🏆 Top Performers")
            
            # Most efficient shipments (lowest emissions per km)
            df_efficiency = df.copy()
            df_efficiency['co2_kg'] = pd.to_numeric(df_efficiency['co2_kg'], errors='coerce')
            df_efficiency['distance_km'] = pd.to_numeric(df_efficiency['distance_km'], errors='coerce')
            df_efficiency = df_efficiency.dropna(subset=['co2_kg', 'distance_km'])
            
            if not df_efficiency.empty:
                df_efficiency['efficiency'] = df_efficiency['co2_kg'] / df_efficiency['distance_km']
                efficient_shipments = df_efficiency.nsmallest(5, 'efficiency')[['shipment_id', 'transport_mode', 'distance_km', 'co2_kg', 'efficiency']]
                efficient_shipments['efficiency'] = efficient_shipments['efficiency'].round(4)
                efficient_shipments['shipment_id'] = efficient_shipments['shipment_id'].astype(str).str[:8] + '...'
                
                st.dataframe(efficient_shipments, use_container_width=True)
            else:
                st.warning("No valid data available for efficiency analysis.")
        
        # Recent shipments table
        st.subheader("📋 Recent Shipments")
        
        # Sort by departure time and take recent 20
        df_sorted = df.sort_values('departure_time', ascending=False).head(20)
        
        # Format the table
        table_data = []
        for _, row in df_sorted.iterrows():
            table_data.append({
                'Shipment ID': str(row['shipment_id'])[:8] + '...',
                'Transport Mode': row['transport_mode'].title(),
                'Package Type': row['package_type'],
                'Distance (km)': f"{row['distance_km']:.1f}",
                'Weight (kg)': f"{row['weight_kg']:.1f}",
                'CO₂ (kg)': f"{row['co2_kg']:.2f}",
                'Departure': pd.to_datetime(row['departure_time']).strftime('%Y-%m-%d %H:%M')
            })
        
        table_df = pd.DataFrame(table_data)
        st.dataframe(table_df, use_container_width=True)
        
    else:
        st.warning("No data found for the selected filters. Try adjusting your date range or filters.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🌱 Supply Chain Carbon Analytics Platform | Built for Amazon BI Engineer Internship</p>
        <p>Real-time carbon emissions tracking and supply chain optimization</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 