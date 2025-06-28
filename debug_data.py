"""
Debug script to check data types and values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_session
from database.models import Shipment, CarbonEmission
from sqlalchemy import func
import pandas as pd

def debug_data():
    """Debug the data types and values."""
    try:
        session = get_db_session()
        
        # Get some sample data
        query = session.query(
            Shipment.shipment_id,
            Shipment.origin_lat,
            Shipment.origin_lng,
            Shipment.weight_kg,
            Shipment.distance_km,
            CarbonEmission.co2_kg,
            CarbonEmission.co2_equivalent_kg
        ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id).limit(5)
        
        results = query.all()
        
        print("Sample data from database:")
        for i, row in enumerate(results):
            print(f"Row {i}:")
            print(f"  shipment_id: {row[0]} (type: {type(row[0])})")
            print(f"  origin_lat: {row[1]} (type: {type(row[1])})")
            print(f"  origin_lng: {row[2]} (type: {type(row[2])})")
            print(f"  weight_kg: {row[3]} (type: {type(row[3])})")
            print(f"  distance_km: {row[4]} (type: {type(row[4])})")
            print(f"  co2_kg: {row[5]} (type: {type(row[5])})")
            print(f"  co2_equivalent_kg: {row[6]} (type: {type(row[6])})")
            print()
        
        # Convert to DataFrame and check types
        df = pd.DataFrame(results, columns=[
            'shipment_id', 'origin_lat', 'origin_lng', 'weight_kg', 
            'distance_km', 'co2_kg', 'co2_equivalent_kg'
        ])
        
        print("DataFrame info:")
        print(df.info())
        print("\nDataFrame dtypes:")
        print(df.dtypes)
        
        # Test numeric conversion
        print("\nTesting numeric conversion:")
        weight_numeric = pd.to_numeric(df['weight_kg'], errors='coerce')
        print(f"weight_kg after pd.to_numeric: {weight_numeric.dtype}")
        print(f"weight_kg values: {weight_numeric.values}")
        
        co2_numeric = pd.to_numeric(df['co2_kg'], errors='coerce')
        print(f"co2_kg after pd.to_numeric: {co2_numeric.dtype}")
        print(f"co2_kg values: {co2_numeric.values}")
        
        session.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_data() 