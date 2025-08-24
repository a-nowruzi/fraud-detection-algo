#!/usr/bin/env python3
"""
Startup script for the improved fraud detection API
اسکریپت راه‌اندازی برای API بهبود یافته تشخیص تقلب
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from app_improved import create_app
    import config
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    def main():
        """Main function to start the application"""
        print("🚀 Starting Fraud Detection API (Improved Version)")
        print("=" * 50)
        
        # Check environment variables
        print("📋 Checking configuration...")
        print(f"   Database Host: {config.db_config.host}")
        print(f"   Database Name: {config.db_config.database}")
        print(f"   Flask Host: {config.app_config.host}")
        print(f"   Flask Port: {config.app_config.port}")
        print(f"   Debug Mode: {config.app_config.debug}")
        
        # Create application
        print("\n🔧 Creating application...")
        try:
            fraud_app = create_app()
            print("✅ Application created successfully")
        except Exception as e:
            print(f"❌ Failed to create application: {str(e)}")
            logger.error(f"Application creation failed: {str(e)}")
            return 1
        
        # Check if services are ready
        if fraud_app.prediction_service and fraud_app.prediction_service.is_ready():
            print("✅ All services are ready")
        else:
            print("⚠️  Some services may not be fully initialized")
        
        # Start the server
        print(f"\n🌐 Starting server on {config.app_config.host}:{config.app_config.port}")
        print("📚 API Documentation: http://localhost:5000/docs/")
        print("🏠 Home Page: http://localhost:5000/")
        print("💚 Health Check: http://localhost:5000/health")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        try:
            fraud_app.run()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            return 0
        except Exception as e:
            print(f"❌ Server error: {str(e)}")
            logger.error(f"Server error: {str(e)}")
            return 1
    
    if __name__ == "__main__":
        exit_code = main()
        sys.exit(exit_code)

except ImportError as e:
    print(f"❌ Import error: {str(e)}")
    print("Please make sure all required modules are available.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    sys.exit(1)
