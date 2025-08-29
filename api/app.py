"""
Memory-optimized Flask application for fraud detection API
اپلیکیشن Flask بهینه‌سازی شده حافظه برای API تشخیص تقلب
"""

import os
import sys

# Set environment variables for memory optimization if not already set
os.environ.setdefault('CHUNK_SIZE', '5000')
os.environ.setdefault('MAX_CACHE_SIZE', '5')
os.environ.setdefault('ENABLE_STREAMING', 'True')
os.environ.setdefault('ENABLE_ASYNC_INIT', 'True')
os.environ.setdefault('MEMORY_CLEANUP_INTERVAL', '300')
os.environ.setdefault('MAX_MEMORY_USAGE_MB', '2048')

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from flasgger import Swagger
import pandas as pd
import numpy as np
import warnings
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import gc
import psutil
import threading
import time

# Import configuration and utilities
from config import api_config, app_config, db_config, memory_config
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('fraud_detection_optimized.log')
    ]
)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore')
pd.set_option('display.max_column', 50)
pd.set_option('display.max_rows', 100)

class LazyDataLoader:
    """Lazy data loader that streams data from database"""
    
    def __init__(self, chunk_size: int = None):
        self.chunk_size = chunk_size or memory_config.chunk_size
        self.db_manager = get_db_manager()
        self._data_cache = {}
        self._cache_lock = threading.Lock()
        
    def get_data_chunk(self, chunk_id: int) -> Optional[pd.DataFrame]:
        """Get a specific chunk of data"""
        with self._cache_lock:
            if chunk_id in self._data_cache:
                return self._data_cache[chunk_id]
            
            # Load chunk from database
            offset = chunk_id * self.chunk_size
            query = f"SELECT * FROM Prescriptions LIMIT {self.chunk_size} OFFSET {offset}"
            chunk = self.db_manager.load_data_from_db('Prescriptions', query)
            
            if chunk is not None and not chunk.empty:
                # Process chunk
                chunk = self._process_chunk(chunk)
                self._data_cache[chunk_id] = chunk
                
                # Keep only last N chunks in cache
                max_cache_size = memory_config.max_cache_size
                if len(self._data_cache) > max_cache_size:
                    oldest_chunk = min(self._data_cache.keys())
                    del self._data_cache[oldest_chunk]
                
                return chunk
            return None
    
    def _process_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """Process a single chunk of data"""
        # Clean numeric columns
        chunk['cost_amount'] = clean_numeric_column(chunk['cost_amount'], 'cost_amount')
        chunk['ded_amount'] = clean_numeric_column(chunk['ded_amount'], 'ded_amount')
        chunk['confirmed_amount'] = clean_numeric_column(chunk['confirmed_amount'], 'confirmed_amount')
        
        # Fill missing provider names
        chunk['provider_name'] = chunk['provider_name'].fillna(chunk['Ref_code'])
        chunk['provider_name'] = chunk['provider_name'].fillna(chunk['Ref_name'])
        
        # Add age column
        chunk['age'] = chunk['jalali_date'].apply(calculate_age)
        
        # Convert dates
        chunk['Adm_date'] = chunk['Adm_date'].apply(shamsi_to_miladi)
        chunk['confirm_date'] = chunk['confirm_date'].apply(shamsi_to_miladi)
        chunk['confirm_date'] = chunk['confirm_date'].fillna(chunk['Adm_date'].apply(add_one_month))
        
        # Reset confirmed amount
        chunk['confirmed_amount'] = chunk['confirmed_amount'].fillna(0)
        chunk['Adm_date'] = pd.to_datetime(chunk['Adm_date'])
        chunk['year_month'] = chunk['Adm_date'].dt.to_period('M')
        
        # Ensure consistent data types
        chunk['ID'] = chunk['ID'].astype(str)
        chunk['provider_name'] = chunk['provider_name'].astype(str)
        chunk['Service'] = chunk['Service'].astype(str)
        chunk['provider_specialty'] = chunk['provider_specialty'].astype(str)
        chunk['year_month'] = chunk['year_month'].astype(str)
        
        return chunk
    
    def get_total_chunks(self) -> int:
        """Get total number of chunks"""
        total_count = self.db_manager.get_table_count('Prescriptions')
        if total_count is None:
            return 0
        return (total_count + self.chunk_size - 1) // self.chunk_size
    
    def clear_cache(self):
        """Clear the data cache"""
        with self._cache_lock:
            self._data_cache.clear()
            gc.collect()

