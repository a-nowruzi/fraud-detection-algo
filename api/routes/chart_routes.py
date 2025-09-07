"""
Chart routes for fraud detection API
مسیرهای نمودار برای API تشخیص تقلب
"""

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.chart_service import ChartService
from services.prediction_service import PredictionService
from core.validators import validate_chart_parameters, validate_prescription_data, sanitize_input
from core.exceptions import ValidationError, ChartGenerationError, ModelNotReadyError
from config.config import app_config
import logging

logger = logging.getLogger(__name__)

# Create blueprint
chart_bp = Blueprint('charts', __name__, url_prefix='/charts')

# Global service instances
chart_service = None
prediction_service = None

def init_chart_services(chart_svc: ChartService, pred_svc: PredictionService):
    """Initialize the chart services"""
    global chart_service, prediction_service
    chart_service = chart_svc
    prediction_service = pred_svc

@chart_bp.route('/fraud-by-province', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {
                        'type': 'string',
                        'description': 'Base64 PNG image string'
                    }
                }
            }
        },
        500: {
            'description': 'Server error'
        }
    }
})
def fraud_by_province_chart():
    """Generate fraud by province chart"""
    try:
        if chart_service is None:
            return jsonify({
                'error': 'Chart service not initialized',
                'message': 'The application is still starting up or encountered an error during initialization. Please try again in a few moments.',
                'status': 'service_unavailable'
            }), 503
        
        chart_data = chart_service.create_chart('fraud_by_province')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating fraud by province chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/fraud-by-gender', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {
                        'type': 'string',
                        'description': 'Base64 PNG image string'
                    }
                }
            }
        },
        500: {
            'description': 'Server error'
        }
    }
})
def fraud_by_gender_chart():
    """Generate fraud by gender chart"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        chart_data = chart_service.create_chart('fraud_by_gender')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating fraud by gender chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/fraud-by-age', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {
                        'type': 'string',
                        'description': 'Base64 PNG image string'
                    }
                }
            }
        },
        500: {
            'description': 'Server error'
        }
    }
})
def fraud_by_age_chart():
    """Generate fraud by age group chart"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        chart_data = chart_service.create_chart('fraud_by_age_group')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating fraud by age chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/risk-indicators', methods=['POST'])
@swag_from({
    'tags': ['Charts'],
    'consumes': ['application/json'],
    'produces': ['application/json'],
    'parameters': [{
        'in': 'body',
        'name': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['ID', 'jalali_date', 'Adm_date', 'Service', 'provider_name', 'provider_specialty', 'cost_amount'],
            'properties': {
                'ID': {'type': 'integer'},
                'jalali_date': {'type': 'string'},
                'Adm_date': {'type': 'string'},
                'Service': {'type': 'string'},
                'provider_name': {'type': 'string'},
                'provider_specialty': {'type': 'string'},
                'cost_amount': {'type': 'number'}
            }
        }
    }],
    'responses': {
        200: {
            'description': 'Chart and prediction',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'},
                    'prediction': {'type': 'object'}
                }
            }
        },
        400: {
            'description': 'Validation error'
        },
        503: {
            'description': 'Model not ready'
        },
        500: {
            'description': 'Server error'
        }
    }
})
def risk_indicators_chart():
    """Generate risk indicators chart for a prescription"""
    try:
        if chart_service is None or prediction_service is None:
            return jsonify({'error': 'Services not initialized'}), 500
        
        # Get and validate prescription data
        prescription_data = request.get_json()
        if prescription_data is None:
            raise ValidationError("Request body must contain valid JSON")
        
        prescription_data = sanitize_input(prescription_data)
        validated_data = validate_prescription_data(prescription_data)
        
        # Make prediction to get risk scores
        result = prediction_service.predict_new_prescription(validated_data)
        
        # Create chart with risk values
        chart_data = chart_service.create_chart('risk_indicators', risk_values=result['risk_scores'])
        
        return jsonify({'chart': chart_data, 'prediction': result})
    
    except ValidationError as e:
        logger.warning(f"Validation error in risk indicators chart: {str(e)}")
        return jsonify({
            'error': e.message,
            'field': getattr(e, 'field', None),
            'details': e.details
        }), 400
    
    except ModelNotReadyError as e:
        logger.error(f"Model not ready for risk indicators chart: {str(e)}")
        return jsonify({
            'error': e.message,
            'status': 'model_not_ready'
        }), 503
    
    except Exception as e:
        logger.error(f"Error creating risk indicators chart: {str(e)}")
        return jsonify({
            'error': 'Failed to generate risk indicators chart',
            'message': 'An error occurred while generating the chart. Please try again.',
            'details': str(e) if app_config.debug else 'Internal server error'
        }), 500

