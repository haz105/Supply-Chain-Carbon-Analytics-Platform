"""
Generate massive amounts of data for the Supply Chain Carbon Analytics Platform
Creates 100x more data (25,000 shipments) for realistic analytics and ML training.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etl.main import run_etl_pipeline
from database.connection import get_db_session
from database.models import Shipment, CarbonEmission
from sqlalchemy import func
import time
from datetime import datetime

def generate_massive_data():
    """Generate 25,000 shipments (100x more data)."""
    print("🚀 Generating Massive Dataset (25,000 shipments)...")
    print("=" * 60)
    
    start_time = time.time()
    
    # Generate data in batches to avoid memory issues
    batch_size = 1000
    total_shipments = 25000
    num_batches = total_shipments // batch_size
    
    print(f"📊 Generating {total_shipments:,} shipments in {num_batches} batches of {batch_size:,}")
    print()
    
    for batch in range(num_batches):
        batch_start = time.time()
        print(f"🔄 Batch {batch + 1}/{num_batches} - Generating {batch_size:,} shipments...")
        
        try:
            # Generate batch
            run_etl_pipeline(num_shipments=batch_size)
            
            batch_time = time.time() - batch_start
            print(f"✅ Batch {batch + 1} completed in {batch_time:.2f} seconds")
            
            # Show progress
            completed = (batch + 1) * batch_size
            progress = (completed / total_shipments) * 100
            print(f"📈 Progress: {completed:,}/{total_shipments:,} ({progress:.1f}%)")
            print()
            
        except Exception as e:
            print(f"❌ Error in batch {batch + 1}: {e}")
            continue
    
    total_time = time.time() - start_time
    
    # Verify the data
    print("🔍 Verifying generated data...")
    try:
        session = get_db_session()
        
        shipment_count = session.query(func.count(Shipment.shipment_id)).scalar()
        emission_count = session.query(func.count(CarbonEmission.emission_id)).scalar()
        
        session.close()
        
        print(f"✅ Verification complete:")
        print(f"   📦 Shipments: {shipment_count:,}")
        print(f"   🌱 Carbon Emissions: {emission_count:,}")
        print(f"   ⏱️ Total generation time: {total_time:.2f} seconds")
        print(f"   🚀 Average speed: {shipment_count/total_time:.1f} shipments/second")
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
    
    print("\n🎉 Massive data generation complete!")
    print("Your dashboard will now show much more comprehensive analytics!")

def check_data_distribution():
    """Check the distribution of the generated data."""
    print("\n📊 Data Distribution Analysis")
    print("=" * 40)
    
    try:
        session = get_db_session()
        
        # Transport mode distribution
        transport_query = session.query(
            Shipment.transport_mode,
            func.count(Shipment.shipment_id)
        ).group_by(Shipment.transport_mode).all()
        
        print("🚚 Transport Mode Distribution:")
        for mode, count in transport_query:
            percentage = (count / sum(c for _, c in transport_query)) * 100
            print(f"   {mode.title()}: {count:,} ({percentage:.1f}%)")
        
        # Package type distribution
        package_query = session.query(
            Shipment.package_type,
            func.count(Shipment.shipment_id)
        ).group_by(Shipment.package_type).all()
        
        print("\n📦 Package Type Distribution:")
        for package, count in package_query:
            percentage = (count / sum(c for _, c in package_query)) * 100
            print(f"   {package}: {count:,} ({percentage:.1f}%)")
        
        # Emissions statistics
        emissions_query = session.query(
            func.avg(CarbonEmission.co2_kg),
            func.min(CarbonEmission.co2_kg),
            func.max(CarbonEmission.co2_kg),
            func.sum(CarbonEmission.co2_kg)
        ).scalar()
        
        print(f"\n🌱 Emissions Statistics:")
        print(f"   Average CO₂ per shipment: {emissions_query[0]:.2f} kg")
        print(f"   Min CO₂ per shipment: {emissions_query[1]:.2f} kg")
        print(f"   Max CO₂ per shipment: {emissions_query[2]:.2f} kg")
        print(f"   Total CO₂ emissions: {emissions_query[3]:,.0f} kg")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Error analyzing data distribution: {e}")

if __name__ == "__main__":
    # Generate the massive dataset
    generate_massive_data()
    
    # Analyze the data distribution
    check_data_distribution()
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Launch dashboard: streamlit run dashboard/streamlit_app.py")
    print("2. Train ML models: python analytics/ml_models.py")
    print("3. Test API endpoints: python test_api.py")
    print("4. Move to Phase 3: Cloud deployment and advanced features") 