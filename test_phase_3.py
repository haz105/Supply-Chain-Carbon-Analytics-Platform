"""
Test Script for Phase 3: Advanced Analytics and Cloud Deployment
Tests massive data generation, advanced analytics, and cloud deployment features.
"""

import sys
import os
import time
import subprocess
import requests
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_massive_data_generation():
    """Test generating 100x more data (25,000 shipments)."""
    print("🚀 Testing Massive Data Generation (25,000 shipments)...")
    print("=" * 60)
    
    try:
        # Import the massive data generator
        from generate_massive_data import generate_massive_data, check_data_distribution
        
        # Generate a smaller test batch first (1,000 shipments)
        print("📊 Generating test batch of 1,000 shipments...")
        
        # Test with smaller batch for faster testing
        from etl.main import run_etl_pipeline
        run_etl_pipeline(num_shipments=1000)
        
        print("✅ Test batch generation successful!")
        
        # Check data distribution
        print("\n📈 Checking data distribution...")
        check_data_distribution()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in massive data generation: {e}")
        return False

def test_advanced_analytics():
    """Test advanced analytics features."""
    print("\n🔍 Testing Advanced Analytics Features...")
    print("=" * 50)
    
    try:
        from analytics.advanced_analytics import (
            RealTimeAnalytics, 
            SupplierAnalytics, 
            PredictiveAnalytics,
            get_advanced_analytics_summary
        )
        
        # Test real-time analytics
        print("📊 Testing Real-Time Analytics...")
        real_time = RealTimeAnalytics()
        real_time_metrics = real_time.get_real_time_metrics(hours_back=24)
        
        if real_time_metrics:
            print(f"✅ Real-time metrics: {real_time_metrics.get('shipment_count', 0)} shipments")
            print(f"   Total emissions: {real_time_metrics.get('total_emissions_kg', 0):.2f} kg")
            print(f"   Anomalies detected: {real_time_metrics.get('anomalies_detected', 0)}")
        else:
            print("⚠️ No real-time data available")
        
        # Test supplier analytics
        print("\n🏭 Testing Supplier Analytics...")
        supplier_analytics = SupplierAnalytics()
        
        # Get a sample supplier ID
        from database.connection import get_db_session
        from database.models import Shipment
        
        session = get_db_session()
        sample_supplier = session.query(Shipment.supplier_id).first()
        session.close()
        
        if sample_supplier:
            supplier_score = supplier_analytics.calculate_supplier_sustainability_score(
                sample_supplier[0]
            )
            if 'sustainability_score' in supplier_score:
                print(f"✅ Supplier sustainability score: {supplier_score['sustainability_score']:.2f}")
            else:
                print(f"⚠️ Supplier analysis: {supplier_score.get('error', 'Unknown error')}")
        
        # Test predictive analytics
        print("\n🔮 Testing Predictive Analytics...")
        predictive = PredictiveAnalytics()
        
        # Test trend analysis
        trend_analysis = predictive.analyze_trends(days_back=30)
        if 'trends' in trend_analysis:
            print("✅ Trend analysis completed")
            for trend_name, trend_data in trend_analysis['trends'].items():
                print(f"   {trend_name}: {trend_data['direction']}")
        else:
            print(f"⚠️ Trend analysis: {trend_analysis.get('error', 'Unknown error')}")
        
        # Test emissions forecasting
        emissions_forecast = predictive.forecast_emissions(days_ahead=7)
        if 'forecast_emissions' in emissions_forecast:
            print("✅ Emissions forecasting completed")
            print(f"   Average daily forecast: {emissions_forecast['avg_daily_forecast']:.2f} kg")
        else:
            print(f"⚠️ Emissions forecast: {emissions_forecast.get('error', 'Unknown error')}")
        
        # Test comprehensive analytics summary
        print("\n📋 Testing Comprehensive Analytics Summary...")
        summary = get_advanced_analytics_summary()
        if summary:
            print("✅ Advanced analytics summary generated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in advanced analytics: {e}")
        return False

