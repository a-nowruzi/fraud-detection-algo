#!/usr/bin/env python3
"""
Test script to diagnose service initialization issues
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection"""
    try:
        from database_config import get_db_manager
        db_manager = get_db_manager()
        if db_manager.test_connection():
            logger.info("✅ Database connection successful")
            return True
        else:
            logger.error("❌ Database connection failed")
            return False
    except Exception as e:
        logger.error(f"❌ Database connection error: {str(e)}")
        return False

def test_data_loading():
    """Test data loading"""
    try:
        from database_config import get_db_manager
        db_manager = get_db_manager()
        data = db_manager.load_data_from_db('Prescriptions')
        if data is not None and not data.empty:
            logger.info(f"✅ Data loaded successfully: {len(data)} records")
            return True
        else:
            logger.error("❌ No data found in database")
            return False
    except Exception as e:
        logger.error(f"❌ Data loading error: {str(e)}")
        return False

def test_prediction_service():
    """Test prediction service initialization"""
    try:
        from services.prediction_service import PredictionService
        from database_config import get_db_manager
        
        # Load data
        db_manager = get_db_manager()
        data = db_manager.load_data_from_db('Prescriptions')
        
        if data is None or data.empty:
            logger.error("❌ No data available for prediction service test")
            return False
        
        # Initialize prediction service
        prediction_service = PredictionService()
        prediction_service.train_model(data)
        
        if prediction_service.is_ready():
            logger.info("✅ Prediction service initialized successfully")
            return True
        else:
            logger.error("❌ Prediction service not ready")
            return False
            
    except Exception as e:
        logger.error(f"❌ Prediction service error: {str(e)}")
        return False

def test_chart_service():
    """Test chart service initialization"""
    try:
        from services.chart_service import ChartService
        from services.prediction_service import PredictionService
        from database_config import get_db_manager
        
        # Load data
        db_manager = get_db_manager()
        data = db_manager.load_data_from_db('Prescriptions')
        
        if data is None or data.empty:
            logger.error("❌ No data available for chart service test")
            return False
        
        # Initialize prediction service first
        prediction_service = PredictionService()
        prediction_service.train_model(data)
        
        if not prediction_service.is_ready():
            logger.error("❌ Prediction service not ready for chart service")
            return False
        
        # Initialize chart service
        chart_service = ChartService(prediction_service.data_final)
        logger.info("✅ Chart service initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Chart service error: {str(e)}")
        return False

def test_full_application():
    """Test full application initialization"""
    try:
        from app import create_app
        
        logger.info("Creating application...")
        app = create_app()
        
        if app.prediction_service is not None and app.prediction_service.is_ready():
            logger.info("✅ Prediction service ready")
        else:
            logger.error("❌ Prediction service not ready")
        
        if app.chart_service is not None:
            logger.info("✅ Chart service ready")
        else:
            logger.error("❌ Chart service not ready")
        
        if app.data is not None:
            logger.info("✅ Data loaded")
        else:
            logger.error("❌ Data not loaded")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Application initialization error: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("Service Initialization Test")
    logger.info("=" * 50)
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Data Loading", test_data_loading),
        ("Prediction Service", test_prediction_service),
        ("Chart Service", test_chart_service),
        ("Full Application", test_full_application)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"Testing: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info("")
        except Exception as e:
            logger.error(f"Test failed with exception: {str(e)}")
            results.append((test_name, False))
            logger.info("")
    
    # Summary
    logger.info("=" * 50)
    logger.info("Test Summary")
    logger.info("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    logger.info("")
    logger.info(f"Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
