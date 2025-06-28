"""
Supply Chain Carbon Analytics Dashboard
A comprehensive dashboard for visualizing carbon emissions and supply chain data.
"""

import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import uuid
from typing import Dict, List, Optional

# Database imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db_session
from database.models import Shipment, CarbonEmission
from sqlalchemy import func, and_

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

app.title = "Supply Chain Carbon Analytics Platform"

# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-leaf me-3"),
                "Supply Chain Carbon Analytics Platform"
            ], className="text-primary mb-3"),
            html.P("Real-time carbon emissions tracking and supply chain optimization", 
                   className="text-muted")
        ], width=12)
    ], className="mb-4"),
    
    # Filters
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Filters", className="card-title"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Date Range"),
                            dcc.DatePickerRange(
                                id='date-range',
                                start_date=(date.today() - timedelta(days=30)).isoformat(),
                                end_date=date.today().isoformat(),
                                display_format='YYYY-MM-DD'
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("Transport Mode"),
                            dcc.Dropdown(
                                id='transport-mode-filter',
                                options=[
                                    {'label': 'All Modes', 'value': 'all'},
                                    {'label': 'Air', 'value': 'air'},
                                    {'label': 'Ground', 'value': 'ground'},
                                    {'label': 'Sea', 'value': 'sea'}
                                ],
                                value='all',
                                clearable=False
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("Package Type"),
                            dcc.Dropdown(
                                id='package-type-filter',
                                options=[
                                    {'label': 'All Types', 'value': 'all'},
                                    {'label': 'Small Package', 'value': 'Small Package'},
                                    {'label': 'Large Package', 'value': 'Large Package'},
                                    {'label': 'Pallet', 'value': 'Pallet'}
                                ],
                                value='all',
                                clearable=False
                            )
                        ], width=4)
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Key Metrics
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id='total-emissions', className="text-primary"),
                    html.P("Total CO₂ Emissions (kg)", className="text-muted mb-0")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id='total-shipments', className="text-success"),
                    html.P("Total Shipments", className="text-muted mb-0")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id='avg-emissions', className="text-warning"),
                    html.P("Avg Emissions per Shipment", className="text-muted mb-0")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id='efficiency-score', className="text-info"),
                    html.P("Efficiency Score", className="text-muted mb-0")
                ])
            ], className="text-center")
        ], width=3)
    ], className="mb-4"),
    
    # Charts Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Emissions Over Time", className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='emissions-timeline')
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Emissions by Transport Mode", className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='emissions-by-mode')
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Charts Row 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Distance vs Emissions Scatter", className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='distance-emissions-scatter')
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Emissions by Package Type", className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='emissions-by-package')
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Advanced Analytics
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Carbon Intensity Analysis", className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='carbon-intensity-map')
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Data Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Recent Shipments", className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id='shipments-table')
                ])
            ])
        ], width=12)
    ])
    
], fluid=True)

def get_filtered_data(start_date: str, end_date: str, transport_mode: str, package_type: str) -> pd.DataFrame:
    """Get filtered data from database."""
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
        if transport_mode != 'all':
            query = query.filter(Shipment.transport_mode == transport_mode)
        
        # Apply package type filter
        if package_type != 'all':
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
        print(f"Error getting data: {e}")
        return pd.DataFrame()

# Callbacks
@app.callback(
    [Output('total-emissions', 'children'),
     Output('total-shipments', 'children'),
     Output('avg-emissions', 'children'),
     Output('efficiency-score', 'children')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('transport-mode-filter', 'value'),
     Input('package-type-filter', 'value')]
)
def update_metrics(start_date, end_date, transport_mode, package_type):
    """Update key metrics."""
    df = get_filtered_data(start_date, end_date, transport_mode, package_type)
    
    if df.empty:
        return "0", "0", "0", "0"
    
    total_emissions = f"{df['co2_kg'].sum():,.0f} kg"
    total_shipments = f"{len(df):,}"
    avg_emissions = f"{df['co2_kg'].mean():.1f} kg"
    
    # Calculate efficiency score (lower emissions per km = higher score)
    if df['distance_km'].sum() > 0:
        efficiency = (1 / (df['co2_kg'].sum() / df['distance_km'].sum())) * 1000
        efficiency_score = f"{min(efficiency, 100):.0f}/100"
    else:
        efficiency_score = "0/100"
    
    return total_emissions, total_shipments, avg_emissions, efficiency_score

