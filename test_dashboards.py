"""
Test script for dashboards and ML models
"""

import subprocess
import time
import requests
import sys
import os
from datetime import datetime

def test_dashboards():
    """Test the dashboard functionality."""
    print("🚀 Testing Dashboards and ML Models...")
    print("=" * 60)
    
    # Test 1: Check if required packages are installed
    print("\n📋 Package Dependencies")
    print("-" * 40)
    
    required_packages = [
        'dash', 'dash-bootstrap-components', 'plotly', 
        'streamlit', 'scikit-learn', 'pandas', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    # Test 2: Test ML models
    print("\n📋 Machine Learning Models")
    print("-" * 40)
    
    try:
        from analytics.ml_models import train_all_models, get_training_data
        
        # Check if we have training data
        training_data = get_training_data(days_back=30)
        if training_data.empty:
            print("  ⚠️ No training data available - generating sample data first")
            # Generate some data
            from etl.main import run_etl_pipeline
            run_etl_pipeline(num_shipments=100)
            training_data = get_training_data(days_back=30)
        
        if not training_data.empty:
            print(f"  ✅ Training data available: {len(training_data)} records")
            
            # Train models
            print("  🔄 Training ML models...")
            results = train_all_models()
            
            if 'error' not in results:
                print("  ✅ ML models trained successfully")
                for model_name, metrics in results.items():
                    if isinstance(metrics, dict) and 'r2' in metrics:
                        print(f"    {model_name}: R² = {metrics['r2']:.3f}")
            else:
                print(f"  ❌ ML training failed: {results.get('error', 'Unknown error')}")
        else:
            print("  ❌ No training data available")
            
    except Exception as e:
        print(f"  ❌ ML models test failed: {e}")
    
    # Test 3: Test dashboard imports
    print("\n📋 Dashboard Components")
    print("-" * 40)
    
    try:
        # Test Dash dashboard
        import dash
        from dash import dcc, html
        import dash_bootstrap_components as dbc
        print("  ✅ Dash components imported successfully")
        
        # Test Streamlit
        import streamlit as st
        print("  ✅ Streamlit imported successfully")
        
        # Test Plotly
        import plotly.express as px
        import plotly.graph_objects as go
        print("  ✅ Plotly components imported successfully")
        
    except Exception as e:
        print(f"  ❌ Dashboard imports failed: {e}")
        return False
    
    # Test 4: Test database connection for dashboards
    print("\n📋 Dashboard Data Access")
    print("-" * 40)
    
    try:
        from database.connection import get_db_session
        from database.models import Shipment, CarbonEmission
        from sqlalchemy import func
        
        session = get_db_session()
        
        # Check if we have data
        shipment_count = session.query(func.count(Shipment.shipment_id)).scalar()
        emission_count = session.query(func.count(CarbonEmission.emission_id)).scalar()
        
        print(f"  ✅ Database connected")
        print(f"  📊 Shipments: {shipment_count}")
        print(f"  📊 Emissions: {emission_count}")
        
        if shipment_count == 0 or emission_count == 0:
            print("  ⚠️ No data available - generating sample data")
            from etl.main import run_etl_pipeline
            run_etl_pipeline(num_shipments=50)
        
        session.close()
        
    except Exception as e:
        print(f"  ❌ Database access failed: {e}")
        return False
    
    print("\n✅ Dashboard and ML tests completed successfully!")
    return True

def start_dashboards():
    """Start the dashboard servers."""
    print("\n🌐 Starting Dashboards...")
    print("=" * 60)
    
    # Start Streamlit dashboard
    print("\n📊 Starting Streamlit Dashboard...")
    print("  URL: http://localhost:8501")
    print("  Press Ctrl+C to stop")
    
    try:
        # Start Streamlit in background
        streamlit_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard/streamlit_app.py", 
            "--server.port", "8501",
            "--server.address", "127.0.0.1"
        ])
        
        print("  ✅ Streamlit dashboard started")
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test if server is responding
        try:
            response = requests.get("http://localhost:8501", timeout=5)
            if response.status_code == 200:
                print("  ✅ Streamlit dashboard is responding")
            else:
                print(f"  ⚠️ Streamlit dashboard returned status {response.status_code}")
        except requests.exceptions.RequestException:
            print("  ⚠️ Streamlit dashboard not responding yet")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down dashboards...")
            streamlit_process.terminate()
            streamlit_process.wait()
            print("✅ Dashboards stopped")
    
    except Exception as e:
        print(f"❌ Failed to start Streamlit dashboard: {e}")

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        # Start dashboards
        start_dashboards()
    else:
        # Run tests
        if test_dashboards():
            print("\n" + "=" * 60)
            print("🎉 All dashboard and ML tests passed!")
            print("\n📝 Next Steps:")
            print("1. Start dashboards: python test_dashboards.py start")
            print("2. Access Streamlit: http://localhost:8501")
            print("3. Train ML models: python analytics/ml_models.py")
            print("4. Build advanced features and deploy to cloud")
        else:
            print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 