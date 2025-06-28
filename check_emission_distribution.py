#!/usr/bin/env python3
"""
Script to analyze emission type distribution and identify skewing issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_session
from database.models import Shipment, CarbonEmission
from sqlalchemy import func
import pandas as pd

def analyze_emission_distribution():
    """Analyze the distribution of emission types and transport modes."""
    print("🔍 Analyzing Emission Type Distribution")
    print("=" * 50)
    
    try:
        session = get_db_session()
        
        # 1. Transport mode distribution
        print("\n1️⃣ Transport Mode Distribution:")
        transport_dist = session.query(
            Shipment.transport_mode,
            func.count(Shipment.shipment_id)
        ).group_by(Shipment.transport_mode).all()
        
        total_shipments = sum(count for _, count in transport_dist)
        for mode, count in transport_dist:
            percentage = (count / total_shipments) * 100
            print(f"   {mode.title()}: {count:,} ({percentage:.1f}%)")
        
        # 2. Package type distribution
        print("\n2️⃣ Package Type Distribution:")
        package_dist = session.query(
            Shipment.package_type,
            func.count(Shipment.shipment_id)
        ).group_by(Shipment.package_type).all()
        
        total_packages = sum(count for _, count in package_dist)
        for package, count in package_dist:
            percentage = (count / total_packages) * 100
            print(f"   {package}: {count:,} ({percentage:.1f}%)")
        
        # 3. Distance distribution by transport mode
        print("\n3️⃣ Distance Distribution by Transport Mode:")
        distance_stats = session.query(
            Shipment.transport_mode,
            func.avg(Shipment.distance_km).label('avg_distance'),
            func.min(Shipment.distance_km).label('min_distance'),
            func.max(Shipment.distance_km).label('max_distance'),
            func.count(Shipment.shipment_id).label('count')
        ).group_by(Shipment.transport_mode).all()
        
        for mode, avg_dist, min_dist, max_dist, count in distance_stats:
            print(f"   {mode.title()}:")
            print(f"     Count: {count:,}")
            print(f"     Avg Distance: {float(avg_dist):.1f} km")
            print(f"     Min Distance: {float(min_dist):.1f} km")
            print(f"     Max Distance: {float(max_dist):.1f} km")
        
        # 4. Emission values by transport mode
        print("\n4️⃣ Emission Values by Transport Mode:")
        emission_stats = session.query(
            Shipment.transport_mode,
            func.avg(CarbonEmission.co2_kg).label('avg_co2'),
            func.min(CarbonEmission.co2_kg).label('min_co2'),
            func.max(CarbonEmission.co2_kg).label('max_co2'),
            func.sum(CarbonEmission.co2_kg).label('total_co2')
        ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id).group_by(Shipment.transport_mode).all()
        
        for mode, avg_co2, min_co2, max_co2, total_co2 in emission_stats:
            print(f"   {mode.title()}:")
            print(f"     Avg CO2: {float(avg_co2):.2f} kg")
            print(f"     Min CO2: {float(min_co2):.2f} kg")
            print(f"     Max CO2: {float(max_co2):.2f} kg")
            print(f"     Total CO2: {float(total_co2):,.0f} kg")
        
        # 5. Check for potential issues
        print("\n5️⃣ Potential Issues Analysis:")
        
        # Check if any transport mode has 0 emissions
        zero_emissions = session.query(Shipment.transport_mode).join(
            CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id
        ).filter(CarbonEmission.co2_kg == 0).count()
        
        if zero_emissions > 0:
            print(f"   ⚠️ Found {zero_emissions} shipments with 0 CO2 emissions")
        
        # Check for extreme emission values
        extreme_emissions = session.query(Shipment.transport_mode).join(
            CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id
        ).filter(CarbonEmission.co2_kg > 10000).count()
        
        if extreme_emissions > 0:
            print(f"   ⚠️ Found {extreme_emissions} shipments with extreme CO2 emissions (>10,000 kg)")
        
        # Check distance vs emission correlation
        print("\n6️⃣ Distance vs Emission Correlation:")
        correlation_data = session.query(
            Shipment.distance_km,
            CarbonEmission.co2_kg
        ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id).limit(1000).all()
        
        if correlation_data:
            df = pd.DataFrame(correlation_data, columns=['distance_km', 'co2_kg'])
            correlation = df['distance_km'].corr(df['co2_kg'])
            print(f"   Correlation between distance and CO2: {correlation:.3f}")
            
            if correlation < 0.5:
                print("   ⚠️ Low correlation - emissions may not be properly calculated")
            else:
                print("   ✅ Good correlation - emissions calculation looks reasonable")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Error analyzing distribution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_emission_distribution() 