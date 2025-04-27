from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """
    Model representing a system user.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Incident(db.Model):
    """
    Model representing an AI safety incident.
    """
    __tablename__ = 'incidents'  
    __table_args__ = {'mysql_charset': 'utf8mb4'}  

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    category = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(200))  # Comma-separated tags
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolution_notes = db.Column(db.Text)
    impact_scope = db.Column(db.String(200))
    affected_systems = db.Column(db.String(200))
    mitigation_steps = db.Column(db.Text)
    prevention_measures = db.Column(db.Text)

    def __repr__(self):
        return f"<Incident {self.id}: {self.title}>"

    def to_dict(self):
        """Convert incident to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'reported_by': self.reported_by,
            'assigned_to': self.assigned_to,
            'reported_at': self.reported_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'updated_at': self.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'resolution_notes': self.resolution_notes,
            'impact_scope': self.impact_scope,
            'affected_systems': self.affected_systems,
            'mitigation_steps': self.mitigation_steps,
            'prevention_measures': self.prevention_measures
        }
