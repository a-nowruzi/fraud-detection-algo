"""
Configuration settings for the fraud detection API
تنظیمات پیکربندی برای API تشخیص تقلب
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = os.getenv('DB_HOST', '91.107.174.199')
    database: str = os.getenv('DB_NAME', 'testdb')
    user: str = os.getenv('DB_USER', 'admin')
    password: str = os.getenv('DB_PASSWORD', 'Alireza')
    port: int = int(os.getenv('DB_PORT', '3306'))
    charset: str = 'utf8mb4'
    autocommit: bool = True

@dataclass
class ModelConfig:
    """Machine learning model configuration"""
    n_estimators: int = 200
    max_samples: int = 36000
    max_features: int = 4
    contamination: float = 0.2
    random_state: int = 42
    
    # Model persistence configuration
    enable_persistence: bool = os.getenv('ENABLE_MODEL_PERSISTENCE', 'True').lower() == 'true'
    max_age_days: int = int(os.getenv('MODEL_MAX_AGE_DAYS', '30'))
    auto_save: bool = os.getenv('AUTO_SAVE_MODEL', 'True').lower() == 'true'

@dataclass
class MemoryConfig:
    """Memory optimization configuration"""
    chunk_size: int = int(os.getenv('CHUNK_SIZE', '5000'))
    max_cache_size: int = int(os.getenv('MAX_CACHE_SIZE', '5'))
    enable_streaming: bool = os.getenv('ENABLE_STREAMING', 'True').lower() == 'true'
    enable_async_init: bool = os.getenv('ENABLE_ASYNC_INIT', 'True').lower() == 'true'
    memory_cleanup_interval: int = int(os.getenv('MEMORY_CLEANUP_INTERVAL', '300'))  # seconds
    max_memory_usage_mb: int = int(os.getenv('MAX_MEMORY_USAGE_MB', '2048'))  # 2GB default

@dataclass
class AppConfig:
    """Application configuration"""
    debug: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host: str = os.getenv('FLASK_HOST', '0.0.0.0')
    port: int = int(os.getenv('FLASK_PORT', '5000'))
    secret_key: str = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Chart configuration
    chart_dpi: int = 300
    chart_figsize: tuple = (12, 6)
    
    # Feature configuration
    max_percentage_change: float = 2000.0
    age_bins: list = None
    age_labels: list = None
    
    def __post_init__(self):
        if self.age_bins is None:
            self.age_bins = [0, 4, 12, 19, 34, 49, 64, 100]
        if self.age_labels is None:
            self.age_labels = ['نوزادان', 'کودکان', 'نوجوانان', 'جوانان', 'بزرگسالان', 'میانسالان', 'سالمندان']

@dataclass
class APIConfig:
    """API configuration"""
    title: str = "Medical Fraud Detection API"
    description: str = "API for detecting fraudulent medical prescriptions"
    version: str = "1.0.0"
    base_path: str = "/"
    schemes: list = None
    
    def __post_init__(self):
        if self.schemes is None:
            self.schemes = ["http"]

# Global configuration instances
db_config = DatabaseConfig()
model_config = ModelConfig()
memory_config = MemoryConfig()
app_config = AppConfig()
api_config = APIConfig()

def get_config() -> Dict[str, Any]:
    """Get all configuration as dictionary"""
    return {
        'database': db_config,
        'model': model_config,
        'memory': memory_config,
        'app': app_config,
        'api': api_config
    }
