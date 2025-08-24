"""
Improved Flask application for fraud detection API
اپلیکیشن بهبود یافته Flask برای API تشخیص تقلب
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from flasgger import Swagger
import pandas as pd
import numpy as np
import warnings
from datetime import datetime
import logging
from typing import Optional

# Import configuration and utilities
from config import api_config, app_config, db_config
from exceptions import handle_exception, FraudDetectionError
from database_config import get_db_manager
from services.prediction_service import PredictionService
from services.chart_service import ChartService
from routes.prediction_routes import prediction_bp, init_prediction_service
from routes.chart_routes import chart_bp, init_chart_services

# Import custom functions
from age_calculate_function import calculate_age
from shamsi_to_miladi_function import shamsi_to_miladi
from add_one_month_function import add_one_month
from utils import clean_numeric_column, memory_usage_optimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore')
pd.set_option('display.max_column', 50)
pd.set_option('display.max_rows', 100)

class FraudDetectionApp:
    """Main application class for fraud detection API"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.prediction_service = None
        self.chart_service = None
        self.data = None
        
        self._configure_app()
        self._register_blueprints()
        self._register_error_handlers()
    
    def _configure_app(self):
        """Configure Flask application"""
        # Basic configuration
        self.app.config['SECRET_KEY'] = app_config.secret_key
        self.app.config['DEBUG'] = app_config.debug
        
        # CORS configuration
        CORS(self.app)
        
        # Swagger configuration
        swagger_template = {
            "swagger": "2.0",
            "info": {
                "title": api_config.title,
                "description": api_config.description,
                "version": api_config.version
            },
            "basePath": api_config.base_path,
            "schemes": api_config.schemes,
            "consumes": ["application/json"],
            "produces": ["application/json"]
        }
        
        self.app.config['SWAGGER'] = {
            'title': api_config.title,
            'uiversion': 3,
        }
        
        self.swagger = Swagger(self.app, template=swagger_template, config={
            'headers': [],
            'specs': [
                {
                    'endpoint': 'apispec_1',
                    'route': '/apispec_1.json',
                    'rule_filter': lambda rule: True,
                    'model_filter': lambda tag: True,
                }
            ],
            'static_url_path': '/flasgger_static',
            'swagger_ui': True,
            'specs_route': '/docs/'
        })
    
    def _register_blueprints(self):
        """Register Flask blueprints"""
        self.app.register_blueprint(prediction_bp)
        self.app.register_blueprint(chart_bp)
    
    def _register_error_handlers(self):
        """Register error handlers"""
        self.app.register_error_handler(FraudDetectionError, handle_exception)
        self.app.register_error_handler(Exception, handle_exception)
    
    def load_and_prepare_data(self) -> bool:
        """
        Load and prepare the dataset from MariaDB
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Connecting to database...")
            db_manager = get_db_manager()
            
            # Test database connection
            if not db_manager.test_connection():
                raise Exception("Failed to connect to database")
            
            logger.info("Loading main dataset from database...")
            # Load main dataset from database table
            self.data = db_manager.load_data_from_db('Prescriptions')
            
            if self.data is None or self.data.empty:
                raise Exception("No data found in database table 'Prescriptions'")
            
            logger.info(f"Loaded {len(self.data)} records from database")
            
            # Clean numeric columns
            self.data['cost_amount'] = clean_numeric_column(self.data['cost_amount'], 'cost_amount')
            self.data['ded_amount'] = clean_numeric_column(self.data['ded_amount'], 'ded_amount')
            self.data['confirmed_amount'] = clean_numeric_column(self.data['confirmed_amount'], 'confirmed_amount')
        
            # Fill missing provider names
            self.data['provider_name'] = self.data['provider_name'].fillna(self.data['Ref_code'])
            self.data['provider_name'] = self.data['provider_name'].fillna(self.data['Ref_name'])
            
            # Load specialties from database
            logger.info("Loading specialties from database...")
            specialties = db_manager.load_data_from_db('Specialties')
            
            if specialties is not None and not specialties.empty:
                merged_data = self.data.merge(specialties, on='Service', how='left')
                self.data['provider_specialty'] = self.data['provider_specialty'].combine_first(merged_data['specialty'])
            else:
                logger.warning("No specialties data found in database, using existing provider_specialty column")
            
            # Add age column
            self.data['age'] = self.data['jalali_date'].apply(calculate_age)
            
            # Convert dates
            self.data['Adm_date'] = self.data['Adm_date'].apply(shamsi_to_miladi)
            self.data['confirm_date'] = self.data['confirm_date'].apply(shamsi_to_miladi)
            self.data['confirm_date'] = self.data['confirm_date'].fillna(self.data['Adm_date'].apply(add_one_month))
            
            # Reset confirmed amount
            self.data['confirmed_amount'] = self.data['confirmed_amount'].fillna(0)
            self.data['record_id'] = range(1, len(self.data) + 1)
            self.data['Adm_date'] = pd.to_datetime(self.data['Adm_date'])
            self.data['year_month'] = self.data['Adm_date'].dt.to_period('M')
            
            # Ensure consistent data types for key columns
            self.data['ID'] = self.data['ID'].astype(str)
            self.data['provider_name'] = self.data['provider_name'].astype(str)
            self.data['Service'] = self.data['Service'].astype(str)
            self.data['provider_specialty'] = self.data['provider_specialty'].astype(str)
            self.data['year_month'] = self.data['year_month'].astype(str)
            
            # Optimize memory usage
            self.data = memory_usage_optimizer(self.data)
            
            logger.info("Data preparation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading and preparing data: {str(e)}")
            return False
    
    def initialize_services(self) -> bool:
        """
        Initialize prediction and chart services
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.data is None:
                raise Exception("Data not loaded")
            
            logger.info("Initializing prediction service...")
            self.prediction_service = PredictionService()
            self.prediction_service.train_model(self.data)
            
            # Verify prediction service is ready
            if not self.prediction_service.is_ready():
                raise Exception("Prediction service failed to initialize properly")
            
            if self.prediction_service.data_final is None:
                raise Exception("Prediction service data_final is None")
            
            logger.info("Initializing chart service...")
            self.chart_service = ChartService(self.prediction_service.data_final)
            
            # Initialize route services
            init_prediction_service(self.prediction_service)
            init_chart_services(self.chart_service, self.prediction_service)
            
            logger.info("Services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")
            # Reset services to None on failure
            self.prediction_service = None
            self.chart_service = None
            return False
    
    def create_home_page(self) -> str:
        """Create home page HTML"""
        return """
        <!DOCTYPE html>
        <html dir="rtl" lang="fa">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>API تشخیص تقلب پزشکی</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
                h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                .endpoint { background: #ecf0f1; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #3498db; }
                .method { background: #e74c3c; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
                .url { background: #2c3e50; color: white; padding: 5px 10px; border-radius: 3px; font-family: monospace; }
                pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
                .example { background: #d5f4e6; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
                .status.ready { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
                .status.not-ready { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 API تشخیص تقلب پزشکی</h1>
                
                <div class="status """ + ("ready" if self.prediction_service and self.prediction_service.is_ready() else "not-ready") + """">
                    <strong>وضعیت سیستم:</strong> """ + ("آماده" if self.prediction_service and self.prediction_service.is_ready() else "در حال بارگذاری") + """
                </div>
                
                <div class="warning">
                    <strong>⚠️ توجه:</strong> این API برای تشخیص تقلب در نسخه‌های پزشکی طراحی شده است.
                </div>
                
                <h2>📋 نقاط پایانی (Endpoints)</h2>
                
                <div class="endpoint">
                    <span class="method">POST</span>
                    <span class="url">/predict</span>
                    <p><strong>تشخیص تقلب برای یک نسخه جدید</strong></p>
                    <p>این نقطه پایانی اطلاعات یک نسخه پزشکی را دریافت کرده و احتمال تقلب بودن آن را محاسبه می‌کند.</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/charts/fraud-by-province</span>
                    <p><strong>نمودار تقلب بر اساس استان</strong></p>
                    <p>نمودار میله‌ای از تعداد نسخه‌های تقلبی در هر استان.</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/stats</span>
                    <p><strong>آمار کلی سیستم</strong></p>
                    <p>آمار کلی از داده‌های موجود و نتایج تشخیص تقلب.</p>
                </div>
                
                <h2>🔧 نحوه استفاده</h2>
                <div class="example">
                    <h4>مثال با cURL:</h4>
                    <pre>curl -X POST http://localhost:5000/predict \\
     -H "Content-Type: application/json" \\
     -d '{
         "ID": 48928,
         "jalali_date": "1361/05/04",
         "Adm_date": "1403/08/05",
         "Service": "ویزیت متخصص",
         "provider_name": "حسینخان خسروخاور",
         "provider_specialty": "دکترای حرفه‌ای پزشکی",
         "cost_amount": 2000000
     }'</pre>
                </div>
                
                <h2>📊 ویژگی‌های سیستم</h2>
                <ul>
                    <li>تشخیص تقلب با الگوریتم Isolation Forest</li>
                    <li>محاسبه ۱۱ شاخص ریسک مختلف</li>
                    <li>نمودارهای تحلیلی متنوع</li>
                    <li>پشتیبانی از تاریخ شمسی</li>
                    <li>محاسبه سن بر اساس تاریخ تولد</li>
                    <li>تحلیل بر اساس استان، جنسیت و گروه سنی</li>
                    <li>اعتبارسنجی ورودی و مدیریت خطا</li>
                    <li>مستندات تعاملی Swagger</li>
                </ul>
                
                <h2>📚 مستندات</h2>
                <p>برای مشاهده مستندات کامل API، به <a href="/docs/">مسیر /docs</a> مراجعه کنید.</p>
            </div>
        </body>
        </html>
        """
    
    def setup_routes(self):
        """Setup additional routes"""
        
        @self.app.route('/')
        def home():
            """Home page with API documentation"""
            return self.create_home_page()
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'model_loaded': self.prediction_service is not None and self.prediction_service.is_ready(),
                'data_loaded': self.data is not None,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/ready')
        def readiness_check():
            """Readiness check endpoint"""
            is_ready = (self.prediction_service is not None and 
                       self.prediction_service.is_ready() and 
                       self.data is not None)
            
            return jsonify({
                'ready': is_ready,
                'services': {
                    'prediction_service': self.prediction_service is not None,
                    'chart_service': self.chart_service is not None,
                    'data_loaded': self.data is not None
                },
                'timestamp': datetime.now().isoformat()
            })
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """
        Run the Flask application
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Debug mode
        """
        # Use configuration values if not provided
        host = host or app_config.host
        port = port or app_config.port
        debug = debug if debug is not None else app_config.debug
        
        logger.info(f"Starting Flask server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def create_app() -> FraudDetectionApp:
    """Create and configure the Flask application"""
    app = FraudDetectionApp()
    
    # Load and prepare data
    if not app.load_and_prepare_data():
        logger.error("Failed to load and prepare data")
        logger.warning("Application will start but services may not be available")
        app.setup_routes()
        return app
    
    # Initialize services
    if not app.initialize_services():
        logger.error("Failed to initialize services")
        logger.warning("Application will start but prediction and chart services may not be available")
        app.setup_routes()
        return app
    
    # Setup routes
    app.setup_routes()
    
    logger.info("Application created successfully")
    return app

if __name__ == '__main__':
    print("Creating and configuring application...")
    fraud_app = create_app()
    
    print("Starting Flask server...")
    fraud_app.run()
