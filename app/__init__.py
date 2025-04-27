from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the database object globally
db = SQLAlchemy()

def create_app():
    # Initialize Flask application
    app = Flask(__name__)

    # Configure database for MySQL Workbench
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        "mysql+pymysql://root:pramod2805@localhost:3306/AI_Safety_Incident_Log_Service"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Register the blueprint
    from app.routes import api
    app.register_blueprint(api)

    return app
