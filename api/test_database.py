"""
Database connection test script
اسکریپت تست اتصال پایگاه داده
"""

import sys
import traceback
from database_config import get_db_manager

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        db_manager = get_db_manager()
        
        if db_manager.test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        traceback.print_exc()
        return False

def test_table_access():
    """Test access to required tables"""
    print("\n📋 Testing table access...")
    
    try:
        db_manager = get_db_manager()
        tables = ['fraud_data', 'specialties']
        
        for table in tables:
            info = db_manager.get_table_info(table)
            if info:
                print(f"✅ Table '{table}' exists with {len(info['columns'])} columns")
            else:
                print(f"❌ Table '{table}' not found or inaccessible")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Table access error: {str(e)}")
        traceback.print_exc()
        return False

def test_data_loading():
    """Test loading data from tables"""
    print("\n📊 Testing data loading...")
    
    try:
        db_manager = get_db_manager()
        
        # Test fraud_data table
        fraud_data = db_manager.load_data_from_db('fraud_data')
        if fraud_data is not None and not fraud_data.empty:
            print(f"✅ Loaded {len(fraud_data)} records from fraud_data table")
            print(f"   Columns: {list(fraud_data.columns)}")
        else:
            print("❌ No data found in fraud_data table")
            return False
        
        # Test specialties table
        specialties = db_manager.load_data_from_db('specialties')
        if specialties is not None and not specialties.empty:
            print(f"✅ Loaded {len(specialties)} records from specialties table")
            print(f"   Columns: {list(specialties.columns)}")
        else:
            print("⚠️ No data found in specialties table (this is optional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading error: {str(e)}")
        traceback.print_exc()
        return False

def test_app_loading():
    """Test if the app can load data successfully"""
    print("\n🚀 Testing application data loading...")
    
    try:
        # Import and test the app's data loading function
        from app import load_and_prepare_data, app_state
        
        # Reset app state
        app_state.data = None
        app_state.clf = None
        app_state.scaler = None
        app_state.data_final = None
        
        # Try to load data
        load_and_prepare_data()
        
        if app_state.is_ready():
            print("✅ Application data loading successful!")
            print(f"   Loaded {len(app_state.data)} records")
            print(f"   Model trained: {app_state.clf is not None}")
            print(f"   Scaler ready: {app_state.scaler is not None}")
            return True
        else:
            print("❌ Application data loading incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Application loading error: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all database tests"""
    print("=" * 50)
    print("   Database Connection Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Table Access", test_table_access),
        ("Data Loading", test_data_loading),
        ("Application Loading", test_app_loading)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("   Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database is ready for use.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the database configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
