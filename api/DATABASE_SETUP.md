# Database Setup Guide - MariaDB Migration

## Overview

This guide explains how to migrate the fraud detection system from CSV files to MariaDB database.

## Database Configuration

The system is configured to connect to a MariaDB database with the following settings:

- **Server**: 91.107.174.199
- **Database**: testdb
- **Username**: testuser
- **Password**: testpass123
- **Port**: 3306

## Prerequisites

1. **MariaDB Server**: Ensure the MariaDB server is running and accessible
2. **Database Access**: Verify you can connect to the database with the provided credentials
3. **Python Dependencies**: Install the required database packages

## Installation Steps

### 1. Install Database Dependencies

The required packages are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This will install:
- `pymysql>=1.1.0` - MySQL/MariaDB connector
- `sqlalchemy>=2.0.0` - Database ORM

### 2. Database Setup

#### Option A: Automatic Setup (Recommended)

If you have the original CSV files, you can automatically create tables and import data:

```bash
# Complete setup with CSV import
python setup_database.py setup
```

#### Option B: Manual Setup

If you prefer to set up manually:

```bash
# Create tables only
python setup_database.py create_tables

# Import specific CSV files
python setup_database.py import DataSEt_FD7.csv fraud_data
python setup_database.py import specialties.csv specialties
```

#### Option C: Check Database Status

To verify your database setup:

```bash
# Show table information
python setup_database.py info
```

### 3. Database Schema

The system creates two main tables:

#### `fraud_data` Table
Contains the main fraud detection dataset with columns:
- `id` - Primary key
- `ID` - Patient ID
- `provider_name` - Healthcare provider name
- `ref_code` - Reference code
- `ref_name` - Reference name
- `Service` - Medical service code
- `provider_specialty` - Provider specialty
- `cost_amount` - Cost amount
- `ded_amount` - Deduction amount
- `confirmed_amount` - Confirmed amount
- `Adm_date` - Admission date
- `confirm_date` - Confirmation date
- `jalali_date` - Persian date
- `record_id` - Record ID
- `year_month` - Year-month period
- `age` - Patient age
- `created_at` - Record creation timestamp
- `updated_at` - Record update timestamp

#### `specialties` Table
Contains service-to-specialty mappings:
- `id` - Primary key
- `Service` - Service code (unique)
- `specialty` - Medical specialty
- `created_at` - Record creation timestamp
- `updated_at` - Record update timestamp

## Running the Application

### 1. Database Connection Test

Before running the API, test the database connection:

```bash
python -c "from database_config import get_db_manager; db = get_db_manager(); print('Success' if db.test_connection() else 'Failed')"
```

### 2. Start the API

#### Windows:
```bash
run_api.bat
```

#### Linux/Mac:
```bash
./run_api.sh
```

The startup script will automatically:
1. Check Python installation
2. Verify required files exist
3. Test database connection
4. Install dependencies
5. Start the API server

## Troubleshooting

### Database Connection Issues

1. **Connection Refused**:
   - Verify MariaDB server is running
   - Check if the server IP is correct
   - Ensure port 3306 is accessible

2. **Authentication Failed**:
   - Verify username and password
   - Check if the user has access to the database
   - Ensure the database exists

3. **Table Not Found**:
   - Run the setup script: `python setup_database.py setup`
   - Check if tables were created: `python setup_database.py info`

### Data Import Issues

1. **CSV File Not Found**:
   - Ensure CSV files are in the correct directory
   - Check file names match exactly: `DataSEt_FD7.csv` and `specialties.csv`

2. **Import Errors**:
   - Verify CSV file format matches expected schema
   - Check for encoding issues (use UTF-8)
   - Ensure sufficient database permissions

### Performance Issues

1. **Slow Data Loading**:
   - Database indexes are automatically created for better performance
   - Consider using database connection pooling for high traffic

2. **Memory Issues**:
   - The system includes memory optimization for large datasets
   - Consider chunked data loading for very large datasets

## Configuration

### Database Settings

You can modify database settings in `database_config.py`:

```python
DB_CONFIG = {
    'host': '91.107.174.199',
    'database': 'testdb',
    'user': 'testuser',
    'password': 'testpass123',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True
}
```

### Connection Pooling

The system uses SQLAlchemy connection pooling with these settings:
- `pool_pre_ping=True` - Verify connections before use
- `pool_recycle=3600` - Recycle connections every hour
- `echo=False` - Disable SQL logging

## Migration from CSV

### Before Migration

1. Backup your existing CSV files
2. Ensure database server is accessible
3. Verify you have sufficient database permissions

### Migration Process

1. **Automatic Migration** (Recommended):
   ```bash
   python setup_database.py setup
   ```

2. **Manual Migration**:
   ```bash
   # Create tables
   python setup_database.py create_tables
   
   # Import data
   python setup_database.py import DataSEt_FD7.csv fraud_data
   python setup_database.py import specialties.csv specialties
   ```

3. **Verify Migration**:
   ```bash
   python setup_database.py info
   ```

### Post-Migration

1. Test the API with the new database
2. Verify all functionality works as expected
3. Keep CSV backups for reference

## Security Considerations

1. **Database Credentials**: Store credentials securely, consider using environment variables
2. **Network Security**: Ensure database server is properly secured
3. **Access Control**: Limit database user permissions to necessary operations only
4. **Backup**: Regularly backup your database

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify database connectivity
3. Review application logs for error messages
4. Ensure all dependencies are installed correctly

## API Endpoints

The API endpoints remain the same after migration:

- `GET /` - API status
- `POST /predict` - Fraud prediction
- `GET /stats` - Statistics
- `GET /docs/` - API documentation (Swagger UI)

All endpoints now use data from the MariaDB database instead of CSV files.
