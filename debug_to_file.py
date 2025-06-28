#!/usr/bin/env python3
"""
Debug script that writes output to a file to bypass terminal output issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_to_file():
    """Run debug tests and write output to file."""
    
    with open('debug_results.txt', 'w') as f:
        f.write("🔍 Debug Results\n")
        f.write("=" * 50 + "\n")
        
        # Test 1: Basic imports
        f.write("\n1️⃣ Testing basic imports...\n")
        try:
            from data_generators.shipment_generator import ShipmentGenerator
            f.write("✅ ShipmentGenerator imported successfully\n")
        except Exception as e:
            f.write(f"❌ ShipmentGenerator import failed: {e}\n")
            return
        
        try:
            from etl.transformations import DataTransformationPipeline
            f.write("✅ DataTransformationPipeline imported successfully\n")
        except Exception as e:
            f.write(f"❌ DataTransformationPipeline import failed: {e}\n")
            return
        
        try:
            from etl.ingestion import DataIngestionPipeline
            f.write("✅ DataIngestionPipeline imported successfully\n")
        except Exception as e:
            f.write(f"❌ DataIngestionPipeline import failed: {e}\n")
            return
        
        try:
            from database.connection import get_db_session
            f.write("✅ Database connection imported successfully\n")
        except Exception as e:
            f.write(f"❌ Database connection import failed: {e}\n")
            return
        
        # Test 2: Data generation
        f.write("\n2️⃣ Testing data generation...\n")
        try:
            from datetime import datetime, timedelta
            
            generator = ShipmentGenerator()
            today = datetime.now()
            start_date = today - timedelta(days=30)
            end_date = today - timedelta(days=1)
            
            shipments = generator.generate_shipments(
                num_shipments=3,
                start_date=start_date,
                end_date=end_date,
                include_seasonal_patterns=True
            )
            f.write(f"✅ Generated {len(shipments)} shipments\n")
            if shipments:
                f.write(f"   Sample shipment keys: {list(shipments[0].keys())}\n")
                f.write(f"   Sample shipment: {shipments[0]}\n")
            
        except Exception as e:
            f.write(f"❌ Data generation failed: {e}\n")
            import traceback
            f.write(traceback.format_exc())
            return
        
        # Test 3: Emissions calculation
        f.write("\n3️⃣ Testing emissions calculation...\n")
        try:
            transformer = DataTransformationPipeline()
            shipments = transformer.calculate_emissions_for_shipments(shipments)
            
            emissions_count = sum('co2_kg' in s for s in shipments)
            f.write(f"✅ Calculated emissions for {emissions_count} shipments\n")
            if emissions_count > 0:
                f.write(f"   Sample CO2 value: {shipments[0].get('co2_kg', 'N/A')}\n")
                f.write(f"   Sample CO2 equivalent: {shipments[0].get('co2_equivalent_kg', 'N/A')}\n")
            
        except Exception as e:
            f.write(f"❌ Emissions calculation failed: {e}\n")
            import traceback
            f.write(traceback.format_exc())
            return
        
        # Test 4: Database connection
        f.write("\n4️⃣ Testing database connection...\n")
        try:
            with get_db_session() as session:
                from database.models import Shipment, CarbonEmission
                
                # Test basic query
                count = session.query(Shipment).count()
                f.write(f"✅ Database connection successful. Current shipments: {count}\n")
                
                # Check column types
                from sqlalchemy import text
                result = session.execute(text("""
                    SELECT column_name, data_type, numeric_precision, numeric_scale
                    FROM information_schema.columns 
                    WHERE table_name = 'carbon_emissions' 
                    AND column_name = 'co2_kg'
                """))
                
                row = result.fetchone()
                if row:
                    f.write(f"✅ CO2 column type: {row.data_type}({row.numeric_precision},{row.numeric_scale})\n")
                else:
                    f.write("❌ Could not find CO2 column\n")
                
        except Exception as e:
            f.write(f"❌ Database connection failed: {e}\n")
            import traceback
            f.write(traceback.format_exc())
            return
        
        # Test 5: Data ingestion
        f.write("\n5️⃣ Testing data ingestion...\n")
        try:
            ingestion = DataIngestionPipeline()
            ingestion.ingest_daily_shipments(shipments)
            f.write("✅ Data ingestion completed\n")
            
            # Check if data was actually inserted
            with get_db_session() as session:
                new_count = session.query(Shipment).count()
                f.write(f"✅ New shipment count: {new_count}\n")
                
        except Exception as e:
            f.write(f"❌ Data ingestion failed: {e}\n")
            import traceback
            f.write(traceback.format_exc())
            return
        
        f.write("\n🎉 All tests completed successfully!\n")

if __name__ == "__main__":
    debug_to_file()
    print("Debug completed. Check debug_results.txt for results.") 