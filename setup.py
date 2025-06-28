"""
Setup script for the Supply Chain Carbon Analytics Platform.
Helps with initial configuration and environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'alembic', 'psycopg2-binary',
        'pandas', 'numpy', 'requests', 'structlog', 'pydantic', 'pydantic-settings'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            # Handle special cases for package imports
            if package == 'psycopg2-binary':
                __import__('psycopg2')
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✅ All packages installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            return False
    
    return True

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    print("📝 Creating .env file from template...")
    try:
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Replace placeholder values with defaults
        content = content.replace('your_secret_key_here', 'dev_secret_key_change_in_production')
        content = content.replace('your_api_key_here', 'dev_api_key_change_in_production')
        content = content.replace('your_openweather_api_key', 'dev_weather_key')
        content = content.replace('your_epa_api_key', 'dev_epa_key')
        content = content.replace('your_mapbox_api_key', 'dev_mapbox_key')
        content = content.replace('your_aws_access_key', 'dev_aws_key')
        content = content.replace('your_aws_secret_key', 'dev_aws_secret')
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created successfully")
        print("⚠️  Remember to update the .env file with real API keys for production")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_docker():
    """Check if Docker is available."""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Docker not found. You can still run the platform locally without Docker.")
        return False

def setup_database():
    """Test database connection."""
    print("🔍 Testing database connection...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        print("📋 To set up the database manually:")
        print("   1. Install PostgreSQL")
        print("   2. Create database 'supply_chain_carbon'")
        print("   3. Create user 'supply_chain_user' with password 'supply_chain_password'")
        print("   4. Update DATABASE_URL in .env file")
        return False
    
    try:
        # Test database connection
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import OperationalError
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            row = result.fetchone()
            if row:
                version = row[0]
                print(f"✅ Database connection successful")
                print(f"   PostgreSQL version: {version.split(',')[0]}")
            else:
                print("❌ Could not retrieve database version")
                return False
        
        # Test if tables exist (they won't initially, but connection should work)
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
                row = result.fetchone()
                if row:
                    table_count = row[0]
                    print(f"   Tables in database: {table_count}")
                else:
                    print("   Note: Could not count tables")
        except Exception as e:
            print(f"   Note: No tables exist yet (this is normal for new database)")
        
        return True
        
    except ImportError:
        print("❌ SQLAlchemy not available. Install with: pip install sqlalchemy")
        return False
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("📋 To set up the database manually:")
        print("   1. Ensure PostgreSQL is running")
        print("   2. Create database 'supply_chain_carbon'")
        print("   3. Create user 'supply_chain_user' with password 'supply_chain_password'")
        print("   4. Grant privileges to user")
        print("   5. Update DATABASE_URL in .env file")
        return False
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Supply Chain Carbon Analytics Platform")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", create_env_file),
        ("Database Setup", setup_database),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 40)
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SETUP SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Setup completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Run comprehensive test: python test_everything.py")
        print("   2. Start the API: python -m uvicorn api.main:app --reload")
        print("   3. View API docs: http://localhost:8000/docs")
    else:
        print("\n⚠️  Some setup steps failed. Please address the issues above.")
        print("\n📝 Manual setup steps:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Set up PostgreSQL database")
        print("   3. Configure .env file with your API keys")
        print("   4. Run: python test_everything.py")

if __name__ == "__main__":
    main() 