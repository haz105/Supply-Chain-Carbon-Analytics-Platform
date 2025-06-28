#!/usr/bin/env python3
"""
Simple test script to debug the data generation issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_step_by_step():
    """Test each step of the ETL pipeline separately."""
    
    print("🧪 Testing ETL pipeline step by step...")
    print("=" * 50)
    
    # Step 1: Test data generation
    print("\n1️⃣ Testing data generation...")
    try:
        from data_generators.shipment_generator import ShipmentGenerator
        from datetime import datetime, timedelta
        
        generator = ShipmentGenerator()
        today = datetime.now()
        start_date = today - timedelta(days=30)
        end_date = today - timedelta(days=1)
        
        shipments = generator.generate_shipments(
            num_shipments=5,
            start_date=start_date,
            end_date=end_date,
            include_seasonal_patterns=True
        )
        print(f"✅ Generated {len(shipments)} shipments")
        print(f"   Sample shipment: {shipments[0] if shipments else 'None'}")
        
    except Exception as e:
        print(f"❌ Data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Test emissions calculation
    print("\n2️⃣ Testing emissions calculation...")
    try:
        from etl.transformations import DataTransformationPipeline
        
        transformer = DataTransformationPipeline()
        shipments = transformer.calculate_emissions_for_shipments(shipments)
        
        emissions_count = sum('co2_kg' in s for s in shipments)
        print(f"✅ Calculated emissions for {emissions_count} shipments")
        if emissions_count > 0:
            print(f"   Sample CO2 value: {shipments[0].get('co2_kg', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Emissions calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Test database connection
    print("\n3️⃣ Testing database connection...")
    try:
        from database.connection import get_db_session
        from database.models import Shipment, CarbonEmission
        
        with get_db_session() as session:
            # Test basic query
            count = session.query(Shipment).count()
            print(f"✅ Database connection successful. Current shipments: {count}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Test data ingestion
    print("\n4️⃣ Testing data ingestion...")
    try:
        from etl.ingestion import DataIngestionPipeline
        
        ingestion = DataIngestionPipeline()
        ingestion.ingest_daily_shipments(shipments)
        print("✅ Data ingestion completed")
        
    except Exception as e:
        print(f"❌ Data ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_step_by_step() 