import unittest
import json
from app import create_app, db
from app.models import User, Incident
from datetime import datetime

class TestAPI(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create test user
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            is_admin=True
        )
        self.test_user.set_password('testpass123')
        db.session.add(self.test_user)
        db.session.commit()
        
        # Login and get token
        response = self.client.post('/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.json['token']
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_endpoint(self):
        """Test the home endpoint."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('endpoints', data)

    def test_create_incident(self):
        """Test creating a new incident."""
        incident_data = {
            'title': 'Test Incident',
            'description': 'This is a test incident',
            'severity': 'high',
            'category': 'test',
            'tags': ['test', 'api'],
            'impact_scope': 'Test scope',
            'affected_systems': 'Test system'
        }
        
        response = self.client.post(
            '/incidents',
            json=incident_data,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['title'], incident_data['title'])
        self.assertEqual(data['severity'], incident_data['severity'])

    def test_get_incidents(self):
        """Test getting all incidents with pagination."""
        # Create some test incidents
        for i in range(15):
            incident = Incident(
                title=f'Test Incident {i}',
                description=f'Description {i}',
                severity='medium',
                category='test',
                reported_by=self.test_user.id
            )
            db.session.add(incident)
        db.session.commit()

        # Test pagination
        response = self.client.get('/incidents?page=1&per_page=10', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['incidents']), 10)
        self.assertEqual(data['total'], 15)
        self.assertEqual(data['pages'], 2)

    def test_search_incidents(self):
        """Test searching incidents."""
        # Create test incidents
        incident1 = Incident(
            title='Security Breach',
            description='Unauthorized access detected',
            severity='high',
            category='security',
            reported_by=self.test_user.id
        )
        incident2 = Incident(
            title='Performance Issue',
            description='System slowdown',
            severity='medium',
            category='performance',
            reported_by=self.test_user.id
        )
        db.session.add_all([incident1, incident2])
        db.session.commit()

        # Test search
        response = self.client.get('/incidents/search?q=security', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Security Breach')

    def test_incident_stats(self):
        """Test getting incident statistics."""
        # Create test incidents with different severities
        severities = ['low', 'medium', 'high', 'critical']
        for severity in severities:
            incident = Incident(
                title=f'Test {severity}',
                description='Test description',
                severity=severity,
                category='test',
                reported_by=self.test_user.id
            )
            db.session.add(incident)
        db.session.commit()

        response = self.client.get('/incidents/stats', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total_incidents'], 4)
        self.assertEqual(len(data['by_severity']), 4)

    def test_update_incident(self):
        """Test updating an incident."""
        # Create test incident
        incident = Incident(
            title='Original Title',
            description='Original description',
            severity='low',
            category='test',
            reported_by=self.test_user.id
        )
        db.session.add(incident)
        db.session.commit()

        # Update incident
        update_data = {
            'title': 'Updated Title',
            'severity': 'high',
            'status': 'in_progress'
        }
        
        response = self.client.put(
            f'/incidents/{incident.id}',
            json=update_data,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Updated Title')
        self.assertEqual(data['severity'], 'high')
        self.assertEqual(data['status'], 'in_progress')

if __name__ == '__main__':
    unittest.main() 