class MemoryOptimizedFraudDetectionApp:
    """Memory-optimized main application class for fraud detection API"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.prediction_service = None
        self.chart_service = None
        self.data_loader = LazyDataLoader()
        self._services_initialized = False
        self._initialization_lock = threading.Lock()
        self._initialization_thread = None
        
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
    
    def _log_memory_usage(self, stage: str):
        """Log current memory usage"""
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"Memory usage at {stage}: {memory_mb:.2f} MB")
    
    def _initialize_services_async(self):
        """Initialize services asynchronously to avoid blocking startup"""
        try:
            logger.info("Starting asynchronous service initialization...")
            self._log_memory_usage("before_async_init")
            
            # Initialize prediction service with streaming data
            self.prediction_service = PredictionService()
            
            # Train model with streaming data
            self._train_model_with_streaming()
            
            # Initialize chart service
            if self.prediction_service.is_ready():
                self.chart_service = ChartService(self.prediction_service.data_final)
                
                # Initialize route services
                init_prediction_service(self.prediction_service)
                init_chart_services(self.chart_service, self.prediction_service)
                
                self._services_initialized = True
                logger.info("Asynchronous service initialization completed successfully")
            else:
                logger.error("Prediction service failed to initialize properly")
            
            self._log_memory_usage("after_async_init")
            
        except Exception as e:
            logger.error(f"Error in asynchronous service initialization: {str(e)}")
            self.prediction_service = None
            self.chart_service = None
    
    def _train_model_with_streaming(self):
        """Train model using streaming data to reduce memory usage"""
        try:
            logger.info("Training model with streaming data...")
            
            # Get total chunks
            total_chunks = self.data_loader.get_total_chunks()
            logger.info(f"Total chunks to process: {total_chunks}")
            
            # Process chunks and collect features
            all_features = []
            all_metadata = []
            
            for chunk_id in range(total_chunks):
                chunk = self.data_loader.get_data_chunk(chunk_id)
                if chunk is not None and not chunk.empty:
                    # Extract features from chunk
                    features = self._extract_features_from_chunk(chunk)
                    if features is not None:
                        all_features.append(features)
                        all_metadata.append(chunk[['Adm_date', 'gender', 'age', 'Service', 'province',
                                                 'Ins_Cover', 'Invice-type', 'Type_Medical_Record',
                                                 'provider_name', 'ID']].copy())
                    
                    # Clear chunk from cache to save memory
                    self.data_loader.clear_cache()
                    
                    # Log progress
                    if (chunk_id + 1) % 10 == 0:
                        logger.info(f"Processed {chunk_id + 1}/{total_chunks} chunks")
                        self._log_memory_usage(f"chunk_{chunk_id + 1}")
            
            # Combine all features
            if all_features:
                combined_features = pd.concat(all_features, ignore_index=True)
                combined_metadata = pd.concat(all_metadata, ignore_index=True)
                
                # Train model
                self.prediction_service.train_model_streaming(combined_features, combined_metadata)
                
                # Clean up
                del all_features, all_metadata, combined_features, combined_metadata
                gc.collect()
                
                logger.info("Model training with streaming data completed")
            else:
                raise Exception("No features extracted from data")
                
        except Exception as e:
            logger.error(f"Error training model with streaming data: {str(e)}")
            raise
    
    def _extract_features_from_chunk(self, chunk: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Extract features from a single chunk"""
        try:
            from services.feature_extractor import FeatureExtractor
            
            # Create feature extractor for this chunk
            feature_extractor = FeatureExtractor(chunk)
            
            # Extract features
            chunk_with_features = feature_extractor.extract_all_features()
            
            # Return only feature columns
            feature_columns = [
                'unq_ratio_provider', 'unq_ratio_patient', 'percent_change_provider',
                'percent_change_patient', 'percent_difference', 'percent_diff_ser',
                'percent_diff_spe', 'percent_diff_spe2', 'percent_diff_ser_patient',
                'percent_diff_serv', 'Ratio'
            ]
            
            available_features = [col for col in feature_columns if col in chunk_with_features.columns]
            if available_features:
                return chunk_with_features[available_features].copy()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extracting features from chunk: {str(e)}")
            return None
    
    def start_async_initialization(self):
        """Start asynchronous service initialization"""
        if self._initialization_thread is None or not self._initialization_thread.is_alive():
            self._initialization_thread = threading.Thread(target=self._initialize_services_async)
            self._initialization_thread.daemon = True
            self._initialization_thread.start()
            logger.info("Started asynchronous service initialization")
    
    def is_ready(self) -> bool:
        """Check if the application is ready to serve requests"""
        return self._services_initialized and self.prediction_service is not None and self.prediction_service.is_ready()
    
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
                .status.loading { background: #cce5ff; border: 1px solid #b3d9ff; color: #004085; }
                .config { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 API تشخیص تقلب پزشکی (بهینه‌سازی شده)</h1>
                
                <div class="status """ + ("ready" if self.is_ready() else "loading" if self._initialization_thread and self._initialization_thread.is_alive() else "not-ready") + """">
                    <strong>وضعیت سیستم:</strong> """ + ("آماده" if self.is_ready() else "در حال بارگذاری" if self._initialization_thread and self._initialization_thread.is_alive() else "در انتظار") + """
                </div>
                
                <div class="warning">
                    <strong>⚠️ توجه:</strong> این API برای تشخیص تقلب در نسخه‌های پزشکی طراحی شده است. <strong>نسخه بهینه‌سازی شده حافظه</strong>
                </div>
                
                <div class="config">
                    <strong>⚙️ تنظیمات بهینه‌سازی:</strong>
                    <ul>
                        <li>اندازه قطعه داده: """ + str(memory_config.chunk_size) + """ رکورد</li>
                        <li>حداکثر کش: """ + str(memory_config.max_cache_size) + """ قطعه</li>
                        <li>حداکثر حافظه: """ + str(memory_config.max_memory_usage_mb) + """ مگابایت</li>
                        <li>پردازش جریانی: """ + ("فعال" if memory_config.enable_streaming else "غیرفعال") + """</li>
                        <li>راه‌اندازی غیرهمزمان: """ + ("فعال" if memory_config.enable_async_init else "غیرفعال") + """</li>
                    </ul>
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
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/memory</span>
                    <p><strong>وضعیت حافظه</strong></p>
                    <p>مشاهده مصرف حافظه فعلی سیستم.</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <span class="url">/cache/clear</span>
                    <p><strong>پاکسازی کش</strong></p>
                    <p>پاکسازی کش داده‌ها برای آزادسازی حافظه.</p>
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
                
                <h2>📊 ویژگی‌های سیستم (بهینه‌سازی شده)</h2>
                <ul>
                    <li>تشخیص تقلب با الگوریتم Isolation Forest</li>
                    <li>محاسبه ۱۱ شاخص ریسک مختلف</li>
                    <li>نمودارهای تحلیلی متنوع</li>
                    <li>پشتیبانی از تاریخ شمسی</li>
                    <li>محاسبه سن بر اساس تاریخ تولد</li>
                    <li>تحلیل بر اساس استان، جنسیت و گروه سنی</li>
                    <li>اعتبارسنجی ورودی و مدیریت خطا</li>
                    <li>مستندات تعاملی Swagger</li>
                    <li><strong>بهینه‌سازی حافظه با بارگذاری تدریجی داده‌ها</strong></li>
                    <li><strong>پردازش داده‌ها به صورت جریانی (Streaming)</strong></li>
                    <li><strong>کش هوشمند برای کاهش بارگذاری مجدد</strong></li>
                    <li><strong>مدیریت خودکار حافظه و پاکسازی</strong></li>
                    <li><strong>راه‌اندازی غیرهمزمان برای شروع سریع</strong></li>
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
                'services_initialized': self._services_initialized,
                'initialization_running': self._initialization_thread is not None and self._initialization_thread.is_alive(),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/ready')
        def readiness_check():
            """Readiness check endpoint"""
            is_ready = self.is_ready()
            
            return jsonify({
                'ready': is_ready,
                'services': {
                    'prediction_service': self.prediction_service is not None,
                    'chart_service': self.chart_service is not None,
                    'services_initialized': self._services_initialized,
                    'initialization_running': self._initialization_thread is not None and self._initialization_thread.is_alive()
                },
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/memory')
        def memory_status():
            """Memory usage status endpoint"""
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            return jsonify({
                'memory_usage_mb': round(memory_mb, 2),
                'services_initialized': self._services_initialized,
                'initialization_running': self._initialization_thread is not None and self._initialization_thread.is_alive(),
                'cache_size': len(self.data_loader._data_cache),
                'memory_config': {
                    'chunk_size': memory_config.chunk_size,
                    'max_cache_size': memory_config.max_cache_size,
                    'max_memory_usage_mb': memory_config.max_memory_usage_mb,
                    'enable_streaming': memory_config.enable_streaming,
                    'enable_async_init': memory_config.enable_async_init
                },
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/cache/clear')
        def clear_cache():
            """Clear data cache endpoint"""
            self.data_loader.clear_cache()
            return jsonify({
                'status': 'success',
                'message': 'Cache cleared successfully',
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
        
        # Start asynchronous initialization
        self.start_async_initialization()
        
        logger.info(f"Starting memory-optimized Flask server on {host}:{port}")
        logger.info("The application will start immediately and initialize services asynchronously")
        logger.info("Check /ready endpoint to monitor initialization progress")
        logger.info("Check /memory endpoint to monitor memory usage")
        
        self.app.run(host=host, port=port, debug=debug)

def create_app() -> MemoryOptimizedFraudDetectionApp:
    """Create and configure the memory-optimized Flask application"""
    app = MemoryOptimizedFraudDetectionApp()
    
    # Setup routes
    app.setup_routes()
    
    logger.info("Memory-optimized application created successfully")
    return app

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Memory-Optimized Fraud Detection API")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print()
    
    print("Creating and configuring memory-optimized application...")
    fraud_app = create_app()
    
    print("Starting Flask server with memory optimization...")
    print("The application will start immediately and initialize services asynchronously")
    print("Check /ready endpoint to monitor initialization progress")
    print("Check /memory endpoint to monitor memory usage")
    print()
    
    fraud_app.run()

application_instance = create_app()
app = application_instance.app