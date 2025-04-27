
import pymysql
from app import create_app, db
from app.utils import populate_sample_data

def init_database():
    # Create the database if it doesn't exist
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='pramod2805'
    )
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS AI_Safety_Incident_Log_Service")
        print("Database created successfully or already exists")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        conn.close()

    # Create the application context
    app = create_app()
    
    # Create all tables
    with app.app_context():
        db.create_all()
        populate_sample_data()
        print("✅  Database tables created and sample data populated.")

if __name__ == "__main__":
    init_database()

