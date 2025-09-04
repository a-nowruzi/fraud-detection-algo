"""
Configuration Package for Fraud Detection API

This package contains all configuration files and settings.
"""

from .config import api_config, app_config, db_config, memory_config, model_config

__all__ = [
    'api_config',
    'app_config', 
    'db_config',
    'memory_config',
    'model_config'
]

__version__ = '1.0.0'
__author__ = 'Fraud Detection Team'
__description__ = 'Configuration management for medical fraud detection API'
