from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Incident, User
from app.utils import validate_incident_data
from sqlalchemy.exc import IntegrityError
from flask_login import login_required, current_user
from functools import wraps
import re

# Create a Blueprint for the routes
api = Blueprint("api", __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@api.route('/', methods=['GET'])
def home():
    """
    Home route - provides basic API information.
    """
    return jsonify({
        'message': 'Welcome to AI Safety Incident Log API',
        'version': '2.0',
        'endpoints': {
            'GET /incidents': 'Get all incidents (with pagination and filtering)',
            'POST /incidents': 'Create a new incident',
            'GET /incidents/{id}': 'Get a specific incident',
            'PUT /incidents/{id}': 'Update an incident',
            'DELETE /incidents/{id}': 'Delete an incident',
            'GET /incidents/search': 'Search incidents',
            'GET /incidents/stats': 'Get incident statistics'
        }
    }), 200

@api.route('/incidents', methods=['GET'])
@login_required
def get_all_incidents():
    """
    Retrieve all incidents from the database with pagination and filtering.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    severity = request.args.get('severity')
    category = request.args.get('category')
    
    query = Incident.query
    
    # Apply filters
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if category:
        query = query.filter(Incident.category == category)
    
    # Order by most recent first
    query = query.order_by(Incident.reported_at.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    incidents = pagination.items
    
    return jsonify({
        'incidents': [incident.to_dict() for incident in incidents],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@api.route('/incidents/search', methods=['GET'])
@login_required
def search_incidents():
    """
    Search incidents by various criteria.
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    # Search in title, description, and tags
    search_results = Incident.query.filter(
        db.or_(
            Incident.title.ilike(f'%{query}%'),
            Incident.description.ilike(f'%{query}%'),
            Incident.tags.ilike(f'%{query}%')
        )
    ).all()
    
    return jsonify([incident.to_dict() for incident in search_results]), 200

@api.route('/incidents/stats', methods=['GET'])
@login_required
def get_incident_stats():
    """
    Get statistics about incidents.
    """
    total_incidents = Incident.query.count()
    by_severity = db.session.query(
        Incident.severity, db.func.count(Incident.id)
    ).group_by(Incident.severity).all()
    by_status = db.session.query(
        Incident.status, db.func.count(Incident.id)
    ).group_by(Incident.status).all()
    by_category = db.session.query(
        Incident.category, db.func.count(Incident.id)
    ).group_by(Incident.category).all()
    
    return jsonify({
        'total_incidents': total_incidents,
        'by_severity': dict(by_severity),
        'by_status': dict(by_status),
        'by_category': dict(by_category)
    }), 200

@api.route('/incidents', methods=['POST'])
@login_required
def create_incident():
    """
    Create a new incident.
    """
    try:
        data = request.get_json()
        validation_result = validate_incident_data(data)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        new_incident = Incident(
            title=data['title'],
            description=data['description'],
            severity=data['severity'],
            category=data['category'],
            tags=','.join(data.get('tags', [])),
            reported_by=current_user.id,
            impact_scope=data.get('impact_scope'),
            affected_systems=data.get('affected_systems'),
            mitigation_steps=data.get('mitigation_steps'),
            prevention_measures=data.get('prevention_measures')
        )
        
        db.session.add(new_incident)
        db.session.commit()
        
        return jsonify(new_incident.to_dict()), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database integrity error', 'details': str(e)}), 500

@api.route('/incidents/<int:incident_id>', methods=['GET'])
@login_required
def get_incident(incident_id):
    """
    Retrieve a specific incident by ID.
    """
    incident = Incident.query.get(incident_id)
    
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    
    return jsonify(incident.to_dict()), 200

@api.route('/incidents/<int:incident_id>', methods=['PUT'])
@login_required
def update_incident(incident_id):
    """
    Update an existing incident.
    """
    incident = Incident.query.get(incident_id)
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    
    # Only allow updates by the reporter or admin
    if not (current_user.id == incident.reported_by or current_user.is_admin):
        return jsonify({'error': 'Unauthorized to update this incident'}), 403
    
    data = request.get_json()
    
    # Update fields if provided
    if 'title' in data:
        incident.title = data['title']
    if 'description' in data:
        incident.description = data['description']
    if 'severity' in data:
        incident.severity = data['severity']
    if 'status' in data:
        incident.status = data['status']
    if 'category' in data:
        incident.category = data['category']
    if 'tags' in data:
        incident.tags = ','.join(data['tags'])
    if 'assigned_to' in data:
        incident.assigned_to = data['assigned_to']
    if 'resolution_notes' in data:
        incident.resolution_notes = data['resolution_notes']
    if 'impact_scope' in data:
        incident.impact_scope = data['impact_scope']
    if 'affected_systems' in data:
        incident.affected_systems = data['affected_systems']
    if 'mitigation_steps' in data:
        incident.mitigation_steps = data['mitigation_steps']
    if 'prevention_measures' in data:
        incident.prevention_measures = data['prevention_measures']
    
    db.session.commit()
    return jsonify(incident.to_dict()), 200

@api.route('/incidents/<int:incident_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_incident(incident_id):
    """
    Delete an incident by ID (admin only).
    """
    incident = Incident.query.get(incident_id)
    
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    
    db.session.delete(incident)
    db.session.commit()
    
    return jsonify({'message': 'Incident deleted successfully'}), 200
