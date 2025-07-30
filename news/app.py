"""
Flask News Portal Application with Page Object Model (POM) Structure
Main application entry point using the refactored POM architecture
"""

from config import app, db
from datetime import datetime
import os
from flask import render_template, send_from_directory

# Import models to ensure they're registered with SQLAlchemy
from models import *

# Import and register POM controllers (new structure)
from controllers.auth_controller import auth_controller
from controllers.publisher_controller import publisher_controller
from controllers.admin_controller import admin_controller
from controllers.user_controller import user_controller
from controllers.superadmin_controller import superadmin_controller

# Register all blueprints with the new POM structure
app.register_blueprint(auth_controller)
app.register_blueprint(publisher_controller)
app.register_blueprint(admin_controller)
app.register_blueprint(user_controller)
app.register_blueprint(superadmin_controller)

# Set secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')

# Configure static file serving
app.static_folder = 'static'
app.static_url_path = '/static'

# Route for home page
@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

# Example of protected routes using the new decorator structure
@app.route('/admin-dashboard')
def admin_dashboard():
    """Admin dashboard route (redirects to proper POM controller)"""
    from flask import redirect, url_for
    return redirect(url_for('admin.dashboard'))

@app.route('/publisher-dashboard')
def publisher_dashboard():
    """Publisher dashboard route (redirects to proper POM controller)"""
    from flask import redirect, url_for
    return redirect(url_for('publisher.dashboard'))

@app.route('/user-dashboard')
def user_dashboard():
    """User dashboard route (redirects to proper POM controller)"""
    from flask import redirect, url_for
    return redirect(url_for('user.dashboard'))

# Create database tables
def create_db():
    """Create database tables if they don't exist"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    create_db()
    app.run(debug=True)
