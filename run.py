from app import create_app, db
from app.models import User, Incident
from app.utils import populate_sample_data
import os
import sys

app = create_app()

def init_db():
    """Initialize the database with required data."""
    try:
        with app.app_context():
            db.create_all()
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully!")
            
            # Populate sample data
            populate_sample_data()
            print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting the application: {str(e)}")
        sys.exit(1)