@app.callback(
    Output('emissions-timeline', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('transport-mode-filter', 'value'),
     Input('package-type-filter', 'value')]
)
def update_emissions_timeline(start_date, end_date, transport_mode, package_type):
    """Update emissions timeline chart."""
    df = get_filtered_data(start_date, end_date, transport_mode, package_type)
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Group by date
    df['date'] = pd.to_datetime(df['departure_time']).dt.date
    daily_emissions = df.groupby('date')['co2_kg'].sum().reset_index()
    
    fig = px.line(
        daily_emissions,
        x='date',
        y='co2_kg',
        title="Daily Carbon Emissions",
        labels={'co2_kg': 'CO₂ Emissions (kg)', 'date': 'Date'}
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="CO₂ Emissions (kg)",
        hovermode='x unified'
    )
    
    return fig

@app.callback(
    Output('emissions-by-mode', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('transport-mode-filter', 'value'),
     Input('package-type-filter', 'value')]
)
def update_emissions_by_mode(start_date, end_date, transport_mode, package_type):
    """Update emissions by transport mode chart."""
    df = get_filtered_data(start_date, end_date, transport_mode, package_type)
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    mode_emissions = df.groupby('transport_mode')['co2_kg'].sum().reset_index()
    
    fig = px.pie(
        mode_emissions,
        values='co2_kg',
        names='transport_mode',
        title="Emissions by Transport Mode",
        color_discrete_map={
            'air': '#FF6B6B',
            'ground': '#4ECDC4',
            'sea': '#45B7D1'
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

@app.callback(
    Output('distance-emissions-scatter', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('transport-mode-filter', 'value'),
     Input('package-type-filter', 'value')]
)
def update_distance_emissions_scatter(start_date, end_date, transport_mode, package_type):
    """Update distance vs emissions scatter plot."""
    df = get_filtered_data(start_date, end_date, transport_mode, package_type)
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    fig = px.scatter(
        df,
        x='distance_km',
        y='co2_kg',
        color='transport_mode',
        size='weight_kg',
        hover_data=['package_type', 'weight_kg'],
        title="Distance vs Emissions",
        labels={
            'distance_km': 'Distance (km)',
            'co2_kg': 'CO₂ Emissions (kg)',
            'transport_mode': 'Transport Mode',
            'weight_kg': 'Weight (kg)'
        }
    )
    
    fig.update_layout(
        xaxis_title="Distance (km)",
        yaxis_title="CO₂ Emissions (kg)"
    )
    
    return fig

@app.callback(
    Output('emissions-by-package', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('transport-mode-filter', 'value'),
     Input('package-type-filter', 'value')]
)
def update_emissions_by_package(start_date, end_date, transport_mode, package_type):
    """Update emissions by package type chart."""
    df = get_filtered_data(start_date, end_date, transport_mode, package_type)
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    package_emissions = df.groupby('package_type')['co2_kg'].sum().reset_index()
    
    fig = px.bar(
        package_emissions,
        x='package_type',
        y='co2_kg',
        title="Emissions by Package Type",
        labels={'co2_kg': 'CO₂ Emissions (kg)', 'package_type': 'Package Type'},
        color='co2_kg',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title="Package Type",
        yaxis_title="CO₂ Emissions (kg)"
    )
    
    return fig

@app.callback(
    Output('carbon-intensity-map', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('transport-mode-filter', 'value'),
     Input('package-type-filter', 'value')]
)
def update_carbon_intensity_map(start_date, end_date, transport_mode, package_type):
    """Update carbon intensity map."""
    df = get_filtered_data(start_date, end_date, transport_mode, package_type)
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Calculate carbon intensity (emissions per km)
    df['carbon_intensity'] = df['co2_kg'] / df['distance_km']
    
    # Create scatter mapbox
    fig = px.scatter_mapbox(
        df,
        lat='origin_lat',
        lon='origin_lng',
        size='carbon_intensity',
        color='transport_mode',
        hover_data=['distance_km', 'co2_kg', 'package_type'],
        title="Carbon Intensity by Origin Location",
        mapbox_style="carto-positron",
        zoom=3
    )
    
    fig.update_layout(
        mapbox=dict(
            center=dict(lat=39.8283, lon=-98.5795)  # Center of US
        ),
        height=500
    )
    
    return fig

@app.callback(
    Output('shipments-table', 'children'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('transport-mode-filter', 'value'),
     Input('package-type-filter', 'value')]
)
def update_shipments_table(start_date, end_date, transport_mode, package_type):
    """Update shipments table."""
    df = get_filtered_data(start_date, end_date, transport_mode, package_type)
    
    if df.empty:
        return html.P("No shipments found for the selected filters.")
    
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
    
    return dbc.Table.from_dataframe(
        pd.DataFrame(table_data),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True
    )

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8050) 