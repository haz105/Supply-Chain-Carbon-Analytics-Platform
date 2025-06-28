#!/usr/bin/env python3
"""
Debug script to understand what's happening with the database and data generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_database():
    """Debug database connection and status."""
    with open('debug_output.txt', 'w') as f:
        f.write("🔍 Database Debug Information\n")
        f.write("=" * 50 + "\n")
        
        try:
            from database.connection import get_db_session
            from database.models import Shipment, CarbonEmission
            from sqlalchemy import text
            
            f.write("✅ Imported database modules successfully\n")
            
            with get_db_session() as session:
                f.write("✅ Database session created successfully\n")
                
                # Test basic connection
                result = session.execute(text("SELECT 1"))
                f.write("✅ Basic database query successful\n")
                
                # Check table counts
                shipment_count = session.query(Shipment).count()
                emission_count = session.query(CarbonEmission).count()
                f.write(f"📦 Shipments: {shipment_count}\n")
                f.write(f"🌱 Emissions: {emission_count}\n")
                
                # Check column precision
                result = session.execute(text("""
                    SELECT column_name, data_type, numeric_precision, numeric_scale
                    FROM information_schema.columns 
                    WHERE table_name = 'carbon_emissions' 
                    AND column_name = 'co2_kg'
                """))
                
                row = result.fetchone()
                if row:
                    f.write(f"✅ CO2 column type: {row.data_type}({row.numeric_precision},{row.numeric_scale})\n")
                    if row.numeric_precision >= 18:
                        f.write("✅ Migration applied successfully - precision increased to 18\n")
                    else:
                        f.write("❌ Migration not applied - precision still too low\n")
                else:
                    f.write("❌ Could not find CO2 column\n")
                    
        except Exception as e:
            f.write(f"❌ Database debug failed: {e}\n")
            import traceback
            f.write(traceback.format_exc())
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("🎯 Database debug completed\n")

def debug_data_generation():
    """Debug data generation process."""
    with open('debug_output.txt', 'a') as f:
        f.write("\n🚀 Data Generation Debug Information\n")
        f.write("=" * 50 + "\n")
        
        try:
            from etl.main import run_etl_pipeline
            
            f.write("✅ Imported ETL modules successfully\n")
            
            # Test with just 2 shipments
            f.write("Generating 2 test shipments...\n")
            run_etl_pipeline(num_shipments=2)
            f.write("✅ Data generation test completed\n")
            
        except Exception as e:
            f.write(f"❌ Data generation debug failed: {e}\n")
            import traceback
            f.write(traceback.format_exc())
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("🎯 Data generation debug completed\n")

def main():
    """Run all debug functions."""
    print("🧪 Running debug script...")
    print("Output will be written to debug_output.txt")
    
    debug_database()
    debug_data_generation()
    
    print("✅ Debug script completed. Check debug_output.txt for results.")

if __name__ == "__main__":
    main() 