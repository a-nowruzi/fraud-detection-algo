"""
Services and specialties routes for fraud detection API
مسیرهای خدمات و تخصص‌ها برای API تشخیص تقلب
"""

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from config.config import get_db_manager
from core.exceptions import ValidationError
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

# Create blueprint
services_bp = Blueprint('services', __name__, url_prefix='/services')

@services_bp.route('/list', methods=['GET'])
@swag_from({
    'tags': ['Services'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'List of available services',
            'schema': {
                'type': 'object',
                'properties': {
                    'services': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        }
                    },
                    'count': {
                        'type': 'integer'
                    }
                }
            }
        },
        500: {
            'description': 'Server error'
        }
    }
})
def get_services():
    """Get list of available services"""
    try:
        db_manager = get_db_manager()
        
        # Query to get distinct services from Prescriptions table
        query = """
        SELECT DISTINCT Service 
        FROM Prescriptions 
        WHERE Service IS NOT NULL AND Service != ''
        ORDER BY Service
        """
        
        with db_manager.get_connection() as conn:
            result = conn.execute(text(query))
            services = [row[0] for row in result.fetchall()]
        
        logger.info(f"Retrieved {len(services)} services")
        return jsonify({
            'services': services,
            'count': len(services)
        })
    
    except Exception as e:
        logger.error(f"Error getting services: {str(e)}")
        return jsonify({
            'error': 'Internal server error while getting services',
            'details': str(e)
        }), 500

@services_bp.route('/specialties', methods=['GET'])
@swag_from({
    'tags': ['Services'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'List of available specialties',
            'schema': {
                'type': 'object',
                'properties': {
                    'specialties': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        }
                    },
                    'count': {
                        'type': 'integer'
                    }
                }
            }
        },
        500: {
            'description': 'Server error'
        }
    }
})
def get_specialties():
    """Get list of available specialties"""
    try:
        db_manager = get_db_manager()
        
        # Query to get distinct specialties from Prescriptions table
        query = """
        SELECT DISTINCT provider_specialty 
        FROM Prescriptions 
        WHERE provider_specialty IS NOT NULL AND provider_specialty != ''
        ORDER BY provider_specialty
        """
        
        with db_manager.get_connection() as conn:
            result = conn.execute(text(query))
            specialties = [row[0] for row in result.fetchall()]
        
        logger.info(f"Retrieved {len(specialties)} specialties")
        return jsonify({
            'specialties': specialties,
            'count': len(specialties)
        })
    
    except Exception as e:
        logger.error(f"Error getting specialties: {str(e)}")
        return jsonify({
            'error': 'Internal server error while getting specialties',
            'details': str(e)
        }), 500

