"""
Simple test script to verify the FastAPI application works correctly.
"""

import requests
import json
from datetime import date

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_emissions_summary():
    """Test the emissions summary endpoint."""
    print("\nTesting emissions summary...")
    try:
        payload = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        response = requests.post(f"{BASE_URL}/emissions/summary", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_route_optimization():
    """Test the route optimization endpoint."""
    print("\nTesting route optimization...")
    try:
        payload = {
            "origin_lat": 40.7128,
            "origin_lng": -74.0060,
            "destination_lat": 34.0522,
            "destination_lng": -118.2437,
            "weight_kg": 100.0,
            "priority": "balanced"
        }
        response = requests.post(f"{BASE_URL}/optimization/routes", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_supplier_sustainability():
    """Test the supplier sustainability endpoint."""
    print("\nTesting supplier sustainability...")
    try:
        response = requests.get(f"{BASE_URL}/suppliers/sustainability")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Supply Chain Carbon Analytics API")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_emissions_summary,
        test_route_optimization,
        test_supplier_sustainability
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("Test Results:")
    for i, result in enumerate(results):
        status = "PASS" if result else "FAIL"
        print(f"Test {i+1}: {status}")
    
    if all(results):
        print("\nAll tests passed! ✅")
    else:
        print("\nSome tests failed! ❌")

if __name__ == "__main__":
    main() 