@chart_bp.route('/fraud-ratio-by-age-group', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'}
                }
            }
        }
    }
})
def fraud_ratio_by_age_group_chart():
    """Fraud ratio by age group"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        chart_data = chart_service.create_chart('fraud_ratio_by_age_group')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating fraud ratio by age group chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/province-fraud-ratio', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'}
                }
            }
        }
    }
})
def province_fraud_ratio_chart():
    """Fraud ratio per province"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        chart_data = chart_service.create_chart('province_fraud_ratio')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating province fraud ratio chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/province-gender-fraud-percentage', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'}
                }
            }
        }
    }
})
def province_gender_fraud_percentage_chart():
    """Fraud percentage by province and gender"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        chart_data = chart_service.create_chart('province_gender_fraud_percentage')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating province gender fraud percentage chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/fraud-counts-by-date', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'}
                }
            }
        }
    }
})
def fraud_counts_by_date_chart():
    """Fraud counts over time (by admission date)"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        chart_data = chart_service.create_chart('fraud_counts_by_date')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating fraud counts by date chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/fraud-ratio-by-date', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'}
                }
            }
        }
    }
})
def fraud_ratio_by_date_chart():
    """Fraud ratio over time (by admission date)"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        chart_data = chart_service.create_chart('fraud_ratio_by_date')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating fraud ratio by date chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/fraud-ratio-by-ins-cover', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'}
                }
            }
        }
    }
})
def fraud_ratio_by_ins_cover_chart():
    """Fraud ratio by insurance cover"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        chart_data = chart_service.create_chart('fraud_ratio_by_ins_cover')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating fraud ratio by ins cover chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/fraud-ratio-by-invoice-type', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'}
                }
            }
        }
    }
})
def fraud_ratio_by_invoice_type_chart():
    """Fraud ratio by invoice type"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        chart_data = chart_service.create_chart('fraud_ratio_by_invoice_type')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating fraud ratio by invoice type chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/fraud-ratio-by-medical-record-type', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'}
                }
            }
        }
    }
})
def fraud_ratio_by_medical_record_type_chart():
    """Fraud ratio by medical record type"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        chart_data = chart_service.create_chart('fraud_ratio_by_medical_record_type')
        return jsonify({'chart': chart_data})
    
    except Exception as e:
        logger.error(f"Error creating fraud ratio by medical record type chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/provider-risk-indicator', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'parameters': [
        {
            'in': 'query',
            'name': 'provider_name',
            'type': 'string',
            'required': True
        },
        {
            'in': 'query',
            'name': 'indicator',
            'type': 'string',
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'}
                }
            }
        },
        400: {
            'description': 'Validation error'
        }
    }
})
def provider_risk_indicator_chart():
    """Provider risk indicator over time"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        # Get and validate parameters
        params = {
            'provider_name': request.args.get('provider_name'),
            'indicator': request.args.get('indicator')
        }
        
        validated_params = validate_chart_parameters(params, 'provider_risk_indicator_time_series')
        
        chart_data = chart_service.create_chart(
            'provider_risk_indicator_time_series', 
            provider_name=validated_params['provider_name'], 
            indicator=validated_params['indicator']
        )
        return jsonify({'chart': chart_data})
    
    except ValidationError as e:
        logger.warning(f"Validation error in provider risk indicator chart: {str(e)}")
        return jsonify({
            'error': e.message,
            'field': getattr(e, 'field', None),
            'details': e.details
        }), 400
    
    except Exception as e:
        logger.error(f"Error creating provider risk indicator chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_bp.route('/patient-risk-indicator', methods=['GET'])
@swag_from({
    'tags': ['Charts'],
    'parameters': [
        {
            'in': 'query',
            'name': 'patient_id',
            'type': 'integer',
            'required': True
        },
        {
            'in': 'query',
            'name': 'indicator',
            'type': 'string',
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': 'Base64-encoded PNG chart',
            'schema': {
                'type': 'object',
                'properties': {
                    'chart': {'type': 'string'}
                }
            }
        },
        400: {
            'description': 'Validation error'
        }
    }
})
def patient_risk_indicator_chart():
    """Patient risk indicator over time"""
    try:
        if chart_service is None:
            return jsonify({'error': 'Chart service not initialized'}), 500
        
        # Get and validate parameters
        params = {
            'patient_id': request.args.get('patient_id'),
            'indicator': request.args.get('indicator')
        }
        
        validated_params = validate_chart_parameters(params, 'patient_risk_indicator_time_series')
        
        chart_data = chart_service.create_chart(
            'patient_risk_indicator_time_series', 
            patient_id=validated_params['patient_id'], 
            indicator=validated_params['indicator']
        )
        return jsonify({'chart': chart_data})
    
    except ValidationError as e:
        logger.warning(f"Validation error in patient risk indicator chart: {str(e)}")
        return jsonify({
            'error': e.message,
            'field': getattr(e, 'field', None),
            'details': e.details
        }), 400
    
    except Exception as e:
        logger.error(f"Error creating patient risk indicator chart: {str(e)}")
        return jsonify({'error': str(e)}), 500
