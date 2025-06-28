#!/usr/bin/env python3
"""
Simple script to check database status and verify migrations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_session
from database.models import Shipment, CarbonEmission
from sqlalchemy import text

def check_database():
    """Check database status and table structure."""
    print("🔍 Checking database status...")
    
    try:
        with get_db_session() as session:
            # Check if tables exist and have data
            shipment_count = session.query(Shipment).count()
            emission_count = session.query(CarbonEmission).count()
            
            print(f"📦 Shipments in database: {shipment_count}")
            print(f"🌱 Carbon emissions in database: {emission_count}")
            
            # Check column types for carbon_emissions table
            result = session.execute(text("""
                SELECT column_name, data_type, numeric_precision, numeric_scale
                FROM information_schema.columns 
                WHERE table_name = 'carbon_emissions' 
                AND column_name IN ('co2_kg', 'ch4_kg', 'n2o_kg', 'co2_equivalent_kg')
                ORDER BY column_name
            """))
            
            print("\n📊 Carbon emissions column types:")
            for row in result:
                print(f"   {row.column_name}: {row.data_type}({row.numeric_precision},{row.numeric_scale})")
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database() 