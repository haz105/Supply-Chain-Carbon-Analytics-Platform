#!/usr/bin/env python3
"""
Test script to verify the database fix and test data generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test database connection and migration status."""
    print("🔍 Testing database connection...")
    
    try:
        from database.connection import get_db_session
        from database.models import Shipment, CarbonEmission
        from sqlalchemy import text
        
        with get_db_session() as session:
            # Test basic connection
            result = session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            
            # Check table counts
            shipment_count = session.query(Shipment).count()
            emission_count = session.query(CarbonEmission).count()
            print(f"📦 Shipments: {shipment_count}")
            print(f"🌱 Emissions: {emission_count}")
            
            # Check column precision
            result = session.execute(text("""
                SELECT column_name, data_type, numeric_precision, numeric_scale
                FROM information_schema.columns 
                WHERE table_name = 'carbon_emissions' 
                AND column_name = 'co2_kg'
            """))
            
            row = result.fetchone()
            if row:
                print(f"✅ CO2 column type: {row.data_type}({row.numeric_precision},{row.numeric_scale})")
                if row.numeric_precision >= 18:
                    print("✅ Migration applied successfully - precision increased to 18")
                else:
                    print("❌ Migration not applied - precision still too low")
            else:
                print("❌ Could not find CO2 column")
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

def test_data_generation():
    """Test data generation with a small sample."""
    print("\n🚀 Testing data generation...")
    
    try:
        from etl.main import run_etl_pipeline
        
        # Test with just 5 shipments
        print("Generating 5 test shipments...")
        run_etl_pipeline(num_shipments=5)
        print("✅ Data generation test completed")
        
    except Exception as e:
        print(f"❌ Data generation test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("🧪 Running comprehensive tests...")
    print("=" * 50)
    
    test_database_connection()
    test_data_generation()
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("If you see ✅ marks above, the fix is working!")
    print("If you see ❌ marks, there are still issues to resolve.")

if __name__ == "__main__":
    main() 