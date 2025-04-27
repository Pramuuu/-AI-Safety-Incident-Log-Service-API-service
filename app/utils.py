from app import db
from app.models import Incident
from datetime import datetime

def validate_incident_data(data):
    """
    Validate incident data before creating or updating an incident.
    """
    required_fields = ['title', 'description', 'severity', 'category']
    valid_severities = ['low', 'medium', 'high', 'critical']
    valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            return {
                'valid': False,
                'message': f'Missing required field: {field}'
            }
    
    # Validate title length
    if len(data['title']) > 200:
        return {
            'valid': False,
            'message': 'Title must be 200 characters or less'
        }
    
    # Validate severity
    if data['severity'] not in valid_severities:
        return {
            'valid': False,
            'message': f'Severity must be one of: {", ".join(valid_severities)}'
        }
    
    # Validate status if provided
    if 'status' in data and data['status'] not in valid_statuses:
        return {
            'valid': False,
            'message': f'Status must be one of: {", ".join(valid_statuses)}'
        }
    
    # Validate category length
    if len(data['category']) > 50:
        return {
            'valid': False,
            'message': 'Category must be 50 characters or less'
        }
    
    # Validate tags if provided
    if 'tags' in data:
        if not isinstance(data['tags'], list):
            return {
                'valid': False,
                'message': 'Tags must be provided as a list'
            }
        for tag in data['tags']:
            if len(tag) > 50:
                return {
                    'valid': False,
                    'message': 'Each tag must be 50 characters or less'
                }
    
    # Validate impact scope if provided
    if 'impact_scope' in data and len(data['impact_scope']) > 200:
        return {
            'valid': False,
            'message': 'Impact scope must be 200 characters or less'
        }
    
    # Validate affected systems if provided
    if 'affected_systems' in data and len(data['affected_systems']) > 200:
        return {
            'valid': False,
            'message': 'Affected systems must be 200 characters or less'
        }
    
    return {
        'valid': True,
        'message': 'Data is valid'
    }

def format_error_response(error_message, status_code=400):
    """
    Format an error response in a consistent way.
    """
    return {
        'error': error_message,
        'status': 'error',
        'status_code': status_code
    }

def format_success_response(data, message=None, status_code=200):
    """
    Format a success response in a consistent way.
    """
    response = {
        'data': data,
        'status': 'success',
        'status_code': status_code
    }
    if message:
        response['message'] = message
    return response

def populate_sample_data():
    """
    Populate the database with sample incidents.
    """
    # Check if database already has data
    if Incident.query.count() > 0:
        print("Database already has data. Skipping sample data population.")
        return
    
    # Sample incidents
    sample_incidents = [
        {
            'title': 'Chatbot Producing Harmful Content',
            'description': 'AI chatbot started generating unsafe content after a prompt injection attack.',
            'severity': 'High',
            'reported_at': datetime(2025, 4, 1, 14, 30, 0)
        },
        {
            'title': 'Bias in Job Recommendation Algorithm',
            'description': 'AI system showing gender bias in software engineering job recommendations.',
            'severity': 'Medium',
            'reported_at': datetime(2025, 4, 2, 9, 15, 0)
        },
        {
            'title': 'Data Privacy Breach',
            'description': 'AI system accidentally included private user data in its training dataset.',
            'severity': 'High',
            'reported_at': datetime(2025, 4, 3, 11, 45, 0)
        }
    ]
    
    # Add sample incidents to database
    try:
        for incident_data in sample_incidents:
            incident = Incident(
                title=incident_data['title'],
                description=incident_data['description'],
                severity=incident_data['severity'],
                reported_at=incident_data['reported_at']
            )
            db.session.add(incident)
        
        # Commit changes
        db.session.commit()
        print("Sample data populated successfully.")
    except Exception as e:
        db.session.rollback()  # Rollback in case of errors
        print(f"Error populating sample data: {e}")
