"""
Database configuration for MariaDB connection
پیکربندی پایگاه داده برای اتصال MariaDB
"""

import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Optional, Dict, Any
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': '91.107.174.199',
    'database': 'testdb',
    'user': 'testuser',
    'password': 'testpass123',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True
}

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or DB_CONFIG
        self.engine = None
        self.connection = None
        
    def create_engine(self) -> bool:
        """Create SQLAlchemy engine for database connection"""
        try:
            connection_string = (
                f"mysql+pymysql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
                f"?charset={self.config['charset']}"
            )
            
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
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
    
    def load_data_from_db(self, table_name: str, query: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Load data from database table
        
        Args:
            table_name: Name of the table to load
            query: Custom SQL query (optional)
            
        Returns:
            DataFrame with loaded data or None if failed
        """
        try:
            if query:
                sql_query = query
            else:
                sql_query = f"SELECT * FROM {table_name}"
            
            with self.get_connection() as conn:
                df = pd.read_sql(sql_query, conn)
            
            logger.info(f"Successfully loaded {len(df)} rows from {table_name}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load data from {table_name}: {str(e)}")
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
            WHERE TABLE_SCHEMA = '{self.config['database']}' 
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

# Global database manager instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager
