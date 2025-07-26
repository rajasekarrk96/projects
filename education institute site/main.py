#!/usr/bin/env python3
"""
Edusphere Institute Management System
Main Application Entry Point

Quick Start Commands:
    python main.py                    # Start the application
    python init_db.py                 # Initialize database with sample data
    pip install -r requirements.txt   # Install dependencies
    
Demo Login Accounts (after running init_db.py):
    Admin:   admin@edusphere.com / admin123
    Staff:   staff@edusphere.com / staff123
    Faculty: faculty@edusphere.com / faculty123
    Student: student@edusphere.com / student123
    
Access URLs:
    http://localhost:5000/            # Home page
    http://localhost:5000/login       # Login page
    http://localhost:5000/enquiry     # Enquiry form
    http://localhost:5000/dashboard   # Role-based dashboard
"""

from flask import Flask
from flask_login import LoginManager
from core.config import Config
from core.auth import load_user
from core.database import db_manager

# Import all modules
from public.routes import public_bp
from admin.routes import admin_bp
from staff.routes import staff_bp
from faculty.routes import faculty_bp
from student.routes import student_bp

# Initialize extensions
login_manager = LoginManager()

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'public.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register user loader function
    login_manager.user_loader(load_user)
    
    # Initialize database schema
    try:
        db_manager.create_database_schema()
        print("[OK] Database schema initialized successfully!")
    except Exception as e:
        print(f"[ERROR] Database initialization error: {e}")
    
    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(faculty_bp, url_prefix='/faculty')
    app.register_blueprint(student_bp, url_prefix='/student')
    
    return app

def main():
    """Main function to run the application"""
    app = create_app()
    
    print("Edusphere Institute Management System")
    print("=" * 50)
    print("Server starting...")
    print("Access the application at: http://localhost:5000")
    print("Demo accounts available after running: python init_db.py")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main() 