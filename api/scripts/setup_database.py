"""
Database setup script for MariaDB
اسکریپت راه‌اندازی پایگاه داده برای MariaDB
"""

import pandas as pd
from config.config import get_db_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create necessary tables in the database"""
    db_manager = get_db_manager()
    
    # Test connection first
    if not db_manager.test_connection():
        logger.error("Cannot connect to database. Please check your configuration.")
        return False
    
    try:
        # Create main fraud data table
        fraud_data_table_sql = """
        CREATE TABLE IF NOT EXISTS Prescriptions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ID VARCHAR(50),
            provider_name VARCHAR(255),
            Ref_code VARCHAR(100),
            Ref_name VARCHAR(255),
            Service VARCHAR(100),
            provider_specialty VARCHAR(255),
            cost_amount DECIMAL(15,2),
            ded_amount DECIMAL(15,2),
            confirmed_amount DECIMAL(15,2),
            Adm_date VARCHAR(20),
            confirm_date VARCHAR(20),
            jalali_date VARCHAR(20),
            record_id INT,
            year_month VARCHAR(10),
            age INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_provider (provider_name),
            INDEX idx_service (Service),
            INDEX idx_date (Adm_date),
            INDEX idx_year_month (year_month)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # Create specialties table
        specialties_table_sql = """
        CREATE TABLE IF NOT EXISTS specialties (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Service VARCHAR(100) UNIQUE,
            specialty VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_service (Service)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # Execute table creation
        logger.info("Creating Prescriptions table...")
        if not db_manager.execute_query(fraud_data_table_sql):
            logger.error("Failed to create Prescriptions table")
            return False
        
        logger.info("Creating Specialties table...")
        if not db_manager.execute_query(specialties_table_sql):
            logger.error("Failed to create Specialties table")
            return False
        
        logger.info("Tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        return False

def import_csv_to_db(csv_file_path: str, table_name: str):
    """
    Import CSV data to database table
    
    Args:
        csv_file_path: Path to the CSV file
        table_name: Name of the target table
    """
    try:
        logger.info(f"Loading CSV file: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        
        db_manager = get_db_manager()
        
        # Clear existing data
        clear_sql = f"DELETE FROM {table_name}"
        db_manager.execute_query(clear_sql)
        
        # Insert data
        logger.info(f"Importing {len(df)} records to {table_name}...")
        
        with db_manager.get_connection() as conn:
            df.to_sql(table_name, conn, if_exists='append', index=False, method='multi')
        
        logger.info(f"Successfully imported {len(df)} records to {table_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error importing CSV to database: {str(e)}")
        return False

def setup_database_with_csv():
    """Complete database setup with CSV import"""
    logger.info("Starting database setup...")
    
    # Create tables
    if not create_tables():
        logger.error("Failed to create tables")
        return False
    
    # Import main dataset if CSV exists
    try:
        import_csv_to_db('DataSEt_FD7.csv', 'Prescriptions')
    except FileNotFoundError:
        logger.warning("DataSEt_FD7.csv not found. Please import data manually.")
    
    # Import specialties if CSV exists
    try:
        import_csv_to_db('specialties.csv', 'Specialties')
    except FileNotFoundError:
        logger.warning("specialties.csv not found. Please import data manually.")
    
    logger.info("Database setup completed!")
    return True

def show_table_info():
    """Show information about existing tables"""
    db_manager = get_db_manager()
    
    tables = ['Prescriptions', 'Specialties']
    
    for table in tables:
        logger.info(f"\n--- Table: {table} ---")
        info = db_manager.get_table_info(table)
        
        if info:
            logger.info(f"Columns in {table}:")
            for col in info['columns']:
                logger.info(f"  - {col['name']}: {col['type']} ({'NULL' if col['nullable'] == 'YES' else 'NOT NULL'})")
        else:
            logger.warning(f"Table {table} not found or error retrieving info")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create_tables":
            create_tables()
        elif command == "setup":
            setup_database_with_csv()
        elif command == "info":
            show_table_info()
        elif command == "import" and len(sys.argv) >= 4:
            csv_file = sys.argv[2]
            table_name = sys.argv[3]
            import_csv_to_db(csv_file, table_name)
        else:
            logger.error("Invalid command. Use: create_tables, setup, info, or import <csv_file> <table_name>")
    else:
        logger.info("Database setup script")
        logger.info("Usage:")
        logger.info("  python setup_database.py create_tables  - Create tables only")
        logger.info("  python setup_database.py setup          - Complete setup with CSV import")
        logger.info("  python setup_database.py info           - Show table information")
        logger.info("  python setup_database.py import <csv> <table> - Import specific CSV to table")
