#!/usr/bin/env python3
"""
Quick Start Script for Fraud Detection API with MariaDB
اسکریپت راه‌اندازی سریع برای API تشخیص تقلب با MariaDB
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {str(e)}")
        return False

def check_python():
    """Check if Python is available"""
    print("🐍 Checking Python installation...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Python not found or not working")
            return False
    except Exception as e:
        print(f"❌ Python check failed: {str(e)}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    return run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing dependencies")

def setup_database():
    """Set up database tables and import data"""
    print("\n🗄️ Setting up database...")
    
    # First, try to create tables
    if not run_command(f"{sys.executable} setup_database.py create_tables", "Creating database tables"):
        return False
    
    # Check if CSV files exist and import them
    csv_files = {
        'DataSEt_FD7.csv': 'fraud_data',
        'specialties.csv': 'specialties'
    }
    
    for csv_file, table_name in csv_files.items():
        if os.path.exists(csv_file):
            if not run_command(f"{sys.executable} setup_database.py import {csv_file} {table_name}", f"Importing {csv_file}"):
                print(f"⚠️ Warning: Failed to import {csv_file}")
        else:
            print(f"⚠️ Warning: {csv_file} not found, skipping import")
    
    return True

def test_database():
    """Test database functionality"""
    return run_command(f"{sys.executable} test_database.py", "Testing database connection")

def show_status():
    """Show current status"""
    print("\n📊 Current Status:")
    
    # Check database connection
    try:
        from database_config import get_db_manager
        db_manager = get_db_manager()
        if db_manager.test_connection():
            print("✅ Database connection: OK")
        else:
            print("❌ Database connection: FAILED")
    except Exception as e:
        print(f"❌ Database connection: ERROR - {str(e)}")
    
    # Check if tables exist
    try:
        from database_config import get_db_manager
        db_manager = get_db_manager()
        tables = ['fraud_data', 'specialties']
        for table in tables:
            info = db_manager.get_table_info(table)
            if info:
                print(f"✅ Table '{table}': EXISTS")
            else:
                print(f"❌ Table '{table}': MISSING")
    except Exception as e:
        print(f"❌ Table check: ERROR - {str(e)}")

def main():
    """Main quick start function"""
    print("=" * 60)
    print("   Fraud Detection API - Quick Start")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Check Python installation")
    print("2. Install dependencies")
    print("3. Set up database tables")
    print("4. Import CSV data (if available)")
    print("5. Test database connection")
    print("6. Show current status")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("\n❌ Error: app.py not found!")
        print("Please run this script from the api/ directory")
        return 1
    
    # Step 1: Check Python
    if not check_python():
        print("\n❌ Python check failed. Please install Python 3.7+")
        return 1
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return 1
    
    # Step 3: Set up database
    if not setup_database():
        print("\n❌ Failed to set up database")
        return 1
    
    # Step 4: Test database
    if not test_database():
        print("\n❌ Database test failed")
        return 1
    
    # Step 5: Show status
    show_status()
    
    print("\n" + "=" * 60)
    print("   Quick Start Complete!")
    print("=" * 60)
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the API:")
    print("   - Windows: run_api.bat")
    print("   - Linux/Mac: ./run_api.sh")
    print("   - Manual: python app.py")
    print("\n2. Access the API:")
    print("   - Main API: http://localhost:5000")
    print("   - Documentation: http://localhost:5000/docs/")
    print("\n3. For more information:")
    print("   - Read DATABASE_SETUP.md")
    print("   - Run: python test_database.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

