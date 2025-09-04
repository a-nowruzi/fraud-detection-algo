"""
Prediction routes for fraud detection API
مسیرهای پیش‌بینی برای API تشخیص تقلب
"""

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.prediction_service import PredictionService
from core.validators import validate_prescription_data, sanitize_input
from core.exceptions import ValidationError, ModelNotReadyError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprint
prediction_bp = Blueprint('prediction', __name__)

# Global prediction service instance
prediction_service = None

def init_prediction_service(service: PredictionService):
    """Initialize the prediction service"""
    global prediction_service
    prediction_service = service

@prediction_bp.route('/predict', methods=['POST'])
@swag_from({
    'tags': ['Predictions'],
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
                'ID': {
                    'type': 'integer',
                    'example': 48928
                },
                'jalali_date': {
                    'type': 'string',
                    'description': 'Jalali date of birth in YYYY/MM/DD',
                    'example': "1361/05/04"
                },
                'Adm_date': {
                    'type': 'string',
                    'description': 'Jalali admission date in YYYY/MM/DD',
                    'example': "1403/08/05"
                },
                'Service': {
                    'type': 'string',
                    'example': "ویزیت متخصص"
                },
                'provider_name': {
                    'type': 'string',
                    'example': "حسینخان خسروخاور"
                },
                'provider_specialty': {
                    'type': 'string',
                    'example': "دکترای حرفه‌ای پزشکی"
                },
                'cost_amount': {
                    'type': 'number',
                    'example': 2000000
                }
            }
        }
    }],
    'responses': {
        200: {
            'description': 'Prediction result',
            'schema': {
                'type': 'object',
                'properties': {
                    'prediction': {
                        'type': 'integer',
                        'enum': [-1, 1]
                    },
                    'score': {
                        'type': 'number'
                    },
                    'is_fraud': {
                        'type': 'boolean'
                    },
                    'risk_scores': {
                        'type': 'array',
                        'items': {
                            'type': 'number'
                        }
                    },
                    'features': {
                        'type': 'object'
                    }
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
def predict():
    """Predict fraud for a new prescription"""
    try:
        # Get and sanitize input data
        prescription_data = request.get_json()
        if prescription_data is None:
            raise ValidationError("Request body must contain valid JSON")
        
        prescription_data = sanitize_input(prescription_data)
        
        # Validate input data
        validated_data = validate_prescription_data(prescription_data)
        
        # Make prediction
        if prediction_service is None:
            raise ModelNotReadyError("Prediction service not initialized")
        
        result = prediction_service.predict_new_prescription(validated_data)
        
        logger.info(f"Prediction completed for ID: {validated_data['ID']}")
        return jsonify(result)
    
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({
            'error': e.message,
            'field': getattr(e, 'field', None),
            'details': e.details
        }), 400
    
    except ModelNotReadyError as e:
        logger.error(f"Model not ready: {str(e)}")
        return jsonify({
            'error': e.message,
            'status': 'model_not_ready'
        }), 503
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            'error': 'Internal server error during prediction',
            'details': str(e)
        }), 500

@prediction_bp.route('/stats', methods=['GET'])
@swag_from({
    'tags': ['System'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'Overall statistics',
            'schema': {
                'type': 'object',
                'properties': {
                    'total_prescriptions': {
                        'type': 'integer'
                    },
                    'fraud_prescriptions': {
                        'type': 'integer'
                    },
                    'normal_prescriptions': {
                        'type': 'integer'
                    },
                    'fraud_percentage': {
                        'type': 'number'
                    },
                    'model_contamination': {
                        'type': 'number'
                    },
                    'features_count': {
                        'type': 'integer'
                    }
                }
            }
        },
        503: {
            'description': 'Model not ready'
        }
    }
})
def get_stats():
    """Get system statistics"""
    try:
        if prediction_service is None:
            return jsonify({'error': 'Prediction service not initialized'}), 503
        
        stats = prediction_service.get_statistics()
        
        if 'error' in stats:
            return jsonify(stats), 503
        
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({
            'error': 'Internal server error while getting statistics',
            'details': str(e)
        }), 500

@prediction_bp.route('/model-info', methods=['GET'])
@swag_from({
    'tags': ['System'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'Model information',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'enum': ['ready', 'not_ready']
                    },
                    'model_type': {
                        'type': 'string'
                    },
                    'n_estimators': {
                        'type': 'integer'
                    },
                    'max_samples': {
                        'type': 'integer'
                    },
                    'max_features': {
                        'type': 'integer'
                    },
                    'contamination': {
                        'type': 'number'
                    },
                    'training_samples': {
                        'type': 'integer'
                    },
                    'feature_count': {
                        'type': 'integer'
                    }
                }
            }
        }
    }
})
def get_model_info():
    """Get model information"""
    try:
        if prediction_service is None:
            return jsonify({'status': 'not_ready', 'error': 'Prediction service not initialized'})
        
        model_info = prediction_service.get_model_info()
        return jsonify(model_info)
    
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return jsonify({
            'error': 'Internal server error while getting model info',
            'details': str(e)
        }), 500

@prediction_bp.route('/retrain', methods=['POST'])
@swag_from({
    'tags': ['System'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'Model retraining initiated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string'
                    },
                    'message': {
                        'type': 'string'
                    },
                    'timestamp': {
                        'type': 'string'
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def retrain_model():
    """Force model retraining"""
    try:
        if prediction_service is None:
            return jsonify({'error': 'Prediction service not initialized'}), 503
        
        # Force retrain
        prediction_service.force_retrain()
        
        return jsonify({
            'status': 'success',
            'message': 'Model retraining initiated. The model will be retrained on the next request.',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error initiating model retrain: {str(e)}")
        return jsonify({
            'error': 'Internal server error while initiating retrain',
            'details': str(e)
        }), 500
