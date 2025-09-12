"""
Database configuration for MariaDB connection
پیکربندی پایگاه داده برای اتصال MariaDB
"""

import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Optional, Dict, Any, Iterator
import warnings
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': '91.107.174.199',
    'database': 'testdb',
    'user': 'admin',
    'password': 'Alireza',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True
}

class DatabaseManager:
    """Database manager for connections and operations"""
    
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
            WHERE TABLE_SCHEMA = '{self.config['database']}' 
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

# Global database manager instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager

# Alias for backward compatibility
MemoryOptimizedDatabaseManager = DatabaseManager
