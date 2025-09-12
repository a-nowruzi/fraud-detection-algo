"""
Configuration settings for the fraud detection API
تنظیمات پیکربندی برای API تشخیص تقلب
"""

import os
import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Dict, Any, Optional, Iterator
import warnings
import gc
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for database operations"""
        return {
            'host': self.host,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'port': self.port,
            'charset': self.charset,
            'autocommit': self.autocommit
        }

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

class DatabaseManager:
    """Database manager for connections and operations"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or db_config
        self.engine = None
        self.connection = None
        
    def create_engine(self) -> bool:
        """Create SQLAlchemy engine for database connection"""
        try:
            config_dict = self.config.to_dict()
            connection_string = (
                f"mysql+pymysql://{config_dict['user']}:{config_dict['password']}"
                f"@{config_dict['host']}:{config_dict['port']}/{config_dict['database']}"
                f"?charset={config_dict['charset']}"
            )
            
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
                # Connection pool settings
                pool_size=5,
                max_overflow=10,
                pool_timeout=30
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database engine created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database engine: {str(e)}")
            return False
    
    def get_connection(self):
        """Get database connection"""
        if not self.engine:
            if not self.create_engine():
                raise Exception("Failed to create database engine")
        
        return self.engine.connect()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def get_table_count(self, table_name: str) -> Optional[int]:
        """
        Get the total count of records in a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Total count or None if failed
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {table_name}"
            with self.get_connection() as conn:
                result = pd.read_sql(query, conn)
                return int(result.iloc[0]['total'])
        except Exception as e:
            logger.error(f"Failed to get count for {table_name}: {str(e)}")
            return None
    
    def load_data_from_db(self, table_name: str, query: Optional[str] = None, 
                         chunk_size: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Load data from database table
        
        Args:
            table_name: Name of the table to load
            query: Custom SQL query (optional)
            chunk_size: Size of chunks to load (optional, for streaming)
            
        Returns:
            DataFrame with loaded data or None if failed
        """
        try:
            if query:
                sql_query = query
            else:
                sql_query = f"SELECT * FROM {table_name}"
            
            with self.get_connection() as conn:
                if chunk_size:
                    # Load in chunks for large datasets
                    return pd.read_sql(sql_query, conn, chunksize=chunk_size)
                else:
                    df = pd.read_sql(sql_query, conn)
            
            logger.info(f"Successfully loaded {len(df)} rows from {table_name}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load data from {table_name}: {str(e)}")
            return None
    
    def stream_data_from_db(self, table_name: str, query: Optional[str] = None, 
                           chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        """
        Stream data from database table to reduce memory usage
        
        Args:
            table_name: Name of the table to stream
            query: Custom SQL query (optional)
            chunk_size: Size of each chunk
            
        Yields:
            DataFrame chunks
        """
        try:
            if query:
                sql_query = query
            else:
                sql_query = f"SELECT * FROM {table_name}"
            
            with self.get_connection() as conn:
                for chunk in pd.read_sql(sql_query, conn, chunksize=chunk_size):
                    yield chunk
                    # Force garbage collection after each chunk
                    gc.collect()
                    
        except Exception as e:
            logger.error(f"Failed to stream data from {table_name}: {str(e)}")
            yield pd.DataFrame()  # Yield empty DataFrame on error
    
    def load_data_in_chunks(self, table_name: str, chunk_size: int = 10000) -> Optional[pd.DataFrame]:
        """
        Load data from database in chunks and combine
        
        Args:
            table_name: Name of the table to load
            chunk_size: Size of each chunk
            
        Returns:
            Combined DataFrame or None if failed
        """
        try:
            logger.info(f"Loading {table_name} in chunks of {chunk_size}")
            
            chunks = []
            chunk_count = 0
            
            for chunk in self.stream_data_from_db(table_name, chunk_size=chunk_size):
                if not chunk.empty:
                    chunks.append(chunk)
                    chunk_count += 1
                    logger.info(f"Loaded chunk {chunk_count} with {len(chunk)} records")
            
            if chunks:
                # Combine all chunks
                combined_df = pd.concat(chunks, ignore_index=True)
                del chunks  # Free memory
                gc.collect()
                
                logger.info(f"Successfully loaded {len(combined_df)} total records in {chunk_count} chunks")
                return combined_df
            else:
                logger.warning(f"No data loaded from {table_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load data in chunks from {table_name}: {str(e)}")
            return None
    
    def execute_query(self, query: str) -> bool:
        """
        Execute a custom SQL query
        
        Args:
            query: SQL query to execute
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                conn.execute(text(query))
                conn.commit()
            logger.info("Query executed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to execute query: {str(e)}")
            return False
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get table structure information
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information or None if failed
        """
        try:
            query = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = '{self.config.database}' 
            AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
            """
            
            with self.get_connection() as conn:
                result = conn.execute(text(query))
                columns = result.fetchall()
            
            table_info = {
                'table_name': table_name,
                'columns': [
                    {
                        'name': col[0],
                        'type': col[1],
                        'nullable': col[2],
                        'default': col[3],
                        'comment': col[4]
                    }
                    for col in columns
                ]
            }
            
            logger.info(f"Retrieved table info for {table_name}")
            return table_info
            
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {str(e)}")
            return None
    
    def get_table_size_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get table size information for optimization
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with size information or None if failed
        """
        try:
            query = f"""
            SELECT 
                TABLE_ROWS,
                DATA_LENGTH,
                INDEX_LENGTH,
                (DATA_LENGTH + INDEX_LENGTH) as TOTAL_SIZE
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = '{self.config.database}' 
            AND TABLE_NAME = '{table_name}'
            """
            
            with self.get_connection() as conn:
                result = pd.read_sql(query, conn)
                if not result.empty:
                    row = result.iloc[0]
                    return {
                        'table_name': table_name,
                        'estimated_rows': int(row['TABLE_ROWS']) if pd.notna(row['TABLE_ROWS']) else None,
                        'data_size_mb': round(row['DATA_LENGTH'] / 1024 / 1024, 2) if pd.notna(row['DATA_LENGTH']) else None,
                        'index_size_mb': round(row['INDEX_LENGTH'] / 1024 / 1024, 2) if pd.notna(row['INDEX_LENGTH']) else None,
                        'total_size_mb': round(row['TOTAL_SIZE'] / 1024 / 1024, 2) if pd.notna(row['TOTAL_SIZE']) else None
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get table size info for {table_name}: {str(e)}")
            return None

# Global configuration instances
db_config = DatabaseConfig()
model_config = ModelConfig()
memory_config = MemoryConfig()
app_config = AppConfig()
api_config = APIConfig()

# Global database manager instance
db_manager = DatabaseManager()

def get_config() -> Dict[str, Any]:
    """Get all configuration as dictionary"""
    return {
        'database': db_config,
        'model': model_config,
        'memory': memory_config,
        'app': app_config,
        'api': api_config
    }

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager

# Alias for backward compatibility
MemoryOptimizedDatabaseManager = DatabaseManager
