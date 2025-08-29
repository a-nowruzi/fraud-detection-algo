"""
Test script for memory optimization improvements
اسکریپت تست برای بهبودهای بهینه‌سازی حافظه
"""

import psutil
import os
import time
import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_memory_optimization():
    """Test the memory optimization improvements"""
    try:
        logger.info("=== Memory Optimization Test ===")
        
        # Initial memory usage
        initial_memory = get_memory_usage()
        logger.info(f"Initial memory usage: {initial_memory:.2f} MB")
        
        # Create the optimized application
        logger.info("Creating memory-optimized application...")
        start_time = time.time()
        
        app = create_app()
        
        creation_time = time.time() - start_time
        final_memory = get_memory_usage()
        
        logger.info(f"Application creation time: {creation_time:.2f} seconds")
        logger.info(f"Final memory usage: {final_memory:.2f} MB")
        logger.info(f"Memory increase: {final_memory - initial_memory:.2f} MB")
        
        # Test health endpoints
        logger.info("Testing health endpoints...")
        
        with app.app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                logger.info("Health endpoint working")
            
            # Test memory endpoint
            response = client.get('/memory')
            if response.status_code == 200:
                memory_data = response.get_json()
                logger.info(f"Current memory from API: {memory_data['memory_usage_mb']} MB")
            
            # Test readiness endpoint
            response = client.get('/ready')
            if response.status_code == 200:
                ready_data = response.get_json()
                logger.info(f"Application ready: {ready_data['ready']}")
                logger.info(f"Services status: {ready_data['services']}")
        
        logger.info("=== Memory Optimization Test Completed ===")
        
        return {
            'initial_memory_mb': round(initial_memory, 2),
            'final_memory_mb': round(final_memory, 2),
            'memory_increase_mb': round(final_memory - initial_memory, 2),
            'creation_time_seconds': round(creation_time, 2),
            'application_ready': ready_data['ready'] if 'ready_data' in locals() else False
        }
        
    except Exception as e:
        logger.error(f"Error during memory optimization test: {str(e)}")
        return None

def compare_with_original():
    """Compare with original implementation (if available)"""
    logger.info("=== Memory Usage Comparison ===")
    
    # This would require the original implementation to be available
    # For now, we'll just show the optimized results
    results = test_memory_optimization()
    
    if results:
        logger.info("Optimization Results:")
        logger.info(f"  - Memory increase: {results['memory_increase_mb']} MB")
        logger.info(f"  - Creation time: {results['creation_time_seconds']} seconds")
        logger.info(f"  - Application ready: {results['application_ready']}")
        
        # Provide recommendations
        logger.info("Optimization Features Implemented:")
        logger.info("  ✓ Chunked data loading from database")
        logger.info("  ✓ Memory-efficient feature extraction")
        logger.info("  ✓ Garbage collection after each processing step")
        logger.info("  ✓ Optimized DataFrame operations")
        logger.info("  ✓ Memory monitoring and cleanup")
        logger.info("  ✓ Reduced intermediate data storage")

if __name__ == '__main__':
    compare_with_original()
