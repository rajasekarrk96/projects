# Configuration file for Edusphere Institute Management System
# 
# Environment Setup Commands:
#     pip install python-dotenv          # Install dotenv for environment variables
#     echo SECRET_KEY=your-secret-key > .env  # Create .env file (optional)
#     echo DATABASE_URL=sqlite:///edusphere.db >> .env  # Set database URL
# 
# Database Options:
#     SQLite (default): sqlite:///edusphere.db
#     MySQL: mysql://user:password@localhost/edusphere
#     PostgreSQL: postgresql://user:password@localhost/edusphere
# 
# Testing Commands:
#     python -c "from core.config import Config; print(' Config loaded:', Config.INSTITUTE_NAME)"

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MySQL Database Configuration (Port 3307)
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = int(os.environ.get('DB_PORT') or 3307)
    DB_NAME = os.environ.get('DB_NAME') or 'edusphere_db'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    
    # Email Configuration (optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Institute Information
    INSTITUTE_NAME = 'Edusphere Training and Development Institute'
    INSTITUTE_ADDRESS = '123 Education Street, Learning City'
    INSTITUTE_PHONE = '+91-9876543210'
    INSTITUTE_EMAIL = 'info@edusphere.com'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Pagination
    ITEMS_PER_PAGE = 20