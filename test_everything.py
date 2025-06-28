"""
Comprehensive test script for the Supply Chain Carbon Analytics Platform.
Tests all components: database, ETL, API, and data flow.
"""

import os
import sys
import subprocess
import time
import requests
from datetime import datetime, date, timedelta
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

class PlatformTester:
    """Comprehensive tester for the Supply Chain Carbon Analytics Platform."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {}
    
    def test_1_database_connection(self):
        """Test database connection and setup."""
        print("🔍 Testing database connection...")
        try:
            from database.connection import test_database_connection
            result = test_database_connection()
            self.test_results['database_connection'] = result
            print(f"✅ Database connection: {'SUCCESS' if result else 'FAILED'}")
            return result
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.test_results['database_connection'] = False
            return False
    
    def test_2_run_migrations(self):
        """Run database migrations."""
        print("🔍 Running database migrations...")
        try:
            # Check if alembic is already initialized
            if not os.path.exists("alembic.ini"):
                subprocess.run(["alembic", "init", "alembic"], check=True)
            
            # Create versions directory if it doesn't exist
            os.makedirs("alembic/versions", exist_ok=True)
            
            # Create initial migration if no versions exist
            if not os.path.exists("alembic/versions") or not os.listdir("alembic/versions"):
                subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"], check=True)
            
            # Run migrations
            subprocess.run(["alembic", "upgrade", "head"], check=True)
            
            self.test_results['migrations'] = True
            print("✅ Database migrations: SUCCESS")
            return True
        except Exception as e:
            print(f"❌ Database migrations failed: {e}")
            self.test_results['migrations'] = False
            return False
    
    def test_3_generate_sample_data(self):
        """Generate sample data using the ETL pipeline."""
        print("🔍 Generating sample data...")
        try:
            from etl.main import run_etl_pipeline
            run_etl_pipeline(num_shipments=100)  # Generate 100 shipments for testing
            
            # Verify data was created
            from database.connection import get_db_session
            from sqlalchemy import text
            
            session = get_db_session()
            try:
                # Check if shipments table has data
                result = session.execute(text("SELECT COUNT(*) FROM shipments")).scalar()
                print(f"  📊 Generated {result} shipments")
                
                # Check if carbon_emissions table has data
                result = session.execute(text("SELECT COUNT(*) FROM carbon_emissions")).scalar()
                print(f"  📊 Generated {result} carbon emissions records")
                
                if result == 0:
                    print("  ⚠️ Warning: No carbon emissions data found")
                    
            finally:
                session.close()
            
            self.test_results['sample_data'] = True
            print("✅ Sample data generation: SUCCESS")
            return True
        except Exception as e:
            print(f"❌ Sample data generation failed: {e}")
            self.test_results['sample_data'] = False
            return False
    
    def test_4_start_api_server(self):
        """Start the FastAPI server in the background."""
        print("🔍 Starting API server...")
        try:
            # Check if server is already running
            try:
                response = requests.get(f"{self.base_url}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ API server: SUCCESS (already running)")
                    self.test_results['api_server'] = True
                    return True
            except requests.exceptions.RequestException:
                pass  # Server not running, continue to start it
            
            # Start the server in the background
            import subprocess
            import sys
            
            # Use python -m uvicorn for better compatibility
            # Use localhost instead of 0.0.0.0 for better Windows compatibility
            self.api_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "api.main:app", 
                "--host", "127.0.0.1", "--port", "8000", "--reload"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for server to start with better error handling
            print("  Waiting for server to start...")
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    time.sleep(2)  # Wait 2 seconds between attempts
                    response = requests.get(f"{self.base_url}/health", timeout=5)
                    if response.status_code == 200:
                        self.test_results['api_server'] = True
                        print("✅ API server: SUCCESS")
                        return True
                except requests.exceptions.RequestException:
                    if attempt < max_attempts - 1:
                        print(f"  Attempt {attempt + 1}/{max_attempts}: Server not ready yet...")
                    continue
            
            # If we get here, server didn't start properly
            # Check if there are any error messages
            try:
                stdout, stderr = self.api_process.communicate(timeout=1)
                if stderr:
                    print(f"  Server error output: {stderr}")
            except subprocess.TimeoutExpired:
                pass
            
            raise Exception("Server failed to start within expected time")
                
        except Exception as e:
            print(f"❌ API server failed: {e}")
            self.test_results['api_server'] = False
            return False
    
    def test_5_api_endpoints(self):
        """Test all API endpoints."""
        print("🔍 Testing API endpoints...")
        endpoints_tested = 0
        endpoints_passed = 0
        
        try:
            # Test health endpoint
            endpoints_tested += 1
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                endpoints_passed += 1
                print("  ✅ Health endpoint: SUCCESS")
            else:
                print(f"  ❌ Health endpoint: FAILED (status {response.status_code})")
            
            # Test emissions summary endpoint
            endpoints_tested += 1
            payload = {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
            response = requests.post(f"{self.base_url}/emissions/summary", json=payload)
            if response.status_code == 200:
                endpoints_passed += 1
                print("  ✅ Emissions summary endpoint: SUCCESS")
            else:
                print(f"  ❌ Emissions summary endpoint: FAILED (status {response.status_code})")
                try:
                    error_detail = response.json()
                    print(f"     Error: {error_detail}")
                except:
                    print(f"     Response: {response.text[:200]}")
            
            # Test route optimization endpoint
            endpoints_tested += 1
            payload = {
                "origin_lat": 40.7128,
                "origin_lng": -74.0060,
                "destination_lat": 34.0522,
                "destination_lng": -118.2437,
                "weight_kg": 100.0,
                "priority": "balanced"
            }
            response = requests.post(f"{self.base_url}/optimization/routes", json=payload)
            if response.status_code == 200:
                endpoints_passed += 1
                print("  ✅ Route optimization endpoint: SUCCESS")
            else:
                print(f"  ❌ Route optimization endpoint: FAILED (status {response.status_code})")
            
            # Test supplier sustainability endpoint
            endpoints_tested += 1
            response = requests.get(f"{self.base_url}/suppliers/sustainability")
            if response.status_code == 200:
                endpoints_passed += 1
                print("  ✅ Supplier sustainability endpoint: SUCCESS")
            else:
                print(f"  ❌ Supplier sustainability endpoint: FAILED (status {response.status_code})")
            
            success_rate = endpoints_passed / endpoints_tested
            self.test_results['api_endpoints'] = success_rate > 0.5
            print(f"✅ API endpoints: {endpoints_passed}/{endpoints_tested} passed")
            return success_rate > 0.5
            
        except Exception as e:
            print(f"❌ API endpoints test failed: {e}")
            self.test_results['api_endpoints'] = False
            return False
    
    def test_6_data_flow(self):
        """Test the complete data flow: ETL → Database → API."""
        print("🔍 Testing complete data flow...")
        try:
            # Generate more data
            from etl.main import run_etl_pipeline
            run_etl_pipeline(num_shipments=50)
            
            # Wait a moment for data to be processed
            time.sleep(2)
            
            # Test that data appears in API
            # Use a date range that matches the generated data (past 30 days)
            end_date = date.today() - timedelta(days=1)  # Yesterday
            start_date = end_date - timedelta(days=30)   # 30 days ago
            
            payload = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            # Try multiple times with timeout
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    response = requests.post(f"{self.base_url}/emissions/summary", json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data['shipment_count'] > 0:
                            self.test_results['data_flow'] = True
                            print(f"✅ Data flow: SUCCESS ({data['shipment_count']} shipments found)")
                            return True
                        else:
                            print(f"  Attempt {attempt + 1}/{max_attempts}: No shipments found yet...")
                            if attempt < max_attempts - 1:
                                time.sleep(3)  # Wait longer between attempts
                            continue
                    else:
                        print(f"  Attempt {attempt + 1}/{max_attempts}: API error {response.status_code}")
                        if attempt < max_attempts - 1:
                            time.sleep(3)
                        continue
                        
                except requests.exceptions.RequestException as e:
                    print(f"  Attempt {attempt + 1}/{max_attempts}: Request failed - {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(3)
                    continue
            
            print("❌ Data flow: FAILED (no shipments found after multiple attempts)")
            self.test_results['data_flow'] = False
            return False
                
        except Exception as e:
            print(f"❌ Data flow test failed: {e}")
            self.test_results['data_flow'] = False
            return False
    
    def cleanup(self):
        """Clean up resources."""
        print("🧹 Cleaning up...")
        try:
            if hasattr(self, 'api_process'):
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("🚀 Starting comprehensive platform test...")
        print("=" * 60)
        
        tests = [
            ("Database Connection", self.test_1_database_connection),
            ("Database Migrations", self.test_2_run_migrations),
            ("Sample Data Generation", self.test_3_generate_sample_data),
            ("API Server", self.test_4_start_api_server),
            ("API Endpoints", self.test_5_api_endpoints),
            ("Data Flow", self.test_6_data_flow),
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results[test_name] = False
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Platform is working correctly.")
        elif passed >= total * 0.8:
            print("⚠️ Most tests passed. Platform is mostly working.")
        else:
            print("❌ Many tests failed. Platform needs attention.")
        
        return results

def main():
    """Main test runner."""
    tester = PlatformTester()
    
    try:
        results = tester.run_all_tests()
        
        # Provide next steps
        print("\n" + "=" * 60)
        print("📝 NEXT STEPS")
        print("=" * 60)
        
        if results.get("API Server", False):
            print("🌐 API is running at: http://localhost:8000")
            print("📚 API documentation at: http://localhost:8000/docs")
            print("🔍 Interactive API docs at: http://localhost:8000/redoc")
        
        if results.get("Data Flow", False):
            print("✅ Data pipeline is working! You can:")
            print("   - Generate more data: python etl/main.py")
            print("   - Test specific endpoints: python test_api.py")
            print("   - Build dashboards and frontend components")
        
        print("\n💡 To stop the API server, press Ctrl+C")
        
        # Keep the server running for manual testing
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
    
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 