@services_bp.route('/providers', methods=['GET'])
@swag_from({
    'tags': ['Services'],
    'produces': ['application/json'],
    'parameters': [
        {
            'in': 'query',
            'name': 'specialty',
            'type': 'string',
            'required': False,
            'description': 'Filter providers by specialty'
        },
        {
            'in': 'query',
            'name': 'service',
            'type': 'string',
            'required': False,
            'description': 'Filter providers by service'
        }
    ],
    'responses': {
        200: {
            'description': 'List of providers with optional filtering',
            'schema': {
                'type': 'object',
                'properties': {
                    'providers': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'provider_name': {'type': 'string'},
                                'provider_specialty': {'type': 'string'},
                                'services_count': {'type': 'integer'},
                                'total_prescriptions': {'type': 'integer'}
                            }
                        }
                    },
                    'count': {
                        'type': 'integer'
                    }
                }
            }
        },
        500: {
            'description': 'Server error'
        }
    }
})
def get_providers():
    """Get list of providers with optional filtering by specialty or service"""
    try:
        db_manager = get_db_manager()
        
        # Build query with optional filters
        base_query = """
        SELECT 
            provider_name,
            provider_specialty,
            COUNT(DISTINCT Service) as services_count,
            COUNT(*) as total_prescriptions
        FROM Prescriptions 
        WHERE provider_name IS NOT NULL AND provider_name != ''
        """
        
        params = []
        conditions = []
        
        # Add specialty filter if provided
        specialty = request.args.get('specialty')
        if specialty:
            conditions.append("provider_specialty = %s")
            params.append(specialty)
        
        # Add service filter if provided
        service = request.args.get('service')
        if service:
            conditions.append("Service = %s")
            params.append(service)
        
        # Add conditions to query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += """
        GROUP BY provider_name, provider_specialty
        ORDER BY total_prescriptions DESC, provider_name
        """
        
        with db_manager.get_connection() as conn:
            result = conn.execute(text(base_query), params)
            providers = []
            for row in result.fetchall():
                providers.append({
                    'provider_name': row[0],
                    'provider_specialty': row[1],
                    'services_count': row[2],
                    'total_prescriptions': row[3]
                })
        
        logger.info(f"Retrieved {len(providers)} providers")
        return jsonify({
            'providers': providers,
            'count': len(providers)
        })
    
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        return jsonify({
            'error': 'Internal server error while getting providers',
            'details': str(e)
        }), 500

@services_bp.route('/stats', methods=['GET'])
@swag_from({
    'tags': ['Services'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'Statistics about services and specialties',
            'schema': {
                'type': 'object',
                'properties': {
                    'total_services': {'type': 'integer'},
                    'total_specialties': {'type': 'integer'},
                    'total_providers': {'type': 'integer'},
                    'total_prescriptions': {'type': 'integer'},
                    'top_services': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'service': {'type': 'string'},
                                'count': {'type': 'integer'}
                            }
                        }
                    },
                    'top_specialties': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'specialty': {'type': 'string'},
                                'count': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        },
        500: {
            'description': 'Server error'
        }
    }
})
def get_services_stats():
    """Get statistics about services and specialties"""
    try:
        db_manager = get_db_manager()
        
        # Get basic counts
        count_queries = {
            'total_services': "SELECT COUNT(DISTINCT Service) FROM Prescriptions WHERE Service IS NOT NULL AND Service != ''",
            'total_specialties': "SELECT COUNT(DISTINCT provider_specialty) FROM Prescriptions WHERE provider_specialty IS NOT NULL AND provider_specialty != ''",
            'total_providers': "SELECT COUNT(DISTINCT provider_name) FROM Prescriptions WHERE provider_name IS NOT NULL AND provider_name != ''",
            'total_prescriptions': "SELECT COUNT(*) FROM Prescriptions"
        }
        
        stats = {}
        with db_manager.get_connection() as conn:
            for key, query in count_queries.items():
                result = conn.execute(text(query))
                stats[key] = result.fetchone()[0]
            
            # Get top services
            top_services_query = """
            SELECT Service, COUNT(*) as count
            FROM Prescriptions 
            WHERE Service IS NOT NULL AND Service != ''
            GROUP BY Service
            ORDER BY count DESC
            LIMIT 10
            """
            result = conn.execute(text(top_services_query))
            stats['top_services'] = [{'service': row[0], 'count': row[1]} for row in result.fetchall()]
            
            # Get top specialties
            top_specialties_query = """
            SELECT provider_specialty, COUNT(*) as count
            FROM Prescriptions 
            WHERE provider_specialty IS NOT NULL AND provider_specialty != ''
            GROUP BY provider_specialty
            ORDER BY count DESC
            LIMIT 10
            """
            result = conn.execute(text(top_specialties_query))
            stats['top_specialties'] = [{'specialty': row[0], 'count': row[1]} for row in result.fetchall()]
        
        logger.info("Retrieved services and specialties statistics")
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error getting services stats: {str(e)}")
        return jsonify({
            'error': 'Internal server error while getting services statistics',
            'details': str(e)
        }), 500