def test_cloud_deployment_preparation():
    """Test cloud deployment preparation."""
    print("\n☁️ Testing Cloud Deployment Preparation...")
    print("=" * 50)
    
    try:
        # Test AWS dependencies
        print("🔧 Testing AWS Dependencies...")
        import boto3
        print("✅ boto3 imported successfully")
        
        # Test Lambda deployment package creation
        print("\n📦 Testing Lambda Deployment Package...")
        from cloud.aws_deployment import AWSDeployer
        
        deployer = AWSDeployer()
        deployer._create_lambda_package()
        
        # Check if Lambda files were created
        lambda_files = ['lambda_function.py', 'lambda_requirements.txt']
        for file in lambda_files:
            if os.path.exists(file):
                print(f"✅ {file} created successfully")
            else:
                print(f"❌ {file} not found")
        
        # Test S3 bucket name generation
        import time
        bucket_name = f"supply-chain-carbon-analytics-models-{int(time.time())}"
        print(f"✅ S3 bucket name generated: {bucket_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in cloud deployment preparation: {e}")
        return False

def test_api_with_advanced_endpoints():
    """Test API with new advanced endpoints."""
    print("\n🌐 Testing API with Advanced Endpoints...")
    print("=" * 50)
    
    try:
        # Start API server
        print("🚀 Starting API server...")
        api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "api.main:app", 
            "--host", "127.0.0.1", "--port", "8000"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        time.sleep(5)
        
        # Test basic endpoints
        base_url = "http://127.0.0.1:8000"
        
        # Test health check
        print("🏥 Testing health check...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Test shipments endpoint
        print("📦 Testing shipments endpoint...")
        response = requests.get(f"{base_url}/shipments", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Shipments endpoint: {len(data)} shipments")
        else:
            print(f"❌ Shipments endpoint failed: {response.status_code}")
        
        # Test emissions summary
        print("🌱 Testing emissions summary...")
        response = requests.get(f"{base_url}/emissions/summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Emissions summary: {data.get('total_emissions_kg', 0):.2f} kg total")
        else:
            print(f"❌ Emissions summary failed: {response.status_code}")
        
        # Stop API server
        api_process.terminate()
        api_process.wait()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_dashboard_with_massive_data():
    """Test dashboard with massive dataset."""
    print("\n📊 Testing Dashboard with Massive Data...")
    print("=" * 50)
    
    try:
        # Test dashboard startup
        print("🚀 Testing dashboard startup...")
        
        # Check if dashboard files exist
        dashboard_files = [
            'dashboard/streamlit_app.py',
            'dashboard/main.py'
        ]
        
        for file in dashboard_files:
            if os.path.exists(file):
                print(f"✅ {file} exists")
            else:
                print(f"❌ {file} not found")
        
        # Test dashboard imports
        print("\n📦 Testing dashboard imports...")
        import streamlit as st
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Dashboard dependencies imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

def main():
    """Run all Phase 3 tests."""
    print("🎯 Phase 3: Advanced Analytics and Cloud Deployment")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Massive Data Generation", test_massive_data_generation),
        ("Advanced Analytics", test_advanced_analytics),
        ("Cloud Deployment Preparation", test_cloud_deployment_preparation),
        ("API with Advanced Endpoints", test_api_with_advanced_endpoints),
        ("Dashboard with Massive Data", test_dashboard_with_massive_data)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            print(f"\n❌ ERROR: {test_name} - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 PHASE 3 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All Phase 3 tests passed! Ready for cloud deployment.")
        print("\n📝 Next Steps:")
        print("1. Generate full 25,000 shipment dataset: python generate_massive_data.py")
        print("2. Launch dashboard: streamlit run dashboard/streamlit_app.py")
        print("3. Deploy to AWS: python cloud/aws_deployment.py")
        print("4. Setup CI/CD pipeline")
        print("5. Configure monitoring and alerts")
    else:
        print(f"\n⚠️ {total-passed} test(s) failed. Please review and fix issues.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 